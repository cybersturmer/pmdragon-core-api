import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.core.models import Person, PersonRegistrationRequest, PersonForgotRequest, Workspace

SAMPLE_CORRECT_USER_USERNAME = 'test'

SAMPLE_CORRECT_USER_PASSWORD = 'test'
SAMPLE_INCORRECT_USER_PASSWORD = 'no test'

SAMPLE_CORRECT_USER_FIRST_NAME = 'Test'
SAMPLE_CORRECT_USER_LAST_NAME = 'Test'
SAMPLE_CORRECT_USER_EMAIL = 'cybersturmer@ya.ru'
SAMPLE_CORRECT_USER_PHONE = '+79999999999'
SAMPLE_CORRECT_PREFIX_URL = 'TEST'

SAMPLE_INCORRECT_REFRESH_TOKEN = 'INCORRECT REFRESH_TOKEN'


class PersonRegistrationRequestTest(APITestCase):
	def test_can_create(self):
		url = reverse('request-register_create')
		data = {
			'email': SAMPLE_CORRECT_USER_EMAIL,
			'prefix_url': SAMPLE_CORRECT_PREFIX_URL
		}

		response = self.client.post(url, data, format='json', follow=True)
		self.assertEqual(
			response.status_code,
			201
		)

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

		get_registration_request_url = reverse(
			'request-register_retrieve',
			args=[registration_request.key]
		)

		response = self.client.get(get_registration_request_url, format='json', follow=True)
		json_response = json.loads(response.content)

		self.assertEqual(
			response.status_code, 200
		)

		self.assertIn('email', json_response)
		self.assertIn('prefix_url', json_response)


class PersonForgotRequestTest(APITestCase):
	def test_can_create(self):
		url = reverse('request-forgot_create')
		data = {
			'email': SAMPLE_CORRECT_USER_EMAIL
		}

		response = self.client.post(url, data, format='json', follow=True)
		self.assertEqual(
			response.status_code,
			201
		)

		json_response = json.loads(response.content)
		self.assertIn('email', json_response)

	def test_can_retrieve(self):
		request_model_data = PersonForgotRequest \
			.objects \
			.create(email=SAMPLE_CORRECT_USER_EMAIL)

		url = reverse(
			'request-forgot_actions',
			args=[request_model_data.key]
		)

		response = self.client.get(url, format='json', follow=True)
		self.assertEqual(
			response.status_code,
			200
		)

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
	def setUp(self) -> None:
		self.user = User \
			.objects \
			.create_user(
				username=SAMPLE_CORRECT_USER_USERNAME,
				password=SAMPLE_CORRECT_USER_PASSWORD,
				first_name=SAMPLE_CORRECT_USER_FIRST_NAME,
				last_name=SAMPLE_CORRECT_USER_LAST_NAME,
				is_staff=False,
				is_active=True,
				email=SAMPLE_CORRECT_USER_EMAIL
			)

		self.person = Person \
			.objects \
			.create(
				user=self.user,
				phone=SAMPLE_CORRECT_USER_PHONE
			)

	def test_can_get_tokens(self):
		url = reverse('token_obtain_pair')
		data = {
			'username': SAMPLE_CORRECT_USER_USERNAME,
			'password': SAMPLE_CORRECT_USER_PASSWORD
		}

		response = self.client.post(url, data, format='json', follow=True)
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
	def setUp(self):
		super().setUp()

		self.user = User \
			.objects \
			.create_user(
				username=SAMPLE_CORRECT_USER_USERNAME,
				email=SAMPLE_CORRECT_USER_EMAIL,
				password=SAMPLE_CORRECT_USER_PASSWORD
			)

		self.person = Person \
			.objects \
			.create(
				user=self.user,
				phone=SAMPLE_CORRECT_USER_PHONE
			)

		self.workspace = Workspace \
			.objects \
			.create(
				prefix_url=SAMPLE_CORRECT_PREFIX_URL,
				owned_by=self.person
			)

		self.workspace.participants.add(self.person)


class WorkspaceTest(APIAuthBaseTestCase):
	def test_can_retrieve(self):
		self.client.force_login(self.user)

		url = reverse('core_api:workspaces-detail', kwargs={'pk': self.workspace.id})

		response = self.client.get(url, format='json', follow=True)

		self.assertEqual(
			response.status_code,
			200
		)

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
			[self.person.id]
		)

