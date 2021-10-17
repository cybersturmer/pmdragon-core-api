import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from libs.cryptography import hashing
from .models import Person, Workspace, Project, PersonForgotRequest, PersonRegistrationRequest, PersonInvitationRequest, \
	IssueTypeCategoryIcon, IssueTypeCategory, IssueStateCategory, IssueEstimationCategory, Issue, ProjectBacklog, \
	IssueHistory, IssueMessage, Sprint, ProjectNonWorkingDay, ProjectWorkingDays, SprintEffortsHistory

SAMPLE_CORRECT_USERNAME = 'cybersturmer'
SAMPLE_CORRECT_FIRST_NAME = 'Vladimir'
SAMPLE_CORRECT_LAST_NAME = 'Shturmer'
SAMPLE_CORRECT_EMAIL = 'test@test.com'
SAMPLE_CORRECT_PHONE = '+79282412233'
SAMPLE_CORRECT_PREFIX_URL = 'TEST'

SAMPLE_CORRECT_PROJECT_TITLE = 'TEST'
SAMPLE_CORRECT_PROJECT_KEY = 'TST'

SAMPLE_CORRECT_ICON_CATEGORY_PREFIX = 'mdi-bookmark'
SAMPLE_CORRECT_COLOR = '#f02222'

SAMPLE_CORRECT_ISSUE_TYPE_CATEGORY_TITLE = 'User Story'

SAMPLE_CORRECT_ISSUE_TITLE = 'As a user i want to create new issue'
SAMPLE_CORRECT_ISSUE_DESCRIPTION = 'This description is really good'

SAMPLE_CORRECT_ISSUE_MESSAGE_DESCRIPTION = 'Hello, how are you?'

SAMPLE_CORRECT_SPRINT_TITLE = 'Crucial Sprint N15'
SAMPLE_CORRECT_SPRINT_GOAL = 'Do extremely important things.'



class BaseModelTesting(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username=SAMPLE_CORRECT_USERNAME,
			first_name=SAMPLE_CORRECT_FIRST_NAME,
			last_name=SAMPLE_CORRECT_LAST_NAME,
			email=SAMPLE_CORRECT_EMAIL,
			is_staff=False,
			is_active=True
		)

		self.person = Person \
			.objects \
			.create(
				user=self.user,
				phone=SAMPLE_CORRECT_PHONE
			)

		self.workspace = Workspace \
			.objects \
			.create(
				prefix_url=SAMPLE_CORRECT_PREFIX_URL,
				owned_by=self.person
			)

		self.workspace.participants.add(self.person)

		self.project = Project \
			.objects \
			.create(
				workspace=self.workspace,
				title=SAMPLE_CORRECT_PROJECT_TITLE,
				key=SAMPLE_CORRECT_PROJECT_KEY,
				owned_by=self.person
			)

	def tearDown(self) -> None:
		self.workspace.delete()
		self.user.delete()


class PersonModelTesting(BaseModelTesting):
	def test_instance(self):
		self.assertTrue(isinstance(self.person, Person))

	def test_username(self):
		self.assertEqual(self.user.username, self.person.username)

	def test_first_name(self):
		self.assertEqual(self.user.first_name, self.person.first_name)

	def test_last_name(self):
		self.assertEqual(self.user.last_name, self.person.last_name)

	def test_title(self):
		self.assertEqual(
			f'{self.user.first_name} {self.user.last_name}',
			f'{self.person.first_name} {self.person.last_name}'
		)

	def test_email(self):
		self.assertEqual(
			self.user.email,
			self.person.email
		)

	def test_is_active(self):
		self.assertEqual(
			self.user.is_active,
			self.person.is_active
		)

	def test_created_at(self):
		self.assertEqual(
			self.user.date_joined,
			self.person.created_at
		)

	def test_last_login(self):
		self.assertEqual(
			self.user.last_login,
			self.person.last_login
		)


