from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import update_last_login, User
from django.db import IntegrityError
from django.db.models import Max
from django.forms import Form
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt import serializers as serializers_jwt

from apps.core.api.tasks import send_forgot_password_email
from apps.core.models import PersonRegistrationRequest, Workspace, PersonInvitationRequest, PersonForgotRequest, Person, \
	Project, IssueTypeCategoryIcon, IssueTypeCategory, IssueStateCategory, IssueEstimationCategory, Issue, IssueHistory, \
	IssueMessage, IssueAttachment, ProjectNonWorkingDay, ProjectBacklog, ProjectWorkingDays, SprintDuration, Sprint, \
	SprintEffortsHistory

UserModel = get_user_model()


def order_issues(validated_data):
	"""
	validated_data should contain issues key.
	We use it in Backlog and Sprint serializers to order it
	by dragging between sprint and Backlog and inside of SCRUM board.
	"""
	if 'issues' not in validated_data:
		return validated_data

	ordered_issues = validated_data['issues']

	for index, issue in enumerate(ordered_issues):
		issue.ordering = index
		issue.save()

		ordered_issues[index] = issue

	validated_data['issues'] = ordered_issues

	return validated_data


class TokenObtainPairExtendedSerializer(serializers_jwt.TokenObtainPairSerializer):
	"""
	We use this serializer to get jwt token
	Extend parent class to add extra data to token.
	Currently: username, first_name, last_name
	"""

	def create(self, validated_data):
		"""
		Implemented for all abstract methods.
		We don't need this method to serializer works properly.
		"""
		pass

	def update(self, instance, validated_data):
		"""
		Implemented for all abstract methods.
		We don't need this method to serializer works properly.
		"""
		pass

	@classmethod
	def get_token(cls, user: UserModel):
		token = super().get_token(user)

		try:
			token['person_id'] = user.person.id
		except User.person.RelatedObjectDoesNotExist:
			raise ValidationError(_('Given user not registered as person in any workspace'))

		token['username'] = user.username
		token['first_name'] = user.first_name
		token['last_name'] = user.last_name

		"""
		Update last login on obtaining token """
		update_last_login(None, user)

		return token

	def validate(self, attrs):
		parent_data = super().validate(attrs)

		refresh_token = parent_data.pop('refresh')
		access_token = parent_data.pop('access')

		assert len(parent_data) == 0, \
			_('Some parent data was missing')

		data = {
			'access': access_token,
			'refresh': refresh_token
		}

		return data


class PersonRegistrationRequestSerializer(serializers.ModelSerializer):
	"""
	We use it to create and get registration request
	1) Get for check that registration is correct
	2) Create for make new registration for user with workspace
	Common Serializer for Person Registration Request on Registration
	"""

	class Meta:
		model = PersonRegistrationRequest
		fields = (
			'email',
			'prefix_url'
		)

	@classmethod
	def validate_prefix_url(cls, attrs):
		"""
		We want to be sure that user not expect to get
		workspace with already exists prefix
		@rtype: None
		@param attrs: string
		"""
		prefix_url = attrs
		workspaces_with_same_prefix = Workspace.objects.filter(prefix_url=prefix_url)
		if workspaces_with_same_prefix.exists():
			raise ValidationError(_('Workspace with given prefix already exists.'))

		return prefix_url

	@classmethod
	def validate_email(cls, attrs):
		"""
		We want to be sure that user,
		that already exists will register one more time with the same email
		@param attrs: We expect to have email here
		@return:
		"""

		email = attrs
		users_with_the_same_email = User.objects.filter(email=email)
		if users_with_the_same_email.exists():
			raise ValidationError(_('User with given email already exists.'))

		return email


