import datetime
import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.core.models import Person, PersonRegistrationRequest, PersonForgotRequest, Workspace, Project, \
	PersonInvitationRequest, IssueTypeCategoryIcon, IssueStateCategory, IssueEstimationCategory, Issue, \
	IssueTypeCategory

from apps.core.tests import data_samples
from apps.core.tests import error_strings
from conf.common import url_aliases


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
	@classmethod
	def setUpTestData(cls):
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
				response[key]
			)

	def assertResponse(self, response: dict, standard: dict):
		self.assertComprehensivenessByStandard(response, standard)
		self.assertEqualityByStandard(response, standard)


class WorkspaceTest(APIAuthBaseTestCase):
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

		standard = {
			'id': self.project.id,
			'workspace': self.workspace.id,
			'title': self.project.title,
			'key': self.project.key,
			'owned_by': self.project.owned_by_id
		}

		self.assertResponse(json_response, standard)

	def test_can_patch_title(self):
		self.client.force_login(self.user)

		url = reverse(url_aliases.PROJECTS_DETAIL, args=[self.project.id])
		data = {
			'title': data_samples.CORRECT_PROJECT_TITLE_3
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		self.assertResponse(json_response, data)

	def test_can_patch_key(self):
		self.client.force_login(self.user)

		url = reverse(url_aliases.PROJECTS_DETAIL, args=[self.project.id])
		data = {
			'key': data_samples.CORRECT_PROJECT_KEY_3
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		self.assertResponse(json_response, data)

	def test_can_patch_owner_by(self):
		self.client.force_login(self.user)

		url = reverse(url_aliases.PROJECTS_DETAIL, args=[self.project.id])
		data = {
			'owned_by': self.second_participant_person.id
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		self.assertResponse(json_response, data)

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
	def create_instance(self):
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

		standard = {
			'workspace': self.workspace.id,
			'project': self.project.id,
			'prefix': data_samples.CORRECT_ICON_CATEGORY_PREFIX,
			'color': data_samples.CORRECT_COLOR
		}

		self.assertResponse(json_response, standard)

	def test_retrieve(self):
		self.client.force_login(self.user)

		issue_type_icon = self.create_instance()

		url = reverse(url_aliases.ISSUE_TYPE_ICONS_DETAIL, args=[issue_type_icon.id])

		response = self.client.get(url, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		standard = {
			'workspace': issue_type_icon.workspace_id,
			'project': issue_type_icon.project_id,
			'prefix': issue_type_icon.prefix,
			'color': issue_type_icon.color
		}

		self.assertResponse(json_response, standard)

	def test_can_patch_prefix(self):
		self.client.force_login(self.user)

		issue_type_icon = self.create_instance()

		url = reverse(url_aliases.ISSUE_TYPE_ICONS_DETAIL, args=[issue_type_icon.id])
		data = {
			'prefix': data_samples.CORRECT_ICON_CATEGORY_PREFIX_2
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		standard = {
			'workspace': issue_type_icon.workspace_id,
			'project': issue_type_icon.project_id,
			'prefix': data_samples.CORRECT_ICON_CATEGORY_PREFIX_2,
			'color': issue_type_icon.color
		}

		self.assertResponse(json_response, standard)

	def test_can_patch_color(self):
		self.client.force_login(self.user)

		issue_type_icon = self.create_instance()

		url = reverse(url_aliases.ISSUE_TYPE_ICONS_DETAIL, args=[issue_type_icon.id])
		data = {
			'color': data_samples.CORRECT_COLOR_RED
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		standard = {
			'workspace': issue_type_icon.workspace_id,
			'project': issue_type_icon.project_id,
			'prefix': issue_type_icon.prefix,
			'color': data_samples.CORRECT_COLOR_RED
		}

		self.assertResponse(json_response, standard)

	def test_can_delete(self):
		self.client.force_login(self.user)

		issue_type_icon = self.create_instance()

		url = reverse(url_aliases.ISSUE_TYPE_ICONS_DETAIL, args=[issue_type_icon.id])

		response = self.client.delete(url, format='json', follow=True)
		self.assertEqual(response.status_code, 204)

		with self.assertRaises(IssueTypeCategoryIcon.DoesNotExist):
			IssueTypeCategoryIcon.objects.get(pk=issue_type_icon.id)


class IssueStateCategoryTest(APIAuthBaseTestCase):
	def create_instance(self):
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

		issue_state_category = self.create_instance()

		url = reverse(url_aliases.ISSUE_STATES_DETAIL, args=[issue_state_category.id])

		response = self.client.get(url, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)
		standard = {
			'workspace': issue_state_category.workspace_id,
			'project': issue_state_category.project_id,
			'title': issue_state_category.title,
			'is_default': issue_state_category.is_default,
			'is_done': issue_state_category.is_done
		}

		self.assertResponse(json_response, standard)

	def test_can_patch_title(self):
		self.client.force_login(self.user)

		issue_state_category = self.create_instance()

		url = reverse(url_aliases.ISSUE_STATES_DETAIL, args=[issue_state_category.id])
		data = {
			'title': data_samples.CORRECT_ISSUE_STATE_TITLE_2
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)
		standard = {
			'workspace': issue_state_category.workspace_id,
			'project': issue_state_category.project_id,
			'title': data['title'],
			'is_default': issue_state_category.is_default,
			'is_done': issue_state_category.is_done
		}

		self.assertResponse(json_response, standard)

	def test_can_patch_is_default(self):
		self.client.force_login(self.user)

		issue_state_category = self.create_instance()

		url = reverse(url_aliases.ISSUE_STATES_DETAIL, args=[issue_state_category.id])
		data = {
			'is_default': True
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)
		standard = {
			'workspace': issue_state_category.workspace_id,
			'project': issue_state_category.project_id,
			'title': issue_state_category.title,
			'is_default': data['is_default'],
			'is_done': issue_state_category.is_done
		}

		self.assertResponse(json_response, standard)

	def test_can_patch_is_done(self):
		self.client.force_login(self.user)

		issue_state_category = self.create_instance()

		url = reverse(url_aliases.ISSUE_STATES_DETAIL, args=[issue_state_category.id])
		data = {
			'is_done': True
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)
		standard = {
			'workspace': issue_state_category.workspace_id,
			'project': issue_state_category.project_id,
			'title': issue_state_category.title,
			'is_default': issue_state_category.is_default,
			'is_done': data['is_done']
		}

		self.assertResponse(json_response, standard)

	def test_can_delete(self):
		self.client.force_login(self.user)

		issue_state_category = self.create_instance()

		url = reverse(url_aliases.ISSUE_STATES_DETAIL, args=[issue_state_category.id])

		response = self.client.delete(url, format='json', follow=True)
		self.assertEqual(response.status_code, 204)

		with self.assertRaises(IssueStateCategory.DoesNotExist):
			IssueStateCategory.objects.get(pk=issue_state_category.id)


class EstimationCategoryTest(APIAuthBaseTestCase):
	def create_instance(self):
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

		issue_estimation_category = self.create_instance()

		url = reverse(url_aliases.ISSUE_ESTIMATIONS_DETAIL, args=[issue_estimation_category.id])

		response = self.client.get(url, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)
		standard = {
			'workspace': issue_estimation_category.workspace_id,
			'project': issue_estimation_category.project_id,
			'title': issue_estimation_category.title,
			'value': issue_estimation_category.value
		}

		self.assertResponse(json_response, standard)

	def test_can_patch_title(self):
		self.client.force_login(self.user)

		issue_estimation_category = self.create_instance()

		url = reverse(url_aliases.ISSUE_ESTIMATIONS_DETAIL, args=[issue_estimation_category.id])
		data = {
			'title': data_samples.CORRECT_ISSUE_ESTIMATION_TITLE_2
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)
		standard = {
			'workspace': self.workspace.id,
			'project': self.project.id,
			'title': data_samples.CORRECT_ISSUE_ESTIMATION_TITLE_2,
			'value': data_samples.CORRECT_ISSUE_ESTIMATION_VALUE
		}

		self.assertResponse(json_response, standard)

	def test_can_patch_value(self):
		self.client.force_login(self.user)

		issue_estimation_category = self.create_instance()

		url = reverse(url_aliases.ISSUE_ESTIMATIONS_DETAIL, args=[issue_estimation_category.id])
		data = {
			'value': data_samples.CORRECT_ISSUE_ESTIMATION_VALUE_2
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)
		standard = {
			'workspace': self.workspace.id,
			'project': self.project.id,
			'title': data_samples.CORRECT_ISSUE_ESTIMATION_TITLE,
			'value': data_samples.CORRECT_ISSUE_ESTIMATION_VALUE_2
		}

		self.assertResponse(json_response, standard)

	def test_can_delete(self):
		self.client.force_login(self.user)

		issue_estimation_category = self.create_instance()

		url = reverse(url_aliases.ISSUE_ESTIMATIONS_DETAIL, args=[issue_estimation_category.id])

		response = self.client.delete(url, format='json', follow=True)
		self.assertEqual(response.status_code, 204)

		with self.assertRaises(IssueEstimationCategory.DoesNotExist):
			IssueEstimationCategory.objects.get(pk=issue_estimation_category.id)


class IssueTest(APIAuthBaseTestCase):
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

	def create_instance(self):
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
		self.client.force_login(self.user)

		issue = self.create_instance()

		url = reverse(url_aliases.ISSUES_DETAIL, args=[issue.id])
		data = {
			'title': data_samples.CORRECT_ISSUE_TITLE_2
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)
		standard = {
			'workspace': self.workspace.id,
			'project': self.project.id,
			'title': data['title'],
			'description': data_samples.CORRECT_ISSUE_DESCRIPTION,
			'type_category': self.type_category.id,
			'state_category': self.state_category.id,
			'estimation_category': self.estimation_category.id,
			'assignee': self.person.id
		}

		self.assertResponse(json_response, standard)

	def test_can_patch_description(self):
		self.client.force_login(self.user)

		issue = self.create_instance()

		url = reverse(url_aliases.ISSUES_DETAIL, args=[issue.id])
		data = {
			'title': data_samples.CORRECT_ISSUE_DESCRIPTION_2
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)
		standard = {
			'workspace': self.workspace.id,
			'project': self.project.id,
			'title': data['title'],
			'description': data_samples.CORRECT_ISSUE_DESCRIPTION,
			'type_category': self.type_category.id,
			'state_category': self.state_category.id,
			'estimation_category': self.estimation_category.id,
			'assignee': self.person.id
		}

		self.assertResponse(json_response, standard)