class WorkspaceModelTesting(BaseModelTesting):
	def test_prefix_url(self):
		self.assertTrue(
			self.workspace.prefix_url,
			SAMPLE_CORRECT_PREFIX_URL
		)

	def test_participants(self):
		self.assertIn(
			self.person,
			self.workspace.participants.all()
		)

	def test_owned_by(self):
		self.assertEqual(
			self.workspace.owned_by,
			self.person
		)


class ProjectModelTesting(BaseModelTesting):
	def test_workspace(self):
		self.assertEqual(
			self.project.workspace,
			self.workspace
		)

	def test_title(self):
		self.assertEqual(
			self.project.title,
			SAMPLE_CORRECT_PROJECT_TITLE
		)

	def test_key(self):
		self.assertEqual(
			self.project.key,
			SAMPLE_CORRECT_PROJECT_KEY
		)

	def test_owned_by(self):
		self.assertEqual(
			self.project.owned_by,
			self.person
		)

	def test_backlog_was_created(self):
		backlog = ProjectBacklog \
			.objects \
			.filter(
				workspace=self.workspace,
				project=self.project
			) \
			.get()

		self.assertTrue(isinstance(backlog, ProjectBacklog))

	def test_default_issue_type_category_icons_were_created(self):
		issue_type_category_icons_count = IssueTypeCategoryIcon \
			.objects \
			.filter(
				workspace=self.workspace,
				project=self.project
			) \
			.count()

		self.assertEqual(issue_type_category_icons_count, 4)

	def test_default_issue_type_category_were_created(self):
		issue_type_category_count = IssueTypeCategory\
			.objects \
			.filter(
				workspace=self.workspace,
				project=self.project
			) \
			.count()

		self.assertEqual(issue_type_category_count, 4)


class PersonForgotRequestModelTesting(BaseModelTesting):
	def setUp(self):
		super().setUp()
		self.forgot_request = PersonForgotRequest \
			.objects \
			.create(
				email=SAMPLE_CORRECT_EMAIL
			)

	def test_key(self):
		self.assertEqual(
			hashing.get_hash(self.forgot_request.expired_at, self.forgot_request.email),
			self.forgot_request.key
		)

	def test_is_email_sent_by_default(self):
		self.assertFalse(self.forgot_request.is_email_sent)

	def test_is_accepted_by_default(self):
		self.assertFalse(self.forgot_request.is_accepted)

	def test_created_at_by_default(self):
		self.assertTrue(
			self.forgot_request.created_at.date() == datetime.date.today()
		)

	def test_expired_at_by_default(self):
		self.assertTrue(
			self.forgot_request.expired_at.date() == datetime.date.today() + datetime.timedelta(days=1)
		)


class PersonRegistrationRequestTesting(BaseModelTesting):
	def setUp(self):
		super().setUp()
		self.registration_request = PersonRegistrationRequest \
			.objects \
			.create(
				email=SAMPLE_CORRECT_EMAIL,
				prefix_url=SAMPLE_CORRECT_PREFIX_URL
			)

	def test_email(self):
		self.assertEqual(
			self.registration_request.email,
			SAMPLE_CORRECT_EMAIL
		)

	def test_prefix_url(self):
		self.assertEqual(
			self.registration_request.prefix_url,
			SAMPLE_CORRECT_PREFIX_URL
		)

	def test_key(self):
		self.assertEqual(
			self.registration_request.key,
			hashing.get_hash(
				self.registration_request.expired_at,
				self.registration_request.email,
				self.registration_request.prefix_url
			)
		)

	def test_is_email_sent_by_default(self):
		self.assertFalse(self.registration_request.is_email_sent)

	def test_is_accepted_by_default(self):
		self.assertFalse(self.registration_request.is_accepted)

	def test_created_at_by_default(self):
		self.assertTrue(
			self.registration_request.created_at.date() == datetime.date.today()
		)

	def test_expired_at_by_default(self):
		self.assertTrue(
			self.registration_request.expired_at.date() == datetime.date.today() + datetime.timedelta(days=1)
		)