class PersonInvitationRequestRetrieveUpdateSerializer(serializers.ModelSerializer):
	"""
	We use this for getting invitation requests and checking
	that this invitation is correct.
	Update request after getting email and follow link inside
	"""

	class Meta:
		model = PersonInvitationRequest
		fields = (
			'email',
			'workspace',
			'is_accepted'
		)
		extra_kwargs = {
			'email': {'read_only': True},
			'workspace': {'read_only': True},
			'is_accepted': {'write_only': True}
		}
		depth = 1

	def update(self, instance, validated_data):
		is_accepted = validated_data.get('is_accepted', instance.is_accepted)

		try:
			user = User.objects.filter(email=instance.email).get()
		except User.MultipleObjectsReturned:
			raise ValidationError(_('Error occurred while getting person to add'))

		if is_accepted and not instance.is_accepted:
			workspace = instance.workspace
			workspace.participants.add(user.person)
			workspace.save()

			instance.is_accepted = True
			instance.save()

		return instance


class PersonInvitationRequestSerializer(serializers.ModelSerializer):
	"""
	We use it to invite multiple users to workspace.
	We also need to check that invitation is correct, update it (set is_accepted to True)
	"""
	class Meta:
		model = PersonInvitationRequest
		fields = (
			'email',
			'workspace',
			'created_at',
			'expired_at'
		)
		extra_kwargs = {
			'expired_at': {'read_only': True}
		}


class PersonForgotRequestSerializer(serializers.ModelSerializer):
	"""
	We use this serializer for GET, HEAD, OPTIONS requests
	"""
	class Meta:
		model = PersonForgotRequest
		fields = (
			'email',
			'created_at',
			'expired_at'
		)


class PersonInvitationRequestList(serializers.Serializer):
	"""
	We use it to invite multiple persons in Workspace
	From Team page on frontend.
	"""
	def create(self, validated_data):
		"""
		Implemented for all abstract methods.
		We don't need this method to serializer works properly.
		"""
		pass

	def update(self, instance, validated_data):
		"""
		Implemented for all abstract methods.
		We don't need this method to serializer works properly.
		"""
		pass

	invitees = PersonInvitationRequestSerializer(many=True)

	class Meta:
		fields = (
			'invitees',
		)


class UserSetPasswordSerializer(serializers.Serializer):
	"""
	Serializer to update password of user.
	We use it normally on Me page on frontend.
	"""

	old_password = serializers.CharField(max_length=128, write_only=True)
	new_password1 = serializers.CharField(max_length=128, write_only=True)
	new_password2 = serializers.CharField(max_length=128, write_only=True)

	set_password_form_class = SetPasswordForm

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.request = self.context.get('request')
		self.user = getattr(self.request, 'user', None)
		self.set_password_form: [Form] = None

	def create(self, validated_data):
		"""
		Implemented for all abstract methods.
		We don't need this method to serializer works properly.
		"""
		pass

	def update(self, instance, validated_data):
		"""
		Implemented for all abstract methods.
		We don't need this method to serializer works properly.
		"""
		pass

	def validate_old_password(self, value):
		invalid_conditions = (
			self.user,
			not self.user.check_password(value),
		)

		if all(invalid_conditions):
			error_message = _('Old one password was entered incorrectly for current user. '
							  'Please try again. ')
			raise ValidationError(error_message)

		return value

	def validate(self, attrs):
		self.set_password_form = self.set_password_form_class(
			user=self.user, data=attrs,
		)

		if not self.set_password_form.is_valid():
			serializers.ValidationError(self.set_password_form.errors)

		new_password1 = attrs['new_password1']
		new_password2 = attrs['new_password2']

		if new_password1 != new_password2:
			serializers.ValidationError({
				'new_password2': "Password confirmation doesn't match password"
			})

		return attrs

	def save(self, **kwargs):
		self.set_password_form.save()
		from django.contrib.auth import update_session_auth_hash
		update_session_auth_hash(self.request, self.user)


