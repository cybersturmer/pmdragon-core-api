import json

from django.contrib.auth.models import AnonymousUser
from django.utils.translation import ugettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, mixins, status, views
from rest_framework.generics import GenericAPIView, UpdateAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView

from libs.check.health import Health
from libs.sprint.analyser import SprintAnalyser
from .permissions import IsParticipateInWorkspace, IsOwnerOrReadOnly, IsCreatorOrReadOnly, WorkspaceOwnerOrReadOnly
from .schemas import IssueListUpdateSchema
from .serializers import *
from .tasks import send_registration_email, send_invitation_email


class CheckConnection(views.APIView):
	"""
	This View is just for check if connection is correct
	Look at libs/check/health.py for detailed information.
	"""
	permission_classes = (
		AllowAny,
	)
	throttle_classes = (
		AnonRateThrottle,
	)

	def get(self, request, format=None):
		health_overall = Health.get_overall_status()

		http_code = status.HTTP_200_OK \
			if health_overall['ok'] \
			else status.HTTP_400_BAD_REQUEST

		return Response(health_overall, status=http_code)


class TokenObtainPairExtendedView(TokenObtainPairView):
	"""
	Takes a set of user credentials and returns an access and refreshes JSON web
	token pair to prove the authentication of those credentials.
	Ext: Also returns user data such as
	[email, first name, last name, expired_at for tokens]
	 to reduce logic from frontend web application.
	"""
	serializer_class = TokenObtainPairExtendedSerializer


class PersonRegistrationRequestView(viewsets.GenericViewSet,
									mixins.RetrieveModelMixin,
									mixins.CreateModelMixin):
	"""
	Create a user registration request by using email and URL prefix.
	It also can be used to get registration request by given key
	"""
	queryset = PersonRegistrationRequest.valid.all()
	serializer_class = PersonRegistrationRequestSerializer
	permission_classes = (AllowAny,)
	throttle_classes = (AnonRateThrottle,)
	lookup_field = 'key'

	def perform_create(self, serializer):
		instance: PersonRegistrationRequest = serializer.save()

		# Send verification email to user on request
		if not settings.DEBUG:
			send_registration_email.delay(instance.pk)

		instance.save()

		return True


class PersonInvitationRequestRetrieveUpdateView(generics.RetrieveUpdateAPIView):
	"""
	Can to be used for check does invitation requests exists by key.
	It also can be used to update state of requests, mark it as accepted.
	"""
	queryset = PersonInvitationRequest.valid.all()
	serializer_class = PersonInvitationRequestRetrieveUpdateSerializer
	permission_classes = (AllowAny,)
	throttle_classes = (AnonRateThrottle,)
	lookup_field = 'key'
	http_method_names = (
		'head',
		'options',
		'get',
		'put'
	)


class PersonForgotPasswordRequestConfirmView(mixins.RetrieveModelMixin,
											 mixins.UpdateModelMixin,
											 mixins.CreateModelMixin,
											 viewsets.GenericViewSet):
	"""
	By this view we can confirm password resetting to get value.
	Example:
	{
	"new_password1": "thestrongestpasswordever",
	"new_password2": "thestrongestpasswordever"
	}
	"""
	queryset = PersonForgotRequest.valid.all()
	lookup_field = 'key'
	permission_classes = (
		AllowAny,
	)
	throttle_classes = (
		AnonRateThrottle,
	)
	http_method_names = (
		'head',
		'options',
		'get',
		'patch',
		'post'
	)

	def get_serializer_class(self):
		"""
		We have to use 2 different serializer for POST and PATCH
		So that we can use 2 different inputs model.
		"""
		method = self.request.method
		serializers_tree = {
			'POST': PersonPasswordResetRequestSerializer,
			'PATCH': PersonPasswordResetConfirmSerializer
		}

		try:
			result = serializers_tree[method]
		except KeyError:
			return PersonForgotRequestSerializer

		return result


class PersonInvitationRequestListView(generics.ListAPIView):
	"""
	Invited person is already exists in PmDragon but should accept invitation
	to be participant in workspace.
	"""
	queryset = PersonInvitationRequest.valid.all()
	serializer_class = PersonInvitationRequestSerializer
	permission_classes = (
		IsAuthenticated,
		IsParticipateInWorkspace
	)


