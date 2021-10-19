import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.core.models import Person

SAMPLE_CORRECT_USER_USERNAME = 'test'

SAMPLE_CORRECT_USER_PASSWORD = 'test'
SAMPLE_INCORRECT_USER_PASSWORD = 'no test'

SAMPLE_CORRECT_USER_FIRST_NAME = 'Test'
SAMPLE_CORRECT_USER_LAST_NAME = 'Test'
SAMPLE_CORRECT_USER_EMAIL = 'cybersturmer@ya.ru'
SAMPLE_CORRECT_USER_PHONE = '+79999999999'

SAMPLE_INCORRECT_REFRESH_TOKEN = 'INCORRECT REFRESH_TOKEN'


class AuthTests(APITestCase):
	def setUp(self) -> None:
		self.user = User \
			.objects \
			.create(
				username=SAMPLE_CORRECT_USER_USERNAME,
				password=SAMPLE_CORRECT_USER_PASSWORD,
				first_name=SAMPLE_CORRECT_USER_FIRST_NAME,
				last_name=SAMPLE_CORRECT_USER_LAST_NAME,
				is_staff=False,
				is_active=True,
				email=SAMPLE_CORRECT_USER_EMAIL
			)

		self.user.set_password(SAMPLE_CORRECT_USER_PASSWORD)
		self.user.save()

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

		response = json.loads(
			self.client.post(url, data, format='json', follow=True).content
		)

		self.assertIn('access', response)
		self.assertIn('refresh', response)

	def test_cant_get_tokens_with_wrong_password(self):
		url = reverse('token_obtain_pair')
		data = {
			'username': SAMPLE_CORRECT_USER_USERNAME,
			'password': SAMPLE_INCORRECT_USER_PASSWORD
		}

		response = self.client.post(url, data, format='json', follow=True)

		obtain_response = json.loads(response.content)

		self.assertIn('detail', obtain_response)
		self.assertEqual(
			obtain_response['detail'],
			'No active account found with the given credentials'
		)

		self.assertNotIn('access', obtain_response)
		self.assertNotIn('refresh', obtain_response)

	def test_can_refresh_tokens(self):
		url = reverse('token_obtain_pair')
		data = {
			'username': SAMPLE_CORRECT_USER_USERNAME,
			'password': SAMPLE_CORRECT_USER_PASSWORD
		}

		obtain_response = json.loads(
			self.client.post(url, data, format='json', follow=True).content
		)

		refresh_token = obtain_response.get('refresh')

		url = reverse('token_refresh')
		data = {
			'refresh': refresh_token
		}

		refresh_response = json.loads(
			self.client.post(url, data, format='json', follow=True).content
		)

		self.assertIn('access', refresh_response)
		self.assertIn('refresh', refresh_response)

	def test_cant_refresh_tokens_with_wrong_refresh_token(self):
		url = reverse('token_refresh')
		data = {
			'refresh': SAMPLE_INCORRECT_REFRESH_TOKEN
		}

		response = self.client.post(url, data, format='json', follow=True)
		refresh_response = json.loads(response.content)

		self.assertIn('detail', refresh_response)
		self.assertIn('code', refresh_response)

		self.assertEqual(
			refresh_response['detail'],
			'Token is invalid or expired'
		)

		self.assertEqual(
			refresh_response['code'],
			'token_not_valid'
		)