class PersonPasswordResetConfirmSerializer(serializers.Serializer):
	"""
	After confirmation email by following link
	We can set new password for user.
	"""
	new_password1 = serializers.CharField(max_length=128, write_only=True)
	new_password2 = serializers.CharField(max_length=128, write_only=True)

	def validate(self, attrs: dict) -> dict:
		""" Let's check that two passwords are match """
		new_password1 = attrs.get('new_password1')
		new_password2 = attrs.get('new_password2')

		if new_password1 != new_password2:
			raise ValidationError(_(
				'Given passwords do not match.'
			))

		return attrs

	def update(self, instance: PersonForgotRequest, validated_data):
		new_password2 = validated_data.get('new_password2')
		user = User.objects.get(email=instance.email)
		user.set_password(new_password2)
		user.save()

		# Let's mark request as accepted
		instance.is_accepted = True
		instance.save()

		return instance

	def create(self, validated_data):
		"""
		Implemented for all abstract methods.
		We don't need this method to serializer works properly.
		"""
		pass


class PersonPasswordResetRequestSerializer(serializers.Serializer):
	"""
	By this serializer we can request a password restoring.
	If user follow link than we will use another serializer
	"""
	email = serializers.EmailField(max_length=128,
								   min_length=4)

	def create(self, validated_data):
		email: str = validated_data.get('email')
		password_forgot_request = PersonForgotRequest(
			email=email.lower()
		)

		password_forgot_request.save()

		if not settings.DEBUG:
			send_forgot_password_email.delay(password_forgot_request.id)

		return password_forgot_request

	def update(self, instance, validated_data):
		"""
		Implemented for all abstract methods.
		We don't need this method to serializer works properly.
		"""
		pass


class PersonRegistrationOrInvitationRequestSerializer(serializers.Serializer):
	"""
	Custom Serializer for verifying Person registration
	For creating Person after confirmation of authenticity of email
	"""
	key = serializers.CharField(max_length=128, write_only=True)
	password = serializers.CharField(max_length=30, write_only=True)
	is_invited = serializers.BooleanField(write_only=True)

	class Meta:
		fields = (
			'key',
			'password'
		)
		extra_kwargs = {
			'key': {'write_only': True},
			'password': {'write_only': True},
			'is_invited': {'write_only': True}
		}

	def create(self, validated_data):
		key = validated_data.get('key')
		password = validated_data.get('password')
		is_invited = validated_data.get('is_invited')

		"""
		If person was invited than we have to search him in PersonInvitationRequests
		else we will try to find him in PersonRegistrationRequests """
		if is_invited:
			request_with_key = PersonInvitationRequest.valid.filter(key=key)
		else:
			request_with_key = PersonRegistrationRequest.valid.filter(key=key)

		if not request_with_key.exists():
			raise serializers.ValidationError({
				'detail': _('Request for registration or invitation was expired or not correct')
			})

		request = request_with_key.get()

		"""
		Check if user with the same email already exists """
		email_equal_users_count = User.objects.filter(email=request.email)
		if email_equal_users_count.exists():
			raise serializers.ValidationError({
				'detail': _('User with the same email already exists. '
							'You can create new workspace in you account. '
							'If you forgot you password you also can restore it')
			})

		user = User(username=request.email, email=request.email)
		user.set_password(password)

		try:
			user.save()

		except IntegrityError:
			raise serializers.ValidationError({
				'detail': _('Someone already registered with this data')
			})

		person = Person(user=user)
		person.save()

		if is_invited:
			"""
			If user was invited then workspace already exists
			And we don't need to create it """
			request: PersonInvitationRequest
			workspace = request.workspace
		else:
			"""
			If user is self registered with prefix_url for workspace then
			we have to create workspace for him. """
			request: PersonRegistrationRequest
			workspace = Workspace(prefix_url=request.prefix_url,
								  owned_by=person)

			try:
				workspace.save()
			except IntegrityError:
				# @todo Had problems with interpreting result of registration
				# Workspace with given prefix url was already registered. was returned on different integrityError
				raise serializers.ValidationError({
					'detail': _('Workspace with given prefix url was already registered.')
				})

		workspace.participants.add(person)
		workspace.save()

		return person

	def update(self, instance, validated_data):
		"""
		Implemented for all abstract methods.
		We don't need this method to serializer works properly.
		"""
		pass


