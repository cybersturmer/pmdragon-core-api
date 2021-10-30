import datetime
import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.core.models import Person, PersonRegistrationRequest, PersonForgotRequest, Workspace, Project, \
	PersonInvitationRequest, IssueTypeCategoryIcon, IssueStateCategory, IssueEstimationCategory, Issue, \
	IssueTypeCategory, IssueHistory, IssueMessage, ProjectBacklog, SprintDuration, Sprint, ProjectNonWorkingDay, \
	ProjectWorkingDays

from apps.core.tests import data_samples
from apps.core.tests import error_strings
from conf.common import url_aliases

from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class PersonRegistrationRequestTest(APITestCase):
	def test_can_create(self):
		url = reverse(url_aliases.PERSON_REGISTRATION_REQUESTS_LIST)
		data = {
			'email': data_samples.CORRECT_EMAIL,
			'prefix_url': data_samples.CORRECT_PREFIX_URL
		}

		response = self.client.post(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 201)

		json_response = json.loads(response.content)

		self.assertIn(
			'email',
			json_response
		)

		self.assertEqual(
			json_response['email'],
			data_samples.CORRECT_EMAIL
		)

		self.assertIn(
			'prefix_url',
			json_response
		)

		self.assertEqual(
			json_response['prefix_url'],
			data_samples.CORRECT_PREFIX_URL
		)

	def test_can_retrieve(self):
		registration_request = PersonRegistrationRequest \
			.objects \
			.create(
				email=data_samples.CORRECT_EMAIL,
				prefix_url=data_samples.CORRECT_PREFIX_URL
			)

		url = reverse(
			url_aliases.PERSON_REGISTRATION_REQUESTS_DETAIL,
			args=[registration_request.key]
		)

		response = self.client.get(url, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		self.assertIn('email', json_response)
		self.assertIn('prefix_url', json_response)


class PersonForgotRequestTest(APITestCase):
	def test_can_create(self):
		url = reverse(url_aliases.PERSON_FORGOT_REQUEST_LIST)
		data = {
			'email': data_samples.CORRECT_EMAIL
		}

		response = self.client.post(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 201)

		json_response = json.loads(response.content)
		self.assertIn('email', json_response)

	def test_can_retrieve(self):
		request_model_data = PersonForgotRequest \
			.objects \
			.create(email=data_samples.CORRECT_EMAIL)

		url = reverse(
			url_aliases.PERSON_FORGOT_REQUEST_DETAIL,
			args=[request_model_data.key]
		)

		response = self.client.get(url, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)
		self.assertIn(
			'email',
			json_response
		)

		self.assertIn(
			'created_at',
			json_response
		)

		self.assertIn(
			'expired_at',
			json_response
		)


class AuthTests(APITestCase):
	@classmethod
	def setUpTestData(cls):
		user = User \
			.objects \
			.create_user(
				username=data_samples.CORRECT_USERNAME,
				password=data_samples.CORRECT_PASSWORD,
				first_name=data_samples.CORRECT_FIRST_NAME,
				last_name=data_samples.CORRECT_LAST_NAME,
				email=data_samples.CORRECT_EMAIL
			)

		person = Person \
			.objects \
			.create(
				user=user,
				phone=data_samples.CORRECT_PHONE
			)

		cls.user = user
		cls.person = person

	def test_can_get_tokens(self):
		url = reverse(url_aliases.TOKEN_OBTAIN)
		data = {
			'username': data_samples.CORRECT_USERNAME,
			'password': data_samples.CORRECT_PASSWORD
		}

		response = self.client.post(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		self.assertIn('access', json_response)
		self.assertIn('refresh', json_response)

	def test_cant_get_tokens_with_wrong_password(self):
		url = reverse(url_aliases.TOKEN_OBTAIN)
		data = {
			'username': data_samples.CORRECT_USERNAME,
			'password': data_samples.WRONG_PASSWORD
		}

		response = self.client.post(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 401)

		json_response = json.loads(response.content)

		self.assertIn('detail', json_response)
		self.assertEqual(
			json_response['detail'],
			error_strings.NO_ACTIVE_ACCOUNTS_FOUND_FOR_CREDENTIALS_MESSAGE
		)

		self.assertNotIn('access', json_response)
		self.assertNotIn('refresh', json_response)

	def test_can_refresh_tokens(self):
		url = reverse(url_aliases.TOKEN_OBTAIN)
		data = {
			'username': data_samples.CORRECT_USERNAME,
			'password': data_samples.CORRECT_PASSWORD
		}

		response = self.client.post(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		refresh_token = json_response.get('refresh')

		url = reverse(url_aliases.TOKEN_REFRESH)
		data = {
			'refresh': refresh_token
		}

		response = self.client.post(url, data, format='json', follow=True)
		json_response = json.loads(response.content)

		self.assertIn('access', json_response)
		self.assertIn('refresh', json_response)

	def test_cant_refresh_tokens_with_wrong_refresh_token(self):
		url = reverse(url_aliases.TOKEN_REFRESH)
		data = {
			'refresh': data_samples.INCORRECT_REFRESH_TOKEN
		}

		response = self.client.post(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 401)

		json_response = json.loads(response.content)

		self.assertIn('detail', json_response)
		self.assertIn('code', json_response)

		self.assertEqual(
			json_response['detail'],
			error_strings.TOKEN_IS_INVALID_OR_EXPIRED_MESSAGE
		)

		self.assertEqual(
			json_response['code'],
			error_strings.TOKEN_IS_INVALID_OR_EXPIRED_CODE
		)


class APIAuthBaseTestCase(APITestCase):
	"""
	We use this class to extend it when we need
	3 different users, 3 different persons,
	workspace, project and get some methods
	to create standard from instance, patch it
	assert comprehensiveness of standard, and equality
	of request and standard.
	"""
	@classmethod
	def setUpTestData(cls):
		"""
		This user (related person) will be participant of single workspace """
		user = User \
			.objects \
			.create_user(
				username=data_samples.CORRECT_USERNAME,
				email=data_samples.CORRECT_EMAIL,
				password=data_samples.CORRECT_PASSWORD
			)

		person = Person \
			.objects \
			.create(
				user=user,
				phone=data_samples.CORRECT_PHONE
			)

		workspace = Workspace \
			.objects \
			.create(
				prefix_url=data_samples.CORRECT_PREFIX_URL,
				owned_by=person
			)

		project = Project \
			.objects \
			.create(
				workspace=workspace,
				title=data_samples.CORRECT_PROJECT_TITLE_2,
				key=data_samples.CORRECT_PROJECT_KEY_2,
				owned_by=person
			)

		second_participant_user = User \
			.objects \
			.create_user(
				username=data_samples.CORRECT_USERNAME_2,
				email=data_samples.CORRECT_EMAIL_2,
				password=data_samples.CORRECT_PASSWORD
			)

		second_participant_person = Person \
			.objects \
			.create(
				user=second_participant_user
			)

		third_not_participant_user = User \
			.objects \
			.create_user(
				username=data_samples.CORRECT_USERNAME_3,
				email=data_samples.CORRECT_EMAIL_3
			)

		third_not_participant_person = Person \
			.objects \
			.create(
				user=third_not_participant_user
			)

		workspace.participants.add(person)
		workspace.participants.add(second_participant_person)

		cls.workspace = workspace
		cls.project = project

		cls.user = user
		cls.person = person

		cls.second_participant_user = second_participant_user
		cls.second_participant_person = second_participant_person

		cls.third_not_participant_user = third_not_participant_user
		cls.third_not_participant_person = third_not_participant_person

	def assertComprehensivenessByStandard(self, response: dict, standard: dict):
		for key in standard.keys():
			self.assertIn(
				key,
				response
			)

	def assertEqualityByStandard(self, response: dict, standard: dict):
		for key in standard.keys():
			self.assertEqual(
				standard[key],
				response[key],
				msg=key
			)

	def assertResponse(self, response: dict, standard: dict):
		self.assertComprehensivenessByStandard(response, standard)
		self.assertEqualityByStandard(response, standard)

	def create_or_get_instance(self):
		raise NotImplementedError

	def base_can_patch_entity(self, url_alias, data: dict = None, exclude: list = None):
		self.client.force_login(self.user)

		instance = self.create_or_get_instance()

		url = reverse(url_alias, args=[instance.id])

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)
		standard = self.create_standard(instance, patch=data, exclude=exclude)

		self.assertResponse(json_response, standard)

		return json_response

	def base_can_delete_entity(self, url_alias):
		self.client.force_login(self.user)

		instance: models.Model = self.create_or_get_instance()

		url = reverse(url_alias, args=[instance.id])

		response = self.client.delete(url, format='json', follow=True)
		self.assertEqual(response.status_code, 204)

		with self.assertRaises(getattr(instance.__class__, 'DoesNotExist')):
			instance.__class__.objects.get(pk=instance.id)

	@staticmethod
	def _create_standard(instance):
		"""
		We need standard to validate data (http json response)
		This method can create standard by
		"""

		fields = instance._meta.get_fields()
		result = {}

		for field in fields:
			# Lets check that model contain field
			if not hasattr(instance, field.name):
				continue

			# Here we sure that model contain field,
			# but dont know is it field or relation to another model

			attribute = getattr(instance, field.name)

			# If this value is a primitive type
			is_primitive = type(attribute) in [int, str, None, datetime.datetime, datetime.date]

			# Ot maybe that's model.
			is_model = issubclass(type(attribute), models.Model)

			# Models have instance.attribute_id for foreign keys
			foreign_key_field = f'{field.name}_id'

			# That's decision tree to understand what type is our field value
			decision_tree = {
				is_primitive: attribute if type(attribute) != datetime.datetime else attribute.utcnow().isoformat(),
				is_model: getattr(instance, foreign_key_field) if hasattr(instance, foreign_key_field) else None
			}

			if decision_tree.get(True):
				result[field.name] = decision_tree.get(True)

		return result

	@staticmethod
	def _patch_standard(standard: dict, patch: dict):
		result = standard.copy()

		for key in patch.keys():
			result[key] = patch[key]

		return result

	@staticmethod
	def _exclude_from_standard(standard: dict, exclude: list):
		for key in exclude:
			del standard[key]

		return standard

	def create_standard(self, instance, patch: dict = None, exclude: list = None):
		standard = self._create_standard(instance)

		if patch is not None:
			standard = self._patch_standard(standard, patch)

		if exclude is not None:
			standard = self._exclude_from_standard(standard, exclude)

		return standard


class WorkspaceTest(APIAuthBaseTestCase):
	def create_or_get_instance(self):
		return self.workspace

	def test_can_get_detail(self):
		self.client.force_login(self.user)

		url = reverse(url_aliases.WORKSPACES_DETAIL, args=[self.workspace.id])

		response = self.client.get(url, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		standard = {
			'id': self.workspace.id,
			'prefix_url': self.workspace.prefix_url,
			'participants': [self.second_participant_person.id, self.person.id]
		}

		self.assertResponse(json_response, standard)

	def test_cant_get_detail_without_credentials(self):
		url = reverse(url_aliases.WORKSPACES_DETAIL, args=[self.workspace.id])

		response = self.client.get(url, format='json', follow=True)
		self.assertEqual(response.status_code, 401)

		json_response = json.loads(response.content)

		self.assertIn(
			'detail',
			json_response
		)

		self.assertEqual(
			error_strings.NO_AUTH_CREDENTIALS_MESSAGE,
			json_response['detail']
		)

	def test_can_get_list(self):
		self.client.force_login(self.user)

		url = reverse(url_aliases.WORKSPACES_LIST)

		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		self.assertIsInstance(json_response, list)

		self.assertEqual(
			len(json_response),
			1
		)

	def test_cant_get_list_without_credentials(self):
		url = reverse(url_aliases.WORKSPACES_LIST)

		response = self.client.get(url, format='json', follow=True)
		self.assertEqual(response.status_code, 401)

		json_response = json.loads(response.content)

		self.assertIn(
			'detail',
			json_response
		)

		self.assertEqual(
			error_strings.NO_AUTH_CREDENTIALS_MESSAGE,
			json_response['detail']
		)


class ProjectTest(APIAuthBaseTestCase):
	def create_or_get_instance(self):
		return self.project

	def test_can_create(self):
		self.client.force_login(self.user)

		url = reverse(url_aliases.PROJECTS_LIST)
		data = {
			'workspace': self.workspace.id,
			'title': data_samples.CORRECT_PROJECT_TITLE,
			'key': data_samples.CORRECT_PROJECT_KEY,
			'owned_by': self.person.id
		}

		response = self.client.post(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 201)

		json_response = json.loads(response.content)
		self.assertResponse(json_response, data)

	def test_can_retrieve(self):
		self.client.force_login(self.user)

		url = reverse(url_aliases.PROJECTS_DETAIL, args=[self.project.id])

		response = self.client.get(url, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		standard = self.create_standard(instance=self.project, exclude=['created_at'])

		self.assertResponse(json_response, standard)

	def test_can_patch_title(self):
		self.base_can_patch_entity(
			url_alias=url_aliases.PROJECTS_DETAIL,
			data={'title': data_samples.CORRECT_PROJECT_TITLE_3},
			exclude=['created_at']
		)

	def test_can_patch_key(self):
		self.base_can_patch_entity(
			url_alias=url_aliases.PROJECTS_DETAIL,
			data={'key': data_samples.CORRECT_PROJECT_KEY_3},
			exclude=['created_at']
		)

	def test_can_patch_owner_by(self):
		self.base_can_patch_entity(
			url_alias=url_aliases.PROJECTS_DETAIL,
			data={'owned_by': self.second_participant_person.id},
			exclude=['created_at']
		)

	def test_cant_patch_owner_by_to_not_participant(self):
		self.client.force_login(self.user)

		url = reverse(url_aliases.PROJECTS_DETAIL, args=[self.project.id])
		data = {
			'owned_by': self.third_not_participant_person.id
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 400)

		json_response = json.loads(response.content)

		standard = {
			'owned_by': [error_strings.OWNER_IS_ONLY_PARTICIPANT_MESSAGE]
		}

		self.assertResponse(json_response, standard)

	def test_cant_patch_owner_by_not_owner(self):
		self.client.force_login(self.second_participant_user)

		url = reverse(url_aliases.PROJECTS_DETAIL, args=[self.project.id])
		data = {
			'owned_by': self.third_not_participant_person.id
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 403)

		json_response = json.loads(response.content)

		standard = {
			'detail': error_strings.YOU_DONT_HAVE_PERMISSION_ON_ACTION_MESSAGE
		}

		self.assertResponse(json_response, standard)

	def test_cant_patch_owner_by_by_not_participant(self):
		"""
		Not participants cant see workspace, so cant' change it
		"""
		self.client.force_login(self.third_not_participant_user)

		url = reverse(url_aliases.PROJECTS_DETAIL, args=[self.project.id])
		data = {
			'owned_by': self.third_not_participant_person.id
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 404)

		json_response = json.loads(response.content)

		standard = {
			'detail': error_strings.NOT_FOUND
		}

		self.assertResponse(json_response, standard)


class PersonInvitationRequestsTest(APIAuthBaseTestCase):
	def create_or_get_instance(self):
		return PersonInvitationRequest\
			.objects\
			.create(
				email=self.third_not_participant_person.email,
				workspace=self.workspace.id
			)

	def test_can_create(self):
		self.client.force_login(self.user)

		url = reverse(url_aliases.PERSON_INVITATIONS_REQUESTS_LIST)
		data = {
			'invitees': [
				{
					'email': self.third_not_participant_person.email,
					'workspace': self.workspace.id,
				}
			],
		}

		response = self.client.post(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 201)

		json_response = json.loads(response.content)

		self.assertEqual(
			1,
			len(json_response)
		)

		json_response_first_slice = json_response[0]

		standard = {
			'email': self.third_not_participant_person.email,
			'workspace': self.workspace.id,
		}

		self.assertIn(
			'created_at',
			json_response_first_slice
		)

		self.assertIn(
			'expired_at',
			json_response_first_slice
		)

		self.assertResponse(json_response_first_slice, standard)

	def test_can_retrieve(self):
		self.client.force_login(self.user)

		person_invitation_request = PersonInvitationRequest \
			.objects \
			.create(
				workspace=self.workspace,
				email=self.third_not_participant_person.email,
			)

		url = reverse(
			url_aliases.PERSON_INVITATIONS_REQUESTS_DETAIL,
			args=[person_invitation_request.key]
		)

		response = self.client.get(url, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		standard = {
			'workspace': self.workspace.id,
			'email': self.third_not_participant_person.email
		}

		self.assertComprehensivenessByStandard(json_response, standard)

	def test_can_be_accepted(self):
		self.client.force_login(self.user)

		person_invitation_request = PersonInvitationRequest \
			.objects \
			.create(
				workspace=self.workspace,
				email=self.third_not_participant_person.email,
			)

		url = reverse(
			url_aliases.PERSON_INVITATIONS_REQUESTS_DETAIL,
			args=[person_invitation_request.key]
		)
		data = {
			'is_accepted': True
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		standard_comprehensiveness = {
			'email': self.third_not_participant_person.email,
			'workspace': self.workspace,
		}

		self.assertComprehensivenessByStandard(json_response, standard_comprehensiveness)

		self.assertIn(
			'email',
			json_response
		)

		self.assertIn(
			'workspace',
			json_response
		)

		self.assertIn(
			self.person.id,
			json_response['workspace']['participants']
		)

		self.assertIn(
			self.second_participant_person.id,
			json_response['workspace']['participants']
		)

		self.assertIn(
			self.third_not_participant_person.id,
			json_response['workspace']['participants']
		)


class IssueTypeCategoryIconTest(APIAuthBaseTestCase):
	def create_or_get_instance(self):
		return IssueTypeCategoryIcon \
			.objects \
			.create(
				workspace=self.workspace,
				project=self.project,
				prefix=data_samples.CORRECT_ICON_CATEGORY_PREFIX,
				color=data_samples.CORRECT_COLOR
			)

	def test_can_create(self):
		self.client.force_login(self.user)

		url = reverse(url_aliases.ISSUE_TYPE_ICONS_LIST)
		data = {
			'workspace': self.workspace.id,
			'project': self.project.id,
			'prefix': data_samples.CORRECT_ICON_CATEGORY_PREFIX,
			'color': data_samples.CORRECT_COLOR
		}

		response = self.client.post(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 201)

		json_response = json.loads(response.content)

		self.assertResponse(json_response, data)

	def test_retrieve(self):
		self.client.force_login(self.user)

		issue_type_icon = self.create_or_get_instance()

		url = reverse(url_aliases.ISSUE_TYPE_ICONS_DETAIL, args=[issue_type_icon.id])

		response = self.client.get(url, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		standard = self._create_standard(issue_type_icon)

		self.assertResponse(json_response, standard)

	def test_can_patch_prefix(self):
		self.base_can_patch_entity(
			url_alias=url_aliases.ISSUE_TYPE_ICONS_DETAIL,
			data={'prefix': data_samples.CORRECT_ICON_CATEGORY_PREFIX_2}
		)

	def test_can_patch_color(self):
		self.base_can_patch_entity(
			url_alias=url_aliases.ISSUE_TYPE_ICONS_DETAIL,
			data={'color': data_samples.CORRECT_COLOR_RED}
		)

	def test_can_delete(self):
		self.base_can_delete_entity(
			url_aliases.ISSUE_TYPE_ICONS_DETAIL
		)


class IssueStateCategoryTest(APIAuthBaseTestCase):
	def create_or_get_instance(self):
		return IssueStateCategory \
			.objects \
			.create(
				workspace=self.workspace,
				project=self.project,
				title=data_samples.CORRECT_ISSUE_STATE_TITLE,
				is_default=False,
				is_done=False
			)

	def test_can_create(self):
		self.client.force_login(self.user)

		url = reverse(url_aliases.ISSUE_STATES_LIST)
		data = {
			'workspace': self.workspace.id,
			'project': self.project.id,
			'title': data_samples.CORRECT_ISSUE_STATE_TITLE,
			'is_default': False,
			'is_done': False
		}

		response = self.client.post(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 201)

		json_response = json.loads(response.content)

		self.assertResponse(json_response, data)

	def test_can_retrieve(self):
		self.client.force_login(self.user)

		issue_state_category = self.create_or_get_instance()

		url = reverse(url_aliases.ISSUE_STATES_DETAIL, args=[issue_state_category.id])

		response = self.client.get(url, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		standard = self._create_standard(issue_state_category)

		self.assertResponse(json_response, standard)

	def test_can_patch_title(self):
		self.base_can_patch_entity(
			url_alias=url_aliases.ISSUE_STATES_DETAIL,
			data={'title': data_samples.CORRECT_ISSUE_STATE_TITLE_2}
		)

	def test_can_patch_is_default(self):
		self.base_can_patch_entity(
			url_alias=url_aliases.ISSUE_STATES_DETAIL,
			data={'is_default': True}
		)

	def test_can_patch_is_done(self):
		self.base_can_patch_entity(
			url_alias=url_aliases.ISSUE_STATES_DETAIL,
			data={'is_done': True}
		)

	def test_can_delete(self):
		self.base_can_delete_entity(
			url_aliases.ISSUE_STATES_DETAIL
		)


class EstimationCategoryTest(APIAuthBaseTestCase):
	def create_or_get_instance(self):
		return IssueEstimationCategory \
			.objects \
			.create(
				workspace=self.workspace,
				project=self.project,
				title=data_samples.CORRECT_ISSUE_ESTIMATION_TITLE,
				value=data_samples.CORRECT_ISSUE_ESTIMATION_VALUE
			)

	def test_can_create(self):
		self.client.force_login(self.user)

		url = reverse(url_aliases.ISSUE_ESTIMATIONS_LIST)
		data = {
			'workspace': self.workspace.id,
			'project': self.project.id,
			'title': data_samples.CORRECT_ISSUE_ESTIMATION_TITLE,
			'value': data_samples.CORRECT_ISSUE_ESTIMATION_VALUE
		}

		response = self.client.post(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 201)

		json_response = json.loads(response.content)

		self.assertResponse(json_response, data)

	def test_can_retrieve(self):
		self.client.force_login(self.user)

		issue_estimation_category = self.create_or_get_instance()

		url = reverse(url_aliases.ISSUE_ESTIMATIONS_DETAIL, args=[issue_estimation_category.id])

		response = self.client.get(url, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		standard = self.create_standard(issue_estimation_category, exclude=[
			'created_at',
			'updated_at',
		])

		self.assertResponse(json_response, standard)

	def test_can_patch_title(self):
		self.base_can_patch_entity(
			url_alias=url_aliases.ISSUE_ESTIMATIONS_DETAIL,
			data={'title': data_samples.CORRECT_ISSUE_ESTIMATION_TITLE_2},
			exclude=['created_at', 'updated_at']
		)

	def test_can_patch_value(self):
		self.base_can_patch_entity(
			url_alias=url_aliases.ISSUE_ESTIMATIONS_DETAIL,
			data={'value': data_samples.CORRECT_ISSUE_ESTIMATION_VALUE_2},
			exclude=['created_at', 'updated_at']
		)

	def test_can_delete(self):
		self.base_can_delete_entity(
			url_aliases.ISSUE_ESTIMATIONS_DETAIL
		)


class IssueBasedTest(APIAuthBaseTestCase):
	project = None
	workspace = None

	def create_or_get_instance(self):
		return Issue \
			.objects \
			.create(
				workspace=self.workspace,
				project=self.project,
				title=data_samples.CORRECT_ISSUE_TITLE,
				description=data_samples.CORRECT_ISSUE_DESCRIPTION,
				type_category=self.type_category,
				state_category=self.state_category,
				estimation_category=self.estimation_category,
				assignee=self.person
			)

	@classmethod
	def setUpTestData(cls):
		super().setUpTestData()

		issue_type_category_icon = IssueTypeCategoryIcon \
			.objects \
			.create(
				workspace=cls.workspace,
				project=cls.project,
				prefix=data_samples.CORRECT_ICON_CATEGORY_PREFIX_2,
				color=data_samples.CORRECT_COLOR_RED
			)

		issue_type_category = IssueTypeCategory \
			.objects \
			.filter(
				workspace=cls.workspace,
				project=cls.project,
				is_default=True) \
			.get()

		issue_state_category = IssueStateCategory \
			.objects \
			.filter(
				workspace=cls.workspace,
				project=cls.project,
				is_default=True
			) \
			.get()

		estimation_category = IssueEstimationCategory \
			.objects \
			.filter(
				workspace=cls.workspace,
				project=cls.project
			) \
			.first()

		cls.type_category_icon = issue_type_category_icon
		cls.type_category = issue_type_category
		cls.state_category = issue_state_category
		cls.estimation_category = estimation_category


class IssueTest(IssueBasedTest):
	def test_can_create(self):
		self.client.force_login(self.user)

		url = reverse(url_aliases.ISSUES_LIST)
		data = {
			'workspace': self.workspace.id,
			'project': self.project.id,
			'title': data_samples.CORRECT_ISSUE_TITLE,
			'description': data_samples.CORRECT_ISSUE_DESCRIPTION,
			'type_category': self.type_category.id,
			'state_category': self.state_category.id,
			'estimation_category': self.estimation_category.id,
			'assignee': self.person.id
		}

		response = self.client.post(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 201)

		json_response = json.loads(response.content)

		self.assertResponse(json_response, data)

	def test_can_patch_title(self):
		self.base_can_patch_entity(
			url_alias=url_aliases.ISSUES_DETAIL,
			data={'title': data_samples.CORRECT_ISSUE_TITLE_2},
			exclude=['created_at', 'updated_at']
		)

	def test_can_patch_description(self):
		self.base_can_patch_entity(
			url_alias=url_aliases.ISSUES_DETAIL,
			data={'title': data_samples.CORRECT_ISSUE_DESCRIPTION_2},
			exclude=['created_at', 'updated_at']
		)

	def test_can_patch_type_category(self):
		another_type_category = IssueTypeCategory \
			.objects \
			.filter(
				workspace=self.workspace,
				project=self.project,
				is_default=False
			) \
			.first()

		self.base_can_patch_entity(
			url_alias=url_aliases.ISSUES_DETAIL,
			data={'type_category': another_type_category.id},
			exclude=['created_at', 'updated_at']
		)

	def test_can_patch_state_category(self):
		another_state_category = IssueStateCategory \
			.objects \
			.filter(
				workspace=self.workspace,
				project=self.project,
				is_default=False
			) \
			.first()

		self.base_can_patch_entity(
			url_alias=url_aliases.ISSUES_DETAIL,
			data={'state_category': another_state_category.id},
			exclude=['created_at', 'updated_at']
		)

	def test_can_patch_estimation_category(self):
		another_estimation_category = IssueEstimationCategory \
			.objects \
			.filter(
				workspace=self.workspace,
				project=self.project
			). \
			last()

		self.base_can_patch_entity(
			url_alias=url_aliases.ISSUES_DETAIL,
			data={'estimation_category': another_estimation_category.id},
			exclude=['created_at', 'updated_at']
		)

	def test_can_patch_assignee(self):
		self.base_can_patch_entity(
			url_alias=url_aliases.ISSUES_DETAIL,
			data={'assignee': self.second_participant_person.id},
			exclude=['created_at', 'updated_at']
		)

	def test_can_patch_ordering(self):
		self.base_can_patch_entity(
			url_alias=url_aliases.ISSUES_DETAIL,
			data={'ordering': data_samples.CORRECT_ISSUE_ORDERING_2},
			exclude=['created_at', 'updated_at']
		)

	def test_can_delete(self):
		self.base_can_delete_entity(
			url_aliases.ISSUES_DETAIL
		)


class IssueHistoryTest(IssueBasedTest):
	def create_or_get_instance(self):
		issue = super().create_or_get_instance()

		return IssueHistory \
			.objects \
			.filter(
				issue=issue
			) \
			.get()

	def test_can_get_issue_filtered_list(self):
		self.client.force_login(self.user)

		issue_history_entry: IssueHistory = self.create_or_get_instance()

		url = reverse(url_aliases.ISSUES_HISTORY_LIST)
		url_with_filter = f'{url}?issue={issue_history_entry.issue.id}'

		response = self.client.get(url_with_filter, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)
		json_response_first_slice = json_response[0]

		standard = self.create_standard(issue_history_entry, exclude=[
			'issue',
			'created_at',
			'updated_at'
		])

		self.assertResponse(json_response_first_slice, standard)

	def test_cant_get_issue_filtered_list_without_credentials(self):
		issue_history_entry: IssueHistory = self.create_or_get_instance()

		url = reverse(url_aliases.ISSUES_HISTORY_LIST)
		url_with_filter = f'{url}?issue={issue_history_entry.issue.id}'

		response = self.client.get(url_with_filter, format='json', follow=True)
		self.assertEqual(response.status_code, 401)

		json_response = json.loads(response.content)

		self.assertEqual(
			error_strings.NO_AUTH_CREDENTIALS_MESSAGE,
			json_response['detail']
		)

	def test_cant_get_issue_filtered_list_for_not_participant(self):
		self.client.force_login(self.third_not_participant_user)

		issue_history_entry: IssueHistory = self.create_or_get_instance()

		url = reverse(url_aliases.ISSUES_HISTORY_LIST)
		url_with_filter = f'{url}?issue={issue_history_entry.issue.id}'

		response = self.client.get(url_with_filter, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		self.assertEqual(
			json_response,
			[]
		)


class IssueMessageTest(APIAuthBaseTestCase):
	def create_or_get_instance(self):
		return IssueMessage.objects.create()


class ProjectBacklogTest(APIAuthBaseTestCase):
	def create_or_get_instance(self):
		return ProjectBacklog.objects.create()


class SprintDurationTest(APIAuthBaseTestCase):
	def create_or_get_instance(self):
		return SprintDuration.objects.create()


class SprintTest(APIAuthBaseTestCase):
	def create_or_get_instance(self):
		return Sprint.objects.create()


class ProjectNonWorkingDaysTest(APIAuthBaseTestCase):
	def create_or_get_instance(self):
		return ProjectNonWorkingDay.objects.create()


class ProjectWorkingDaysTest(APIAuthBaseTestCase):
	def create_or_get_instance(self):
		return ProjectWorkingDays.objects.create()