class PersonInvitationRequestListCreateView(generics.ListCreateAPIView):
	"""
	Can be useful for bulk create requests by giving
	1) Email
	2) Workspace prefix
	"""
	queryset = PersonInvitationRequest.valid.all()
	serializer_class = PersonInvitationRequestList
	permission_classes = (
		AllowAny,
	)
	http_method_names = (
		'post',
		'head',
		'options'
	)

	def create(self, request, *args, **kwargs):
		""" On creation it doesn't matter if person with given email already exists in Pmdragon or not
		So we don't care and just create request. We will see if he exists later on creation stage """
		invited_by = request.user.person

		try:
			invitations = request.data['invitees']
		except KeyError:
			raise ValidationError(_('Invalid data. Expected a invitees key in dictionary.'))

		if type(invitations) is not list:
			raise ValidationError(_('Invalid data. Expected a list'))

		invitations_response = []

		for invitation in invitations:

			_workspace_pk = invitation.get('workspace', None)
			_email = invitation.get('email', None)

			try:
				_workspace = Workspace.objects.get(pk=_workspace_pk,
												   participants__in=[invited_by])
			except Workspace.DoesNotExist:
				raise ValidationError(_('You cannot invite to this workspace, '
										'you are not in or workspace does not exists'))

			"""
			Checking if person is already participate in given workspace
			So there is no reason to invite """
			participants_emails_list = _workspace.participants.values_list('user__email', flat=True)
			if _email in participants_emails_list:
				continue

			_invitation_request = PersonInvitationRequest.objects.create(
				email=_email,
				workspace=_workspace
			)

			if not settings.DEBUG:
				send_invitation_email.delay(_invitation_request.pk)
				print('DEBUG: Sent invitation email...')

			serializer = PersonInvitationRequestSerializer(_invitation_request)
			invitations_response.append(serializer.data)

		return Response(data=invitations_response,
						status=status.HTTP_201_CREATED)


class PersonInvitationRequestAcceptView(viewsets.GenericViewSet,
										mixins.UpdateModelMixin):
	"""
	Accept collaboration request for already registered persons.
	We use key as a uniq identifier
	When user accept it - we update field is_accepted from False -> True
	"""
	queryset = PersonInvitationRequest.valid.all()
	serializer_class = PersonInvitationRequestSerializer
	permission_classes = (
		AllowAny,
	)
	throttle_classes = (
		AnonRateThrottle,
	)
	lookup_field = 'key'


class PersonRegistrationRequestVerifyView(generics.CreateAPIView,
										  viewsets.ViewSetMixin):
	"""
	Create a Person object linked to User after confirmation email.
	"""
	queryset = Person.objects.all()
	serializer_class = PersonRegistrationOrInvitationRequestSerializer
	permission_classes = (
		AllowAny,
	)


class PersonsViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	Getting all persons in available workspaces
	"""
	queryset = Person.objects.all()
	serializer_class = PersonSerializer
	permission_classes = (
		IsAuthenticated,
	)

	def get_queryset(self):
		queryset: Person.objects = super().get_queryset()

		try:
			workspaces = Workspace\
				.objects \
				.filter(participants__in=[self.request.user.person]) \
				.all()
		except Person.DoesNotExist:
			workspaces = queryset.none()

		# @todo Make it much simplier via db
		collaborators = []
		for workspace in workspaces:
			for participant in workspace.participants.all():
				collaborators.append(participant.id)

		collaborators_set = set(collaborators)

		return queryset.filter(id__in=collaborators_set).all()


class WorkspaceViewSet(viewsets.ModelViewSet):
	"""
	Writable endpoint for workspaces
	Of course we need to add information about current person
	to created_by and participant
	"""
	permission_classes = (
		IsAuthenticated,
		IsOwnerOrReadOnly
	)

	serializer_class = WorkspaceWritableSerializer
	queryset = Workspace.objects.all()

	def get_queryset(self):
		queryset = super().get_queryset()
		try:
			person = self.request.user.person
			return queryset.filter(participants__in=[person])
		except Person.DoesNotExist:
			return queryset.none()

	def get_serializer_class(self):
		if self.action == 'list':
			return WorkspaceDetailedSerializer
		else:
			return WorkspaceWritableSerializer

	def get_serializer_context(self):
		"""
		Put to serializer context information about current person
		"""
		context = super().get_serializer_context()
		try:
			context.update({
				'person': self.request.user.person
			})
		except Person.DoesNotExist:
			pass

		return context

	def create(self, request, *args, **kwargs):
		workspace_data = request.data

		short_serializer = WorkspaceWritableSerializer(
			data=workspace_data,
			context={'person': self.request.user.person}
		)

		if not short_serializer.is_valid():
			return Response(
				data=short_serializer.errors,
				status=status.HTTP_400_BAD_REQUEST
			)

		short_serializer.save()
		detailed_serializer = WorkspaceDetailedSerializer(instance=short_serializer.instance)

		return Response(
			data=detailed_serializer.data,
			status=status.HTTP_201_CREATED
		)


class WorkspaceReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	Get all workspaces current Person participate in
	We need it on frontend to understand list of workspaces to switch between
	If person does not participate in Workspace -> he / her has no access
	to Workspace related data.
	On the other hand - if person participate in Workspace - he / her has full access
	to all Workspace related data.
	"""
	permission_classes = (
		IsAuthenticated,
	)

	serializer_class = WorkspaceDetailedSerializer
	queryset = Workspace.objects.all()

	def get_queryset(self):
		queryset = super().get_queryset()
		try:
			person = self.request.user.person
			return queryset.filter(participants__in=[person]).all()
		except Person.DoesNotExist:
			return queryset.none()


class WorkspacesReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	Extendable class to have read only ViewSet of any instance, that have
	workspace isolation.
	We can use it without mixins as Read Only view
	Or can use Mixins to add Update | Remove options.
	"""
	permission_classes = (
		IsAuthenticated,
	)

	def get_queryset(self):
		"""
		Getting all instances, that belong to this workspace.
		"""
		queryset = super().get_queryset()
		try:
			person = self.request.user.person
			return queryset.filter(workspace__participants__in=[person]).all()
		except Person.DoesNotExist:
			return queryset.none()

	def get_serializer_context(self):
		"""
		Put to serializer context information about current person
		"""
		context = super().get_serializer_context()
		context['person'] = None
		try:
			person = self.request.user.person
			context.update({
				'person': person
			})
		except Person.DoesNotExist:
			pass

		return context


class WorkspacesModelViewSet(WorkspacesReadOnlyModelViewSet,
							 mixins.CreateModelMixin,
							 mixins.UpdateModelMixin,
							 mixins.DestroyModelMixin):
	"""
	@todo Added IsOwnerOrReadOnly permission
	not allow to remove participants from workspace
	"""
	permission_classes = (
		IsAuthenticated
	)
	"""
	Extendable class to have writable ViewSet,
	that have isolation by workspaces.
	"""
	pass


class ProjectViewSet(WorkspacesModelViewSet):
	"""
	View for getting, editing, deleting instance.
	"""
	queryset = Project.objects.all()
	serializer_class = ProjectSerializer
	permission_classes = (
		IsAuthenticated,
		IsParticipateInWorkspace,
		IsOwnerOrReadOnly,
	)


class IssueTypeCategoryViewSet(WorkspacesModelViewSet):
	"""
	View for getting, editing, deleting instance.
	"""
	queryset = IssueTypeCategory.objects.all()
	serializer_class = IssueTypeSerializer
	permission_classes = (
		IsAuthenticated,
		IsParticipateInWorkspace
	)


class IssueTypeIconViewSet(WorkspacesModelViewSet):
	"""
	Just CRUD with Issue Type Icons
	"""
	queryset = IssueTypeCategoryIcon.objects.all()
	serializer_class = IssueTypeIconSerializer
	permission_classes = (
		IsAuthenticated,
		IsParticipateInWorkspace,
		WorkspaceOwnerOrReadOnly,
	)


class IssueStateCategoryViewSet(WorkspacesModelViewSet):
	"""
	View for getting, editing, deleting instance.
	"""
	queryset = IssueStateCategory.objects.all()
	serializer_class = IssueStateSerializer
	permission_classes = (
		IsAuthenticated,
		IsParticipateInWorkspace,
		WorkspaceOwnerOrReadOnly,
	)


class IssueEstimationCategoryViewSet(WorkspacesModelViewSet):
	"""
	Just CRUD with Issue Estimations.
	"""
	queryset = IssueEstimationCategory.objects.all()
	serializer_class = IssueEstimationSerializer
	permission_classes = (
		IsAuthenticated,
		IsParticipateInWorkspace,
		WorkspaceOwnerOrReadOnly
	)


class IssueViewSet(WorkspacesModelViewSet):
	"""
	View for getting, editing, deleting instance.
	"""
	queryset = Issue.objects.all()
	serializer_class = IssueSerializer
	permission_classes = (
		IsAuthenticated,
		IsParticipateInWorkspace,
	)


class IssueHistoryViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	We use this view to get history entries for current issue.
	We use filter backend for it with issue param.
	@todo check that IsParticipateInWorkspace is not a problem's root.
	"""
	queryset = IssueHistory.objects.all()
	serializer_class = IssueHistorySerializer
	permission_classes = (
		IsAuthenticated,
		IsParticipateInWorkspace
	)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['issue']

	def get_serializer_context(self):
		"""
		Put to serializer context information about current person
		"""
		context = super().get_serializer_context()

		try:
			context.update({
				'person': self.request.user.person
			})
		except Person.DoesNotExist:
			pass

		return context


