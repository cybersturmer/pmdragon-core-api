import datetime
import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.core.models import Person, PersonRegistrationRequest, PersonForgotRequest, Workspace, Project

SAMPLE_CORRECT_USER_USERNAME = 'test'
SAMPLE_CORRECT_USER_USERNAME_2 = 'test2'
SAMPLE_CORRECT_USER_USERNAME_3 = 'test3'

SAMPLE_CORRECT_USER_PASSWORD = 'test'
SAMPLE_INCORRECT_USER_PASSWORD = 'no test'

SAMPLE_CORRECT_USER_FIRST_NAME = 'Test'
SAMPLE_CORRECT_USER_LAST_NAME = 'Test'

SAMPLE_CORRECT_USER_EMAIL = 'test1@email.com'
SAMPLE_CORRECT_USER_EMAIL_2 = 'test2@email.com'
SAMPLE_CORRECT_USER_EMAIL_3 = 'test3@email.com'

SAMPLE_CORRECT_USER_PHONE = '+79999999999'
SAMPLE_CORRECT_PREFIX_URL = 'TEST'

SAMPLE_CORRECT_PROJECT_TITLE = 'TEST'
SAMPLE_CORRECT_PROJECT_KEY = 'TST'

SAMPLE_INCORRECT_REFRESH_TOKEN = 'INCORRECT REFRESH_TOKEN'

SAMPLE_NO_AUTH_MESSAGE = 'Authentication credentials were not provided.'