class UserUpdateSerializer(serializers.ModelSerializer):
	"""
	We need this serializer for update base information
	about user
	"""

	class Meta:
		model = UserModel
		fields = (
			'username',
			'first_name',
			'last_name'
		)
		extra_kwargs = {
			'username': {
				'max_length': 20
			}
		}


class PersonSerializer(serializers.ModelSerializer):
	"""
	Common Person Serializer.
	We don't need it yet.
	But maybe we will.
	"""

	class Meta:
		model = Person
		fields = (
			'id',
			'username',
			'email',
			'avatar',
			'first_name',
			'last_name',
			'title',
			'is_active',
			'last_login',
			'created_at'
		)
		extra_kwargs = {
			'id': {'read_only': True},
			'created_at': {'read_only': True},
			'is_active': {'read_only': True}
		}


class WorkspaceWritableSerializer(serializers.ModelSerializer):
	"""
	For creating / editing / removing workspaces
	"""

	class Meta:
		model = Workspace
		fields = (
			'id',
			'prefix_url',
			'participants'
		)

	def create(self, validated_data):
		prefix_url = validated_data.get('prefix_url')
		participants = validated_data.get('participants', None)
		person = self.context.get('person')

		workspace = Workspace(
			prefix_url=prefix_url,
			owned_by=person
		)

		try:
			workspace.save()
		except IntegrityError:
			raise serializers.ValidationError({
				'detail': _('Workspace with given prefix url was already registered.')
			})

		"""
		Iteration for the list of participants ids """
		if participants:
			for person_id in participants:
				_person = Person.objects.get(pk=person_id)
				workspace.participants.add(_person)

		workspace.participants.add(person)
		workspace.save()

		return workspace

	def validate_participants(self, participants: list):
		if self.instance.owned_by not in participants:
			raise ValidationError(_('Workspace owner cannot be removed from the workspace'))

		return participants


class WorkspaceDetailedSerializer(serializers.ModelSerializer):
	"""
	For getting information about all persons participated in workspace.
	We can get information just from the spaces we belong.
	"""
	participants = PersonSerializer(many=True)

	class Meta:
		model = Workspace
		fields = (
			'id',
			'prefix_url',
			'participants',
			'projects'
		)
		depth = 1


class WorkspaceModelSerializer(serializers.ModelSerializer):
	"""
	In most cases we just extend this class
	"""
	def validate_workspace(self, value):
		"""
		Check that given workspace contains person sending request.
		"""
		try:
			Workspace.objects \
				.filter(participants__in=[self.context['person']]) \
				.get(prefix_url__exact=value)

		except (KeyError, Workspace.DoesNotExist):
			raise ValidationError(_('Incorrect workspace given for current user'))

		return value


class ProjectSerializer(WorkspaceModelSerializer):
	"""
	Common project serializer
	For getting list of projects in workspace
	"""

	class Meta:
		model = Project
		fields = (
			'id',
			'workspace',
			'title',
			'key',
			'owned_by',
			'created_at'
		)

	def create(self, validated_data):
		workspace = validated_data.get('workspace')
		title = validated_data.get('title')
		key = validated_data.get('key')

		project = Project(
			workspace=workspace,
			title=title,
			key=key,
			owned_by=self.context.get('person')
		)

		try:
			project.save()
		except IntegrityError:
			raise serializers.ValidationError({
				'detail': _('Project name and key should be unique.')
			})

		return project

	def validate_owned_by(self, attrs):
		if self.instance and attrs not in self.instance.workspace.participants.all():
			raise ValidationError(_('You can change owner only to participant of current workspace'))

		return attrs