class IssueMessagesViewSet(WorkspacesModelViewSet):
	"""
	We use this view to get messages for current issue.
	We use filter backend for it with issue param
	"""
	queryset = IssueMessage.objects.all()
	serializer_class = IssueMessageSerializer
	permission_classes = (
		IsAuthenticated,
		IsParticipateInWorkspace,
		IsCreatorOrReadOnly
	)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['issue']


def format_message(message: IssueMessage, is_mine: bool, is_label: bool):
	return {
		"label": message.created_at.strftime('%B %-d') if is_label else False,
		"key": message.id,
		"createdBy": PersonSerializer(data=message.created_by).data,
		"sent": is_mine,
		"text": [
			message.description
		],
		"date": message.created_at,
		"list": [
			message
		]
	}


class IssueMessagesPackedView(GenericAPIView):
	"""
	Actually we already have a message view.
	But on frontend we have to group close by time
	and author messages.
	I think it's much more easier to get already packed
	messages from backend.
	Of course we can pack it on frontend, but it can lead us to
	performance related issues on client side.

	When we add one more message or remove one from the group -
	we do it on frontend based on message creation response body + post 201.
	"""
	permission_classes = (
		AllowAny,
	)

	@staticmethod
	def get(request, issue_id):
		"""
		We need packed messages to group messaged
		for the same author and same date
		It's look much much better
		"""
		messages = IssueMessage \
			.objects \
			.filter(issue_id=issue_id) \
			.all()

		not_normalized_message_pack = []
		for index, message in enumerate(messages):
			same_author_as_last: bool = index != 0 and message.created_by == messages[index - 1].created_by
			same_date_as_last: bool = index != 0 and message.created_at.date() == messages[index - 1].created_at.date()

			"""
			We can aggregate messages that was created
			at the same day and by the same person
			"""
			if same_author_as_last and same_date_as_last:
				not_normalized_message_pack[-1].append(message)
			else:
				not_normalized_message_pack.append([message])

		normalized_message_pack = []
		for pack_slice in not_normalized_message_pack:
			first_message: IssueMessage = pack_slice[0]
			normalized_message_pack.append({
				"label": first_message.created_at.strftime('%B %-d'),
				"key": first_message.id,
				"createdBy": PersonSerializer(
					instance=first_message.created_by,
					context={'request': request}).data,
				"sent": first_message.created_by.user == request.user,
				"date": first_message.created_at,
				"list": IssueMessageSerializer(
					instance=pack_slice,
					many=True,
					context={'request': request}).data
			})

		return Response(data=normalized_message_pack,
						status=status.HTTP_200_OK)