class PersonRegistrationRequestTest(APITestCase):
	def test_can_create(self):
		url = reverse('person-registration-requests-list')
		data = {
			'email': SAMPLE_CORRECT_USER_EMAIL,
			'prefix_url': SAMPLE_CORRECT_PREFIX_URL
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
			SAMPLE_CORRECT_USER_EMAIL
		)

		self.assertIn(
			'prefix_url',
			json_response
		)

		self.assertEqual(
			json_response['prefix_url'],
			SAMPLE_CORRECT_PREFIX_URL
		)

	def test_can_get_created(self):
		registration_request = PersonRegistrationRequest \
			.objects \
			.create(
				email=SAMPLE_CORRECT_USER_EMAIL,
				prefix_url=SAMPLE_CORRECT_PREFIX_URL
			)

		url = reverse(
			'person-registration-requests-detail',
			args=[registration_request.key]
		)

		response = self.client.get(url, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		self.assertIn('email', json_response)
		self.assertIn('prefix_url', json_response)


class PersonForgotRequestTest(APITestCase):
	def test_can_create(self):
		url = reverse('person-forgot-requests-list')
		data = {
			'email': SAMPLE_CORRECT_USER_EMAIL
		}

		response = self.client.post(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 201)

		json_response = json.loads(response.content)
		self.assertIn('email', json_response)

	def test_can_retrieve(self):
		request_model_data = PersonForgotRequest \
			.objects \
			.create(email=SAMPLE_CORRECT_USER_EMAIL)

		url = reverse(
			'person-forgot-requests-detail',
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
				username=SAMPLE_CORRECT_USER_USERNAME,
				password=SAMPLE_CORRECT_USER_PASSWORD,
				first_name=SAMPLE_CORRECT_USER_FIRST_NAME,
				last_name=SAMPLE_CORRECT_USER_LAST_NAME,
				email=SAMPLE_CORRECT_USER_EMAIL
			)

		person = Person \
			.objects \
			.create(
				user=user,
				phone=SAMPLE_CORRECT_USER_PHONE
			)

		cls.user = user
		cls.person = person

	def test_can_get_tokens(self):
		url = reverse('token_obtain_pair')
		data = {
			'username': SAMPLE_CORRECT_USER_USERNAME,
			'password': SAMPLE_CORRECT_USER_PASSWORD
		}

		response = self.client.post(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		self.assertIn('access', json_response)
		self.assertIn('refresh', json_response)

	def test_cant_get_tokens_with_wrong_password(self):
		url = reverse('token_obtain_pair')
		data = {
			'username': SAMPLE_CORRECT_USER_USERNAME,
			'password': SAMPLE_INCORRECT_USER_PASSWORD
		}

		response = self.client.post(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 401)

		json_response = json.loads(response.content)

		self.assertIn('detail', json_response)
		self.assertEqual(
			json_response['detail'],
			'No active account found with the given credentials'
		)

		self.assertNotIn('access', json_response)
		self.assertNotIn('refresh', json_response)

	def test_can_refresh_tokens(self):
		url = reverse('token_obtain_pair')
		data = {
			'username': SAMPLE_CORRECT_USER_USERNAME,
			'password': SAMPLE_CORRECT_USER_PASSWORD
		}

		response = self.client.post(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		refresh_token = json_response.get('refresh')

		url = reverse('token_refresh')
		data = {
			'refresh': refresh_token
		}

		response = self.client.post(url, data, format='json', follow=True)
		json_response = json.loads(response.content)

		self.assertIn('access', json_response)
		self.assertIn('refresh', json_response)

	def test_cant_refresh_tokens_with_wrong_refresh_token(self):
		url = reverse('token_refresh')
		data = {
			'refresh': SAMPLE_INCORRECT_REFRESH_TOKEN
		}

		response = self.client.post(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 401)

		json_response = json.loads(response.content)

		self.assertIn('detail', json_response)
		self.assertIn('code', json_response)

		self.assertEqual(
			json_response['detail'],
			'Token is invalid or expired'
		)

		self.assertEqual(
			json_response['code'],
			'token_not_valid'
		)


class APIAuthBaseTestCase(APITestCase):
	@classmethod
	def setUpTestData(cls):
		user = User \
			.objects \
			.create_user(
				username=SAMPLE_CORRECT_USER_USERNAME,
				email=SAMPLE_CORRECT_USER_EMAIL,
				password=SAMPLE_CORRECT_USER_PASSWORD
			)

		person = Person \
			.objects \
			.create(
				user=user,
				phone=SAMPLE_CORRECT_USER_PHONE
			)

		workspace = Workspace \
			.objects \
			.create(
				prefix_url=SAMPLE_CORRECT_PREFIX_URL,
				owned_by=person
			)

		project = Project \
			.objects \
			.create(
				workspace=workspace,
				title=f'{SAMPLE_CORRECT_PROJECT_TITLE}N',
				key=f'{SAMPLE_CORRECT_PROJECT_KEY}N',
				owned_by=person
			)

		second_participant_user = User \
			.objects \
			.create_user(
				username='another',
				email=SAMPLE_CORRECT_USER_EMAIL_2,
				password='another'
			)

		second_participant_person = Person \
			.objects \
			.create(
				user=second_participant_user
			)

		third_not_participant_user = User \
			.objects \
			.create_user(
				username='third_not_participant_user',
				email=SAMPLE_CORRECT_USER_EMAIL_3
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


class WorkspaceTest(APIAuthBaseTestCase):
	def test_can_get_detail(self):
		self.client.force_login(self.user)

		url = reverse('core_api:workspaces-detail', kwargs={'pk': self.workspace.id})

		response = self.client.get(url, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		self.assertEqual(
			json_response['id'],
			self.workspace.id
		)

		self.assertEqual(
			json_response['prefix_url'],
			self.workspace.prefix_url
		)

		self.assertEqual(
			json_response['participants'],
			[self.second_participant_person.id, self.person.id]
		)

	def test_cant_get_detail_without_credentials(self):
		url = reverse('core_api:workspaces-detail', kwargs={'pk': self.workspace.id})

		response = self.client.get(url, format='json', follow=True)
		self.assertEqual(response.status_code, 401)

		json_response = json.loads(response.content)

		self.assertIn(
			'detail',
			json_response
		)

		self.assertEqual(
			SAMPLE_NO_AUTH_MESSAGE,
			json_response['detail']
		)

	def test_can_get_list(self):
		self.client.force_login(self.user)

		url = reverse('core_api:workspaces-list')

		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		self.assertIsInstance(json_response, list)

		self.assertEqual(
			len(json_response),
			1
		)

	def test_cant_get_list_without_credentials(self):
		url = reverse('core_api:workspaces-list')

		response = self.client.get(url, format='json', follow=True)
		self.assertEqual(response.status_code, 401)

		json_response = json.loads(response.content)

		self.assertIn(
			'detail',
			json_response
		)

		self.assertEqual(
			SAMPLE_NO_AUTH_MESSAGE,
			json_response['detail']
		)


class ProjectTest(APIAuthBaseTestCase):
	def test_can_create(self):
		self.client.force_login(self.user)

		url = reverse('core_api:projects-list')
		data = {
			'workspace': self.workspace.id,
			'title': SAMPLE_CORRECT_PROJECT_TITLE,
			'key': SAMPLE_CORRECT_PROJECT_KEY,
			'owned_by': self.person.id
		}

		response = self.client.post(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 201)

		json_response = json.loads(response.content)

		self.assertIn('id', json_response)
		self.assertIn('workspace', json_response)
		self.assertIn('title', json_response)
		self.assertIn('key', json_response)
		self.assertIn('owned_by', json_response)
		self.assertIn('created_at', json_response)

		self.assertEqual(
			json_response['workspace'],
			self.workspace.id
		)

		self.assertEqual(
			json_response['title'],
			SAMPLE_CORRECT_PROJECT_TITLE
		)

		self.assertEqual(
			json_response['key'],
			SAMPLE_CORRECT_PROJECT_KEY
		)

		self.assertEqual(
			json_response['owned_by'],
			self.person.id
		)

	def test_can_retrieve(self):
		self.client.force_login(self.user)

		url = reverse('core_api:projects-detail', args=[self.project.id])

		response = self.client.get(url, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		self.assertIn('id', json_response)
		self.assertIn('workspace', json_response)
		self.assertIn('title', json_response)
		self.assertIn('key', json_response)
		self.assertIn('owned_by', json_response)
		self.assertIn('created_at', json_response)

		self.assertEqual(
			self.project.id,
			json_response['id']
		)

		self.assertEqual(
			self.project.workspace.id,
			json_response['workspace']
		)

		self.assertEqual(
			self.project.title,
			json_response['title']
		)

		self.assertEqual(
			self.project.key,
			json_response['key']
		)

		self.assertEqual(
			self.project.owned_by.id,
			json_response['owned_by']
		)

	def test_can_patch_title(self):
		self.client.force_login(self.user)

		url = reverse('core_api:projects-detail', args=[self.project.id])
		data = {
			'title': 'NEW TITLE'
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		self.assertIn(
			'title',
			json_response
		)

		self.assertEqual(
			json_response['title'],
			data['title']
		)

	def test_can_patch_key(self):
		self.client.force_login(self.user)

		url = reverse('core_api:projects-detail', args=[self.project.id])
		data = {
			'key': 'NEW'
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		self.assertIn(
			'key',
			json_response
		)

		self.assertEqual(
			json_response['key'],
			data['key']
		)

	def test_can_patch_owner_by(self):
		self.client.force_login(self.user)

		url = reverse('core_api:projects-detail', args=[self.project.id])
		data = {
			'owned_by': self.second_participant_person.id
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 200)

		json_response = json.loads(response.content)

		self.assertIn(
			'owned_by',
			json_response
		)

		self.assertEqual(
			json_response['owned_by'],
			self.second_participant_person.id
		)

	def test_cant_patch_owner_by_to_not_participant(self):
		self.client.force_login(self.user)

		url = reverse('core_api:projects-detail', args=[self.project.id])
		data = {
			'owned_by': self.third_not_participant_person.id
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 400)

		json_response = json.loads(response.content)

		self.assertIn(
			'owned_by',
			json_response
		)

		self.assertIn(
			'You can change owner only to participant of current workspace',
			json_response['owned_by']
		)

	def test_cant_patch_owner_by_not_owner(self):
		self.client.force_login(self.second_participant_user)

		url = reverse('core_api:projects-detail', args=[self.project.id])
		data = {
			'owned_by': self.third_not_participant_person.id
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 403)

		json_response = json.loads(response.content)

		self.assertIn(
			'detail',
			json_response
		)

		self.assertEqual(
			json_response['detail'],
			'You do not have permission to perform this action.'
		)

	def test_cant_patch_owner_by_by_not_participant(self):
		"""
		Not participants cant see workspace, so cant' change it
		"""
		self.client.force_login(self.third_not_participant_user)

		url = reverse('core_api:projects-detail', args=[self.project.id])
		data = {
			'owned_by': self.third_not_participant_person.id
		}

		response = self.client.patch(url, data, format='json', follow=True)
		self.assertEqual(response.status_code, 404)

		json_response = json.loads(response.content)

		self.assertIn(
			'detail',
			json_response
		)

		self.assertEqual(
			'Not found.',
			json_response['detail']
		)


class PersonInvitationRequestTest(APIAuthBaseTestCase):
	def test_can_create(self):
		self.client.force_login(self.user)

		url = reverse('core_api:person-invitations-requests-list')
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
		json_response_first_slice = json_response[0]

		self.assertIn(
			'email',
			json_response_first_slice
		)

		self.assertIn(
			'workspace',
			json_response_first_slice
		)

		self.assertIn(
			'created_at',
			json_response_first_slice
		)

		self.assertIn(
			'expired_at',
			json_response_first_slice
		)

		self.assertEqual(
			self.third_not_participant_person.email,
			json_response_first_slice['email']
		)

		self.assertEqual(
			self.workspace.id,
			json_response_first_slice['workspace']
		)