class IssueTypeIconSerializer(serializers.ModelSerializer):
	"""
	We use it to get list of issue types.
	"""
	class Meta:
		model = IssueTypeCategoryIcon
		fields = (
			'id',
			'workspace',
			'project',
			'prefix',
			'color'
		)


class IssueTypeSerializer(WorkspaceModelSerializer):
	"""
	Common issue category serializer
	For getting all types of issues
	"""

	class Meta:
		model = IssueTypeCategory
		fields = (
			'id',
			'workspace',
			'project',
			'title',
			'icon',
			'is_subtask',
			'is_default',
			'ordering'
		)


class IssueStateSerializer(WorkspaceModelSerializer):
	"""
	Common issue category serializer
	For getting all types of issue states
	"""

	class Meta:
		model = IssueStateCategory
		fields = (
			'id',
			'workspace',
			'project',
			'title',
			'is_default',
			'is_done',
			'ordering'
		)


class IssueEstimationSerializer(WorkspaceModelSerializer):
	"""
	Common issue estimation serializer
	I think we can do with it whatever we want. will see.
	"""

	class Meta:
		model = IssueEstimationCategory
		fields = (
			'id',
			'workspace',
			'project',
			'title',
			'value',
			'created_at',
			'updated_at'
		)

	def validate_value(self, attrs):
		if attrs != 0:
			return attrs

		"""
		Default value is maximum value + 1"""
		workspace = self.initial_data.get('workspace')
		project = self.initial_data.get('project')

		max_value = IssueEstimationCategory.objects \
			.filter(workspace=workspace,
					project=project) \
			.aggregate(Max('value')) \
			.get('value__max')

		return max_value + 1


class IssueSerializer(WorkspaceModelSerializer):
	"""
	Common issue serializer for getting all tasks
	No idea how to use it in reality yet
	"""

	class Meta:
		model = Issue
		fields = (
			'id',
			'number',
			'project_number',
			'workspace',
			'project',
			'title',
			'description',
			'type_category',
			'state_category',
			'estimation_category',
			'assignee',
			'attachments',
			'created_by',
			'created_at',
			'updated_at',
			'updated_by',
			'ordering',
		)
		extra_kwargs = {
			'number': {'read_only': True},
			'project_number': {'read_only': True},
			'created_by': {'read_only': True},
			'created_at': {'read_only': True},
			'type_category': {'required': False},
			'state_category': {'required': False},
			'attachments': {'allow_null': True},
			'estimation_category': {'required': False},
			'ordering': {'required': False},
		}

	def validate(self, attrs):
		data = super().validate(attrs)
		data['updated_by'] = self.context['person']
		return data

	def create(self, validated_data):
		"""
		If we crate it through issue.object.create then we will send two signal
		on create and on update and frontend will create 2 instance in backlog for issues
		"""
		instance = Issue(**validated_data)
		instance.created_by = self.context['person']
		instance.save()

		return instance


class IssueHistorySerializer(serializers.ModelSerializer):
	"""
	Issue History allow us to track changes and reflect it
	on issue history.
	"""
	class Meta:
		model = IssueHistory
		fields = (
			'id',
			'entry_type',
			'edited_field',
			'before_value',
			'after_value',
			'changed_by',
			'created_at',
			'updated_at'
		)


class IssueMessageSerializer(WorkspaceModelSerializer):
	"""
	We use this serializer to get messages for chosen issue
	"""
	class Meta:
		model = IssueMessage
		fields = (
			'id',
			'issue',
			'description',
			'created_by',
			'created_at',
			'updated_at'
		)
		extra_kwargs = {
			'created_at': {
				'read_only': True
			},
			'updated_at': {
				'read_only': True
			},
			'created_by': {
				'read_only': True
			}
		}

	def validate(self, attrs):
		data = super().validate(attrs)
		data['created_by'] = self.context['person']
		return data