class IssueAttachmentViewSet(WorkspacesReadOnlyModelViewSet,
							 mixins.CreateModelMixin,
							 mixins.UpdateModelMixin,
							 mixins.DestroyModelMixin):
	"""
	This view handle anything except
	create (POST), cuz it's handled
	by another view IssueAttachmentUpload
	"""
	queryset = IssueAttachment.objects.all()
	serializer_class = IssueAttachmentSerializer
	permission_classes = (
		IsAuthenticated,
		IsParticipateInWorkspace,
		IsCreatorOrReadOnly
	)

	def create(self, request, *args, **kwargs):
		self.parser_classes = [MultiPartParser]
		"""
		<-- Example of data in raw_data
		{
		  "workspace": 0,
		  "project": 0,
		  "title": "string",
		  "attachment": "string"
		}

		--> Example of output
		{
		  "id": 0,
		  "workspace": 0,
		  "project": 0,
		  "title": "string",
		  "attachment": "string",
		  "created_at": "2021-01-20T15:34:41.989Z",
		  "updated_at": "2021-01-20T15:34:41.989Z"
		}
		"""
		file_obj = request.data['file']
		raw_data = request.data['data']

		data = json.loads(raw_data)

		workspace = Workspace.objects.get(pk=data['workspace'])
		project = Project.objects.get(pk=data['project'])
		issue = Issue.objects.get(pk=data['issue'])

		title = data['title'] or file_obj.name

		attachment = IssueAttachment(
			workspace=workspace,
			project=project,
			title=title,
			attachment=file_obj,
			attachment_size=file_obj.size,
			created_by=self.request.user.person
		)

		from conf.common import mime_settings

		try:

			icon = [entry[2]
					for entry
					in mime_settings.FILE_EXTENSIONS_MAPPING
					if file_obj.content_type in entry[0]][0][0]
			attachment.icon = icon
		except IndexError:
			pass

		try:
			is_preview = [entry[3]
						  for entry
						  in mime_settings.FILE_EXTENSIONS_MAPPING
						  if file_obj.content_type in entry[0]][0]
			attachment.show_preview = is_preview
		except IndexError:
			pass

		attachment.save()
		issue.attachments.add(attachment)

		serializer = self.get_serializer(instance=attachment)

		return Response(
			data=serializer.data,
			status=status.HTTP_201_CREATED
		)


class ProjectBacklogViewSet(WorkspacesReadOnlyModelViewSet,
							mixins.UpdateModelMixin):
	"""
	View for getting, editing, instance.
	Project Backlog view allow us to read issues list
	or change it if we moving issues between sprint Backlog and
	Project Backlog.
	"""
	queryset = ProjectBacklog.objects.all()
	serializer_class = BacklogWritableSerializer
	permission_classes = (
		IsAuthenticated,
		IsParticipateInWorkspace,
	)


class ProjectWorkingDaysViewSet(WorkspacesReadOnlyModelViewSet,
										mixins.UpdateModelMixin):
	"""
	We use Working Days to build a guideline for Sprint BurnDown Chart.
	ProjectWorkingDays contain:
	weekday + non-working days
	"""
	queryset = ProjectWorkingDays.objects.all()
	serializer_class = ProjectWorkingDaysSerializer
	permission_classes = (
		IsAuthenticated,
		IsParticipateInWorkspace
	)


class ProjectNonWorkingDayViewSet(WorkspacesModelViewSet):
	"""
	Non-working days are always linked to
	ProjectWorkingDays.
	At this stage we use non-working days to calculate
	guideline for sprint completion.
	"""
	queryset = ProjectNonWorkingDay.objects.all()
	serializer_class = NonWorkingDaysSerializer
	permission_classes = (
		IsAuthenticated,
		IsParticipateInWorkspace
	)


class SprintDurationViewSet(WorkspacesModelViewSet):
	"""
	View for getting, editing, deleting instance.
	We do not use it at this stage.
	It can be useful to prefill Sprint Finished at
	based on Sprint started at.
	"""
	queryset = SprintDuration.objects.all()
	serializer_class = SprintDurationSerializer
	permission_classes = (
		IsAuthenticated,
		IsParticipateInWorkspace,
	)


class SprintViewSet(WorkspacesModelViewSet):
	"""
	View for getting, editing, deleting instance.
	"""
	queryset = Sprint.objects.all()
	serializer_class = SprintWritableSerializer
	permission_classes = (
		IsAuthenticated,
		IsParticipateInWorkspace,
	)


class SprintEffortsHistoryViewSet(WorkspacesReadOnlyModelViewSet):
	"""
	Estimation is auto-calculated so we can just get it.
	"""
	queryset = SprintEffortsHistory.objects.all()
	serializer_class = SprintEffortsHistorySerializer
	permission_classes = (
		IsAuthenticated,
		IsParticipateInWorkspace,
	)
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['sprint']