class PersonInvitationRequestModelTesting(BaseModelTesting):
	def setUp(self):
		super().setUp()
		self.invitation_request = PersonInvitationRequest\
			.objects\
			.create(
				email=SAMPLE_CORRECT_EMAIL,
				workspace=self.workspace
			)

	def test_email(self):
		self.assertEqual(
			self.invitation_request.email,
			SAMPLE_CORRECT_EMAIL
		)

	def test_workspace(self):
		self.assertEqual(
			self.invitation_request.workspace,
			self.workspace
		)

	def test_key(self):
		self.assertEqual(
			self.invitation_request.key,
			hashing.get_hash(
				self.invitation_request.expired_at,
				self.invitation_request.email,
				self.invitation_request.workspace.prefix_url
			)
		)

	def test_is_email_sent_by_default(self):
		self.assertFalse(self.invitation_request.is_email_sent)

	def test_is_accepted_by_default(self):
		self.assertFalse(self.invitation_request.is_accepted)

	def test_created_at_by_default(self):
		self.assertTrue(
			self.invitation_request.created_at.date() == datetime.date.today()
		)

	def test_expired_at_by_default(self):
		self.assertTrue(
			self.invitation_request.expired_at.date() == datetime.date.today() + datetime.timedelta(days=1)
		)


class IssueTypeCategoryIconModelTesting(BaseModelTesting):
	def setUp(self):
		super().setUp()
		self.issue_type_category_icons = IssueTypeCategoryIcon \
			.objects \
			.filter(
				workspace=self.workspace,
				project=self.project,
			) \
			.all()

	def test_issue_type_category_icons_were_created_with_correct_prefixes(self):
		default_prefixes = [
			'mdi-bag-personal',
			'mdi-bookmark',
			'mdi-file-tree',
			'mdi-bug'
		]

		prefixes = list(self.issue_type_category_icons.values_list('prefix', flat=True))

		self.assertEqual(
			len(set(default_prefixes + prefixes)), 4
		)

	def test_issue_type_category_icons_were_created_with_correct_colors(self):
		default_colors = [
			'#b366ff',
			'#8ffc77',
			'#66b3ff',
			'#f02222'
		]

		colors = list(self.issue_type_category_icons.values_list('color', flat=True))

		final_colors_list = default_colors + colors

		self.assertEqual(len(set(final_colors_list)), 4)

	def test_issue_type_category_icons_were_created_with_correct_workspaces(self):
		workspaces_id_set = set(self.issue_type_category_icons.values_list('workspace_id', flat=True))

		self.assertEqual(list(workspaces_id_set)[0], self.workspace.id)
		self.assertEqual(len(workspaces_id_set), 1)

	def test_issue_type_category_icons_were_created_with_correct_projects(self):
		projects_id_set = set(self.issue_type_category_icons.values_list('project_id', flat=True))

		self.assertEqual(list(projects_id_set)[0], self.project.id)
		self.assertEqual(len(projects_id_set), 1)


class IssueTypeCategoryModelTesting(BaseModelTesting):
	def setUp(self):
		super().setUp()
		self.issue_type_categories = IssueTypeCategory \
			.objects \
			.filter(
				workspace=self.workspace,
				project=self.project
			) \
			.all()

	def test_issue_type_categories_were_created_with_correct_workspaces(self):
		workspaces_id_set = set(
			self.issue_type_categories.values_list('workspace_id', flat=True)
		)

		self.assertEqual(list(workspaces_id_set)[0], self.workspace.id)
		self.assertEqual(len(workspaces_id_set), 1)

	def test_issue_type_categories_were_created_with_correct_projects(self):
		projects_id_set = set(
			self.issue_type_categories.values_list('project_id', flat=True)
		)

		self.assertEqual(list(projects_id_set)[0], self.project.id)
		self.assertEqual(len(projects_id_set), 1)

	def test_issue_type_categories_were_created_with_correct_icons(self):
		default_prefixes = [
			'mdi-bag-personal',
			'mdi-bookmark',
			'mdi-file-tree',
			'mdi-bug'
		]

		icons_prefixes = self.issue_type_categories.values_list('icon__prefix', flat=True)
		self.assertEqual(
			len(set(list(icons_prefixes) + default_prefixes)), 4
		)


