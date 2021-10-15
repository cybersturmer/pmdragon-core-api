from django.contrib.auth.models import User
from django.test import TestCase
from .models import Person, Workspace, Project


class BaseModelTesting(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username='test',
			first_name='First Name',
			last_name='Last Name',
			email='test@test.com',
			is_staff=False,
			is_active=True
		)

		self.person = Person \
			.objects \
			.create(
				user=self.user,
				phone='+99999999999'
			)

		self.workspace = Workspace \
			.objects \
			.create(
				prefix_url='test',
				owned_by=self.person
			)

		self.workspace.participants.add(self.person)

		self.project = Project \
			.objects \
			.create(
				workspace=self.workspace,
				title='TEST',
				key='TST',
				owned_by=self.person
			)


class PersonModelTesting(BaseModelTesting):
	def test_model_instance(self):
		self.assertTrue(isinstance(self.person, Person))

	def test_model_username(self):
		self.assertEqual(self.user.username, self.person.username)

	def test_model_first_name(self):
		self.assertEqual(self.user.first_name, self.person.first_name)

	def test_model_last_name(self):
		self.assertEqual(self.user.last_name, self.person.last_name)

	def test_model_title(self):
		self.assertEqual(
			f'{self.user.first_name} {self.user.last_name}',
			f'{self.person.first_name} {self.person.last_name}'
		)

	def test_model_email(self):
		self.assertEqual(
			self.user.email,
			self.person.email
		)

	def test_model_is_active(self):
		self.assertEqual(
			self.user.is_active,
			self.person.is_active
		)

	def test_model_created_at(self):
		self.assertEqual(
			self.user.date_joined,
			self.person.created_at
		)

	def test_model_last_login(self):
		self.assertEqual(
			self.user.last_login,
			self.person.last_login
		)


class WorkspaceModelTesting(BaseModelTesting):
	def test_model_prefix_url(self):
		self.assertTrue(
			self.workspace.prefix_url,
			'test'
		)

	def test_model_participants(self):
		self.assertIn(
			self.person,
			self.workspace.participants.all()
		)

	def test_model_owned_by(self):
		self.assertEqual(
			self.workspace.owned_by,
			self.person
		)


class ProjectModelTesting(BaseModelTesting):
	def test_model_workspace(self):
		self.assertEqual(
			self.project.workspace,
			self.workspace
		)

	def test_model_title(self):
		self.assertEqual(
			self.project.title,
			'TEST'
		)

	def test_model_key(self):
		self.assertEqual(
			self.project.key,
			'TST'
		)

	def test_model_owned_by(self):
		self.assertEqual(
			self.project.owned_by,
			self.person
		)

# PersonForgotRequest
# PersonRegistrationRequest
# PersonInvitationRequest
# IssueTypeCategoryIcon
# IssueTypeCategory
# IssueStateCategory
# IssueEstimationCategory
# IssueAttachment
# Issue
# IssueHistory
# IssueMessage
# ProjectBacklog
# SprintDuration
# Sprint
# ProjectNonWorkingDay
# ProjectWorkingDays
# SprintEffortsHistory