class IssueAttachmentSerializer(WorkspaceModelSerializer):
	"""
	We use this serializer to get all attachments for Issue
	"""
	class Meta:
		model = IssueAttachment
		fields = (
			'id',
			'workspace',
			'project',
			'title',
			'attachment',
			'attachment_size',
			'show_preview',
			'icon',
			'created_by',
			'created_at',
			'updated_at'
		)
		extra_kwargs = {
			'attachment': {
				'read_only': True
			}
		}


class BacklogWritableSerializer(WorkspaceModelSerializer):
	"""
	This serializer allow us to change issues in backlog
	"""
	class Meta:
		model = ProjectBacklog
		fields = (
			'id',
			'workspace',
			'project',
			'issues'
		)

	def update(self, instance, validated_data):
		validated_data = order_issues(validated_data)
		return super().update(instance, validated_data)


class NonWorkingDaysSerializer(WorkspaceModelSerializer):
	class Meta:
		model = ProjectNonWorkingDay
		fields = (
			'id',
			'workspace',
			'project',
			'date'
		)


class ProjectWorkingDaysSerializer(WorkspaceModelSerializer):
	"""
	We use working days to determine working and non-working days.
	We also use it to build burn down chart delivery plan.
	"""
	class Meta:
		model = ProjectWorkingDays
		fields = (
			'id',
			'workspace',
			'project',
			'timezone',
			'monday',
			'tuesday',
			'wednesday',
			'thursday',
			'friday',
			'saturday',
			'sunday',
			'non_working_days',
			'updated_at'
		)


class SprintDurationSerializer(WorkspaceModelSerializer):
	"""
	Getting Sprint Duration Variant
	"""

	class Meta:
		model = SprintDuration
		fields = (
			'id',
			'workspace',
			'title',
			'duration',
		)


class SprintWritableSerializer(WorkspaceModelSerializer):
	"""
	If we want to update sprint data - we use this serializer.
	"""

	class Meta:
		model = Sprint
		fields = (
			'id',
			'workspace',
			'project',
			'title',
			'goal',
			'issues',
			'is_started',
			'is_completed',
			'started_at',
			'finished_at'
		)

	def update(self, instance, validated_data):
		validated_data = order_issues(validated_data)
		return super().update(instance, validated_data)


class SprintEffortsHistorySerializer(serializers.ModelSerializer):
	"""
	Sprint Estimation Serializer to get data and build a Chart
	(BurnDown Chart for example)
	"""

	class Meta:
		model = SprintEffortsHistory
		fields = (
			'point_at',
			'total_value',
			'done_value',
			'estimated_value'
		)


class IssueListSerializer(serializers.ListSerializer):
	"""
	Look at IssueChildOrderingSerializer,
	This serializer exist only for this purpose.
	"""

	def update(self, instance, validated_data):
		# @todo Refactor to bulk update. But check signals first !!!
		issue_mapping = {issue.id: issue
						 for issue
						 in instance}

		data_mapping = {issue['id']: issue
						for issue
						in validated_data}

		result = []
		for issue_id, data in data_mapping.items():
			issue = issue_mapping.get(issue_id, None)

			if issue is None:
				continue

			result.append(self.child.update(issue, validated_data))

		return result


class IssueChildOrderingSerializer(WorkspaceModelSerializer):
	"""
	We use this serializer for update ordering for any amount of issues.
	Order is the same for any presence (backlog, sprint).
	"""

	def update(self, instance, validated_data):
		# @todo Refactor to bulk update. But check signals first !!!
		instance.ordering = [validated_datum['ordering']
							 for validated_datum
							 in validated_data
							 if validated_datum['id'] == instance.id].pop()
		instance.save()

		return instance

	class Meta:
		model = Issue
		fields = (
			'id',
			'ordering'
		)
		extra_kwargs = {
			'id': {'read_only': False},
		}
		list_serializer_class = IssueListSerializer