class IssueStateCategoryModelTesting(BaseModelTesting):
	def setUp(self):
		super().setUp()
		self.issue_states = IssueStateCategory \
			.objects \
			.filter(
				workspace=self.workspace,
				project=self.project
			) \
			.all()

	def test_issue_states_were_created_with_correct_workspaces(self):
		workspaces_id_set = set(
			self.issue_states.values_list('workspace_id', flat=True)
		)

		self.assertEqual(list(workspaces_id_set)[0], self.workspace.id)
		self.assertEqual(len(workspaces_id_set), 1)

	def test_issue_states_were_created_with_correct_projects(self):
		projects_id_set = set(
			self.issue_states.values_list('project_id', flat=True)
		)

		self.assertEqual(list(projects_id_set)[0], self.project.id)
		self.assertEqual(len(projects_id_set), 1)

	def test_issue_states_were_created_with_correct_titles(self):
		default_titles = [
			'Todo',
			'In Progress',
			'Verify',
			'Done'
		]

		titles = self.issue_states.values_list('title', flat=True)
		self.assertEqual(
			len(set(list(titles) + default_titles)), 4
		)


class IssueEstimationCategoryModelTesting(BaseModelTesting):
	def setUp(self):
		super().setUp()
		self.issue_estimations = IssueEstimationCategory \
			.objects \
			.filter(
				workspace=self.workspace,
				project=self.project
			) \
			.all()

	def test_issue_estimations_were_created_with_correct_workspaces(self):
		workspaces_id_set = set(
			self.issue_estimations.values_list('workspace_id', flat=True)
		)

		self.assertEqual(list(workspaces_id_set)[0], self.workspace.id)
		self.assertEqual(len(workspaces_id_set), 1)

	def test_issue_estimations_were_created_with_correct_projects(self):
		projects_id_set = set(
			self.issue_estimations.values_list('project_id', flat=True)
		)

		self.assertEqual(list(projects_id_set)[0], self.project.id)
		self.assertEqual(len(projects_id_set), 1)

	def test_issue_estimations_were_created_with_correct_titles(self):
		default_titles = [
			'XS',
			'SM',
			'M',
			'L',
			'XL',
			'XXL'
		]

		titles = self.issue_estimations.values_list('title', flat=True)
		self.assertEqual(
			len(set(list(titles) + default_titles)), 6
		)

	def test_issue_estimations_were_created_with_correct_values(self):
		default_values = [
			1,
			2,
			3,
			5,
			8,
			13
		]

		values = self.issue_estimations.values_list('value', flat=True)
		self.assertEqual(
			len(set(list(values) + default_values)), 6
		)


class IssueBasedModelTesting(BaseModelTesting):
	def setUp(self):
		super().setUp()

		self.type_category = IssueTypeCategory \
			.objects \
			.filter(
				workspace=self.workspace,
				project=self.project,
				is_default=True
			) \
			.get()

		self.state_category = IssueStateCategory\
			.objects \
			.filter(
				workspace=self.workspace,
				project=self.project,
				is_default=True
			) \
			.get()

		self.estimation_category = IssueEstimationCategory \
			.objects \
			.filter(
				workspace=self.workspace,
				project=self.project,
				value=1
			)\
			.get()

		self.issue = Issue \
			.objects \
			.create(
				workspace=self.workspace,
				project=self.project,
				title=SAMPLE_CORRECT_ISSUE_TITLE,
				description=SAMPLE_CORRECT_ISSUE_DESCRIPTION,
				type_category=self.type_category,
				state_category=self.state_category,
				estimation_category=self.estimation_category,
				assignee=self.person,
				created_by=self.person,
				updated_by=self.person
			)