class SprintGuidelineView(views.APIView):
	"""
	This view let us to get Sprint Guideline
	For Sprint BurnDown Chart.
	We use this chart to predict Sprint implementation
	"""
	permission_classes = (
		IsAuthenticated,
	)

	@staticmethod
	def get(request, key):
		try:
			sprint = Sprint.objects.get(pk=key)
		except Sprint.DoesNotExist:
			return Response(status=status.HTTP_404_NOT_FOUND)

		project_standard_working_days = ProjectWorkingDays\
			.objects\
			.filter(
				workspace=sprint.workspace,
				project=sprint.project
			) \
			.get()

		sprint_analyser = SprintAnalyser(sprint, project_standard_working_days)

		data = sprint_analyser.calculate_estimated_efforts_distribution()

		return Response(data)


class PersonSetPasswordView(GenericAPIView):
	"""
	We use it to update password for user.
	"""
	queryset = User.objects.all()
	serializer_class = UserSetPasswordSerializer
	permission_classes = (
		IsAuthenticated,
	)

	def post(self, request):
		"""
		Set password for user
		"""
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response({'detail': _('New password has been saved.')},
						status=status.HTTP_200_OK)


class PersonAvatarUpload(views.APIView):
	"""
	Person avatar picture APIView
	We need it to upload user avatar and update it.
	"""
	permission_classes = (
		IsAuthenticated,
	)
	parser_classes = [MultiPartParser]

	def put(self, request):
		file_obj = request.data['image']

		person: Person = self.request.user.person
		person.avatar.save(file_obj.name, file_obj)
		person.save()

		if settings.DEPLOYMENT != 'HEROKU':
			avatar_url = request.build_absolute_uri(person.avatar.url)
		else:
			avatar_url = person.avatar.url

		response_data = {
			'avatar': avatar_url
		}

		return Response(
			data=response_data,
			status=status.HTTP_200_OK
		)

	def delete(self, request):
		person: Person = self.request.user.person
		person.avatar.delete()
		person.save()

		return Response(
			status=status.HTTP_204_NO_CONTENT
		)


class UserUpdateView(generics.UpdateAPIView,
					 viewsets.ViewSetMixin):
	"""
	We use this view for updating user data such as:
	 - First Name
	 - Last Name
	 - username
	"""
	queryset = User.objects.all()
	serializer_class = UserUpdateSerializer
	permission_classes = [IsAuthenticated]

	def get_object(self):
		queryset = self.filter_queryset(self.get_queryset())
		object_ = queryset.get(pk=self.request.user.id)
		self.check_object_permissions(self.request, object_)

		return object_

	def update(self, request, *args, **kwargs):
		user = request.user

		serializer = self.get_serializer(
			user,
			data=request.data,
			partial=True
		)

		if not serializer.is_valid():
			return Response(data=serializer.errors,
							status=status.HTTP_400_BAD_REQUEST)

		self.perform_update(serializer)

		return super().update(request, *args, **kwargs)


def validate_ids(data, field='id', unique=True):
	"""
	By this method we just return uniq list
	Actually we use it for {issue_id:xxx order: xxx}
	We don't really know what to do if we got
	2 different order for the same issue.
	Of course frontend should prevent it.
	But i decided not raise an Exception for this case.
	"""
	if not isinstance(data, list):
		return [data]

	id_list = [int(x[field]) for x in data if field in x]

	unique_id_list = set(id_list)

	if unique and len(id_list) != len(unique_id_list):
		return unique_id_list

	return id_list


class IssueListUpdateApiView(UpdateAPIView):
	"""
	Bulk update issues ordering, doesn't matter is it a Backlog
	or Sprint or Agile Board.
	"""
	schema = IssueListUpdateSchema()
	serializer_class = IssueChildOrderingSerializer
	http_method_names = ['put', 'options', 'head']

	def get_queryset(self, ids=None):
		queryset = Issue.objects.filter(workspace__participants__in=[self.request.user.person])

		if ids is None:
			return queryset

		return queryset.filter(id__in=ids)

	def update(self, request, *args, **kwargs):
		ids = validate_ids(data=request.data)
		instances = self.get_queryset(ids=ids)
		serializer = self.get_serializer(
			instances, data=request.data, partial=False, many=True
		)
		serializer.is_valid(raise_exception=True)
		self.perform_update(serializer)

		return Response(serializer.data)