class IssueModelTesting(IssueBasedModelTesting):
	def test_title(self):
		self.assertEqual(
			self.issue.title,
			SAMPLE_CORRECT_ISSUE_TITLE
		)

	def test_description(self):
		self.assertEqual(
			self.issue.description,
			SAMPLE_CORRECT_ISSUE_DESCRIPTION
		)

	def test_type_category(self):
		self.assertEqual(
			self.issue.type_category,
			self.type_category
		)

	def test_state_category(self):
		self.assertEqual(
			self.issue.state_category,
			self.state_category
		)

	def test_estimation_category(self):
		self.assertEqual(
			self.issue.estimation_category,
			self.estimation_category
		)

	def test_assignee(self):
		self.assertEqual(
			self.issue.assignee,
			self.person
		)

	def test_attachments_are_none(self):
		self.assertEqual(
			self.issue.attachments.count(),
			0
		)


class IssueHistoryModelTesting(IssueBasedModelTesting):
	def setUp(self):
		super().setUp()

		self.issue_history = IssueHistory \
			.objects \
			.filter(
				issue=self.issue,
				entry_type__contains='playlist-plus'
			) \
			.first()

	def test_issue(self):
		self.assertEqual(
			self.issue_history.issue,
			self.issue
		)

	def test_entry_type(self):
		self.assertTrue(isinstance(self.issue_history, IssueHistory))

	def test_edited_field(self):
		self.assertIsNone(self.issue_history.edited_field)

	def test_before_value(self):
		self.assertIsNone(self.issue_history.before_value)

	def test_after_value(self):
		self.assertIsNone(self.issue_history.after_value)


class IssueMessageModelTesting(IssueBasedModelTesting):
	def setUp(self):
		super().setUp()

		self.issue_message = IssueMessage\
			.objects\
			.create(
				workspace=self.workspace,
				project=self.project,
				issue=self.issue,
				created_by=self.person,
				description=SAMPLE_CORRECT_ISSUE_MESSAGE_DESCRIPTION
			)

	def test_issue(self):
		self.assertEqual(
			self.issue_message.issue,
			self.issue
		)

	def test_description(self):
		self.assertEqual(
			self.issue_message.description,
			SAMPLE_CORRECT_ISSUE_MESSAGE_DESCRIPTION
		)

	def test_created_at(self):
		self.assertTrue(
			datetime.datetime.now() - self.issue_message.created_at <= datetime.timedelta(hours=1)
		)

	def test_updated_at(self):
		self.assertTrue(
			self.issue_message.updated_at.date() == datetime.date.today()
		)


class ProjectBacklogModelTesting(IssueBasedModelTesting):
	def setUp(self):
		super().setUp()

		self.project_backlog = ProjectBacklog \
			.objects \
			.filter(
				workspace=self.workspace,
				project=self.project
			) \
			.get()

	def test_issues_list_is_manageable(self):
		# Test that created issue was automatically assigned to ProjectBacklog.
		self.assertEqual(self.project_backlog.issues.count(), 1)

		self.project_backlog \
			.issues \
			.add(self.issue)

		self.assertEqual(self.project_backlog.issues.count(), 1)
		self.assertEqual(self.project_backlog.issues.first(), self.issue)

		self.project_backlog.issues.remove(self.issue)

		self.assertEqual(self.project_backlog.issues.count(), 0)


class SprintBasedModelTesting(BaseModelTesting):
	def setUp(self):
		super().setUp()

		self.sprint = Sprint \
			.objects \
			.create(
				workspace=self.workspace,
				project=self.project,
				title=SAMPLE_CORRECT_SPRINT_TITLE,
				goal=SAMPLE_CORRECT_SPRINT_GOAL
			)


class SprintModelTesting(SprintBasedModelTesting):
	def test_title(self):
		self.assertEqual(
			self.sprint.title, SAMPLE_CORRECT_SPRINT_TITLE
		)

	def test_goal(self):
		self.assertEqual(
			self.sprint.goal, SAMPLE_CORRECT_SPRINT_GOAL
		)

	def test_issues(self):
		self.assertEqual(
			self.sprint.issues.count(), 0
		)

	def test_is_started(self):
		self.assertFalse(self.sprint.is_started)

	def test_is_completed(self):
		self.assertFalse(self.sprint.is_completed)

	def test_started_at(self):
		self.assertIsNone(self.sprint.started_at)

	def test_finished_at(self):
		self.assertIsNone(self.sprint.finished_at)


class ProjectNonWorkingDayModelTesting(BaseModelTesting):
	def setUp(self):
		super().setUp()
		self.project_non_working_day = ProjectNonWorkingDay \
			.objects \
			.create(
				workspace=self.workspace,
				project=self.project,
				date=datetime.date.today()
			)

	def test_workspace(self):
		self.assertEqual(
			self.project_non_working_day.workspace,
			self.workspace
		)

	def test_project(self):
		self.assertEqual(
			self.project_non_working_day.project,
			self.project
		)

	def test_date(self):
		self.assertEqual(
			self.project_non_working_day.date,
			datetime.date.today()
		)


class ProjectWorkingDaysModelTesting(BaseModelTesting):
	def setUp(self):
		super().setUp()
		self.project_working_days = ProjectWorkingDays \
			.objects \
			.filter(
				workspace=self.workspace,
				project=self.project
			) \
			.get()

	def test_timezone(self):
		self.assertEqual(
			self.project_working_days.timezone,
			'UTC'
		)

	def test_monday(self):
		self.assertTrue(self.project_working_days.monday)

	def test_tuesday(self):
		self.assertTrue(self.project_working_days.tuesday)

	def test_wednesday(self):
		self.assertTrue(self.project_working_days.wednesday)

	def test_thursday(self):
		self.assertTrue(self.project_working_days.thursday)

	def test_friday(self):
		self.assertTrue(self.project_working_days.friday)

	def test_saturday(self):
		self.assertFalse(self.project_working_days.saturday)

	def test_sunday(self):
		self.assertFalse(self.project_working_days.sunday)

	def test_non_working_days_are_manageable(self):
		self.assertEqual(self.project_working_days.non_working_days.count(), 0)

	def test_updated_at(self):
		self.assertTrue(
			datetime.datetime.now() - self.project_working_days.updated_at <= datetime.timedelta(hours=1)
		)


class SprintEffortsHistoryModelTesting(SprintBasedModelTesting):
	def setUp(self):
		super().setUp()

		self.sprint_efforts_history = SprintEffortsHistory \
			.objects \
			.create(
				workspace=self.workspace,
				project=self.project,
				sprint=self.sprint,
				total_value=0,
				done_value=0
			)

	def test_sprint(self):
		self.assertEqual(
			self.sprint,
			self.sprint_efforts_history.sprint
		)

	def test_point_at(self):
		self.assertTrue(
			datetime.datetime.now() - self.sprint_efforts_history.point_at <= datetime.timedelta(hours=1)
		)

	def test_created_at(self):
		self.assertTrue(
			datetime.datetime.now() - self.sprint_efforts_history.created_at <= datetime.timedelta(hours=1)
		)

	def test_updated_at(self):
		self.assertTrue(
			datetime.datetime.now() - self.sprint_efforts_history.updated_at <= datetime.timedelta(hours=1)
		)

	def test_total_value(self):
		self.assertEqual(
			self.sprint_efforts_history.total_value, 0
		)

	def test_done_value(self):
		self.assertEqual(
			self.sprint_efforts_history.done_value, 0
		)

	def test_estimated_value(self):
		self.assertEqual(
			self.sprint_efforts_history.total_value - self.sprint_efforts_history.done_value,
			self.sprint_efforts_history.estimated_value
		)

# IssueAttachment
# SprintDuration
