from channels.db import database_sync_to_async
from djangochannelsrestframework.consumers import AsyncAPIConsumer
from djangochannelsrestframework.decorators import action
from djangochannelsrestframework.observer import model_observer
from djangochannelsrestframework.permissions import IsAuthenticated

from .api.serializers import \
	IssueMessageSerializer, \
	IssueSerializer, \
	IssueTypeSerializer, \
	IssueTypeIconSerializer, \
	IssueStateSerializer, \
	IssueEstimationSerializer, SprintEffortsHistorySerializer

from .models import \
	Issue, \
	IssueMessage, \
	IssueTypeCategory, \
	IssueTypeCategoryIcon, \
	IssueStateCategory, \
	IssueEstimationCategory, \
	Person, \
	Workspace, SprintEffortsHistory

UNABLE_SUBSCRIBE_NO_WORKSPACE_TEMPLATE = 'Unable to subscribe {obj} cause workspace was not found'
UNABLE_UNSUBSCRIBE_NO_WORKSPACE_TEMPLATE = 'Unable to unsubscribe {obj} cause workspace was not found'


class IssueMessagesObserver(AsyncAPIConsumer):
	"""
    This consumer allow us to subscribe to all messages in give issue.
    By checking permission we have to check that issue belong to one of
    workspace that person participated in.
    Payload example
    {
      "action": "subscribe_to_messages_in_issue",
      "request_id": 4,
      "issue_pk": 48
    }
    """
	permission_classes = (
		IsAuthenticated,  # Special async permission
	)

	@model_observer(IssueMessage)
	async def message_change_handler(self, message, observer=None, action=None, **kwargs):
		await self.send_json(dict(message=message, action=action))

	@message_change_handler.serializer
	def model_serializer(self, instance: IssueMessage, action=None, **kwargs):
		return IssueMessageSerializer(instance).data

	@message_change_handler.groups_for_signal
	def message_change_handler(self, instance: IssueMessage, **kwargs):
		yield f'-issue__{instance.issue_id}'
		yield f'-pk__{instance.pk}'

	@message_change_handler.groups_for_consumer
	def message_change_handler(self, issue=None, message=None, **kwargs):
		if issue is not None:
			yield f'-issue__{issue.pk}'
		if message is not None:
			yield f'-pk__{message.pk}'

	@database_sync_to_async
	def get_issue_filter_data(self, issue_pk, **kwargs):
		user = self.scope.get('user')
		person = Person.objects.get(user=user)

		issue = Issue.objects.get(
			id=issue_pk,
			workspace__participants__in=[person])

		return issue

	@action()
	async def subscribe_to_messages_in_issue(self, issue_pk, **kwargs):
		try:
			issue = await self.get_issue_filter_data(issue_pk=issue_pk)
			await self.message_change_handler.subscribe(issue=issue)
		except Issue.DoesNotExist:
			print(UNABLE_SUBSCRIBE_NO_WORKSPACE_TEMPLATE.format(obj='issue'))

	@action()
	async def unsubscribe_from_messages_in_issue(self, issue_pk, **kwargs):
		try:
			issue = await self.get_issue_filter_data(issue_pk=issue_pk)
			await self.message_change_handler.unsubscribe(issue=issue)
		except Issue.DoesNotExist:
			print(UNABLE_UNSUBSCRIBE_NO_WORKSPACE_TEMPLATE.format(obj='issue'))


class WorkspaceIssuesObserver(AsyncAPIConsumer):
	"""
    This consumer allow us to subscribe to all issues in give workspace.
    By checking permission we have to check that person participate in given workspace.
    Payload example
    {
        "action": "subscribe_to_issues_in_workspace",
        "request_id": 4,
        "workspace_pk": 34
    }
    With stream payload should look like this.
    {"stream":"workspace_issues","payload":{"action":"subscribe_to_issues_in_workspace","request_id":442,"issue_pk":61}}
    """
	permission_classes = (
		IsAuthenticated,  # Special async permission
	)

	@model_observer(Issue)
	async def issue_change_handler(self, message, observer=None, action=None, **kwargs):
		await self.send_json(dict(message=message, action=action))

	@issue_change_handler.serializer
	def model_serializer(self, instance: Issue, action=None, **kwargs):
		return IssueSerializer(instance).data

	@issue_change_handler.groups_for_signal
	def issue_change_handler(self, instance: Issue, **kwargs):
		yield f'-workspace__{instance.workspace_id}'
		yield f'-pk__{instance.pk}'

	@issue_change_handler.groups_for_consumer
	def issue_change_handler(self, workspace=None, issue=None, **kwargs):
		if workspace is not None:
			yield f'-workspace__{workspace.pk}'
		if issue is not None:
			yield f'-pk__{issue.pk}'

	@database_sync_to_async
	def get_workspace_filter_data(self, workspace_pk, **kwargs):
		user = self.scope.get('user')
		person = Person.objects.get(user=user)

		workspace = Workspace.objects.get(id=workspace_pk,
										  participants__in=[person])

		return workspace

	@action()
	async def subscribe_to_issues_in_workspace(self, workspace_pk, **kwargs):
		try:
			workspace = await self.get_workspace_filter_data(workspace_pk=workspace_pk)
			await self.issue_change_handler.subscribe(workspace=workspace)
		except Workspace.DoesNotExist:
			print(UNABLE_SUBSCRIBE_NO_WORKSPACE_TEMPLATE.format(obj='issues'))

	@action()
	async def unsubscribe_from_issues_in_workspace(self, workspace_pk, **kwargs):
		try:
			workspace = await self.get_workspace_filter_data(workspace_pk=workspace_pk)
			await self.issue_change_handler.unsubscribe(workspace=workspace)
		except Workspace.DoesNotExist:
			print(UNABLE_UNSUBSCRIBE_NO_WORKSPACE_TEMPLATE.format(obj='issues'))


class WorkspaceIssueTypeCategoriesObserver(AsyncAPIConsumer):
	"""
    This consumer allow us to subscribe to all issues types in given workspace.
    By checking permission we have to check that person participate in given workspace.
    Payload example
    {
        "action": "subscribe_to_issue_type_categories_in_workspace",
        "request_id": 4,
        "workspace_pk": 34
    }
    With stream payload should look like this.
    {
    "stream":"workspace_issues","payload":{
        "action":"subscribe_to_issue_type_categories_in_workspace",
        "request_id":442,
        "issue_pk":61}
    }
    """
	permission_classes = (
		IsAuthenticated,
	)

	@model_observer(IssueTypeCategory)
	async def issue_type_category_change_handler(self, message, observer=None, action=None, **kwargs):
		await self.send_json(dict(message=message, action=action))

	@issue_type_category_change_handler.serializer
	def model_serializer(self, instance: IssueTypeCategory, action=None, **kwargs):
		return IssueTypeSerializer(instance).data

	@issue_type_category_change_handler.groups_for_signal
	def issue_type_category_change_handler(self, instance: IssueTypeCategory, **kwargs):
		yield f'-workspace__{instance.workspace_id}'
		yield f'-pk__{instance.pk}'

	@issue_type_category_change_handler.groups_for_consumer
	def issue_type_category_change_handler(self, workspace=None, issue_type=None, **kwargs):
		if workspace is not None:
			yield f'-workspace__{workspace.pk}'
		if issue_type is not None:
			yield f'-pk__{issue_type.pk}'

	@database_sync_to_async
	def get_workspace_filter_data(self, workspace_pk, **kwargs):
		user = self.scope.get('user')
		person = Person.objects.get(user=user)

		workspace = Workspace.objects.get(id=workspace_pk,
										  participants__in=[person])

		return workspace

	@action()
	async def subscribe_to_issue_type_categories_in_workspace(self, workspace_pk, **kwargs):
		try:
			workspace = await self.get_workspace_filter_data(workspace_pk=workspace_pk)
			await self.issue_type_category_change_handler.subscribe(workspace=workspace)
		except Workspace.DoesNotExist:
			print(UNABLE_SUBSCRIBE_NO_WORKSPACE_TEMPLATE.format(obj='issue type category'))

	@action()
	async def unsubscribe_from_issue_type_categories_in_workspace(self, workspace_pk, **kwargs):
		try:
			workspace = await self.get_workspace_filter_data(workspace_pk=workspace_pk)
			await self.issue_type_category_change_handler.unsubscribe(workspace=workspace)
		except Workspace.DoesNotExist:
			print(UNABLE_UNSUBSCRIBE_NO_WORKSPACE_TEMPLATE.format(obj='issue type category'))


class WorkspaceIssueTypeCategoriesIconsObserver(AsyncAPIConsumer):
	"""
    This consumer allow us to subscribe to all issues types icons in given workspace.
    By checking permission we have to check that person participate in given workspace.
    Payload example
    {
        "action": "subscribe_to_issue_type_categories_icons_in_workspace",
        "request_id": 4,
        "workspace_pk": 34
    }
    With stream payload should look like this.
    {
    "stream":"workspace_issues","payload":{
        "action":"subscribe_to_issue_type_categories_icons_in_workspace",
        "request_id":442,
        "issue_pk":61}
    }
    """
	permission_classes = (
		IsAuthenticated,
	)

	@model_observer(IssueTypeCategoryIcon)
	async def issue_type_category_icon_change_handler(self, message, observer=None, action=None, **kwargs):
		await self.send_json(dict(message=message, action=action))

	@issue_type_category_icon_change_handler.serializer
	def model_serializer(self, instance: IssueTypeCategoryIcon, action=None, **kwargs):
		return IssueTypeIconSerializer(instance).data

	@issue_type_category_icon_change_handler.groups_for_signal
	def issue_type_category_icon_change_handler(self, instance: IssueTypeCategoryIcon, **kwargs):
		yield f'-workspace__{instance.workspace_id}'
		yield f'-pk__{instance.pk}'

	@issue_type_category_icon_change_handler.groups_for_consumer
	def issue_type_category_icon_change_handler(self, workspace=None, issue_type_category_icon=None, **kwargs):
		if workspace is not None:
			yield f'-workspace__{workspace.pk}'
		if issue_type_category_icon is not None:
			yield f'-pk__{issue_type_category_icon.pk}'

	@database_sync_to_async
	def get_workspace_filter_data(self, workspace_pk, **kwargs):
		user = self.scope.get('user')
		person = Person.objects.get(user=user)

		workspace = Workspace.objects.get(id=workspace_pk,
										  participants__in=[person])

		return workspace

	@action()
	async def subscribe_to_issue_type_categories_icons_in_workspace(self, workspace_pk, **kwargs):
		try:
			workspace = await self.get_workspace_filter_data(workspace_pk=workspace_pk)
			await self.issue_type_category_icon_change_handler.subscribe(workspace=workspace)
		except Workspace.DoesNotExist:
			print(UNABLE_SUBSCRIBE_NO_WORKSPACE_TEMPLATE.format(obj='issue type icon category'))

	@action()
	async def unsubscribe_from_issue_type_categories_icons_in_workspace(self, workspace_pk, **kwargs):
		try:
			workspace = await self.get_workspace_filter_data(workspace_pk=workspace_pk)
			await self.issue_type_category_icon_change_handler.unsubscribe(workspace=workspace)
		except Workspace.DoesNotExist:
			print(UNABLE_UNSUBSCRIBE_NO_WORKSPACE_TEMPLATE.format(obj='issue type icon category'))


class WorkspaceIssueStateCategoriesObserver(AsyncAPIConsumer):
	"""
    This consumer allow us to subscribe to all issues states in given workspace.
    By checking permission we have to check that person participate in given workspace.
    Payload example
    {
        "action": "subscribe_to_issue_state_categories_in_workspace",
        "request_id": 4,
        "workspace_pk": 34
    }
    With stream payload should look like this.
    {
    "stream":"workspace_issues","payload":{
            "action":"subscribe_to_issue_state_categories_in_workspace",
            "request_id":442,
            "issue_pk":61
        }
    }
    """
	permission_classes = (
		IsAuthenticated,
	)

	@model_observer(IssueStateCategory)
	async def issue_state_change_handler(self, message, observer=None, action=None, **kwargs):
		await self.send_json(dict(message=message, action=action))

	@issue_state_change_handler.serializer
	def model_serializer(self, instance: IssueStateCategory, action=None, **kwargs):
		return IssueStateSerializer(instance).data

	@issue_state_change_handler.groups_for_signal
	def issue_state_change_handler(self, instance: IssueStateCategory, **kwargs):
		yield f'-workspace__{instance.workspace_id}'
		yield f'-pk__{instance.pk}'

	@issue_state_change_handler.groups_for_consumer
	def issue_state_change_handler(self, workspace=None, issue_state=None, **kwargs):
		if workspace is not None:
			yield f'-workspace__{workspace.pk}'
		if issue_state is not None:
			yield f'-pk__{issue_state.pk}'

	@database_sync_to_async
	def get_workspace_filter_data(self, workspace_pk, **kwargs):
		user = self.scope.get('user')
		person = Person.objects.get(user=user)

		workspace = Workspace.objects.get(id=workspace_pk,
										  participants__in=[person])

		return workspace

	@action()
	async def subscribe_to_issue_state_categories_in_workspace(self, workspace_pk, **kwargs):
		try:
			workspace = await self.get_workspace_filter_data(workspace_pk=workspace_pk)
			await self.issue_state_change_handler.subscribe(workspace=workspace)
		except Workspace.DoesNotExist:
			print(UNABLE_SUBSCRIBE_NO_WORKSPACE_TEMPLATE.format(obj='issue state category'))

	@action()
	async def unsubscribe_from_issue_state_categories_in_workspace(self, workspace_pk, **kwargs):
		try:
			workspace = await self.get_workspace_filter_data(workspace_pk=workspace_pk)
			await self.issue_state_change_handler.unsubscribe(workspace=workspace)
		except Workspace.DoesNotExist:
			print(UNABLE_UNSUBSCRIBE_NO_WORKSPACE_TEMPLATE.format(obj='issue type category'))


class WorkspaceIssueEstimationCategoriesObserver(AsyncAPIConsumer):
	"""
    This consumer allow us to subscribe to all issues estimations in given workspace.
    By checking permission we have to check that person participate in given workspace.
    Payload example
    {
        "action": "subscribe_to_issue_estimation_categories_in_workspace",
        "request_id": 4,
        "workspace_pk": 34
    }
    With stream payload should look like this.
    {
    "stream":"workspace_issues","payload":{
            "action":"subscribe_to_issue_estimation_categories_in_workspace",
            "request_id":442,
            "workspace_pk":34
        }
    }
    """
	permission_classes = (
		IsAuthenticated,
	)

	@model_observer(IssueEstimationCategory)
	async def issue_estimation_category_change_handler(self, message, observer=None, action=None, **kwargs):
		await self.send_json(dict(message=message, action=action))

	@issue_estimation_category_change_handler.serializer
	def model_serializer(self, instance: IssueEstimationCategory, action=None, **kwargs):
		return IssueEstimationSerializer(instance).data

	@issue_estimation_category_change_handler.groups_for_signal
	def issue_estimation_category_change_handler(self, instance: IssueEstimationCategory, **kwargs):
		yield f'-workspace__{instance.workspace_id}'
		yield f'-pk__{instance.pk}'

	@issue_estimation_category_change_handler.groups_for_consumer
	def issue_estimation_category_change_handler(self, workspace=None, issue_estimation=None, **kwargs):
		if workspace is not None:
			yield f'-workspace__{workspace.pk}'
		if issue_estimation is not None:
			yield f'-pk__{issue_estimation.pk}'

	@database_sync_to_async
	def get_workspace_filter_data(self, workspace_pk, **kwargs):
		user = self.scope.get('user')
		person = Person.objects.get(user=user)

		workspace = Workspace.objects.get(id=workspace_pk,
										  participants__in=[person])

		return workspace

	@action()
	async def subscribe_to_issue_estimation_categories_in_workspace(self, workspace_pk, **kwargs):
		try:
			workspace = await self.get_workspace_filter_data(workspace_pk=workspace_pk)
			await self.issue_estimation_category_change_handler.subscribe(workspace=workspace)
		except Workspace.DoesNotExist:
			print(UNABLE_SUBSCRIBE_NO_WORKSPACE_TEMPLATE.format(obj='issue estimation category'))

	@action()
	async def unsubscribe_from_issue_estimation_categories_in_workspace(self, workspace_pk, **kwargs):
		try:
			workspace = await self.get_workspace_filter_data(workspace_pk=workspace_pk)
			await self.issue_estimation_category_change_handler.unsubscribe(workspace=workspace)
		except Workspace.DoesNotExist:
			print(UNABLE_UNSUBSCRIBE_NO_WORKSPACE_TEMPLATE.format(obj='issue estimation category'))


class WorkspaceSprintEffortsHistoryObserver(AsyncAPIConsumer):
	"""
	This consumer allow us to subscribe to all Sprint Efforts changed.
	Usually we do this to calculate how close are we to the end of Sprint.
	Payload example:
	{
		"action": "subscribe_to_sprint_efforts_history_in_workspace",
		"request_id": 4,
		"workspace_pk": 34
	}
	With stream payload should look like this.
	{
	"stream": "workspace_issues", "payload": {
		"action": "subscribe_to_sprint_efforts_history_in_workspace",
		"request_id": 442,
		"workspace_pk": 34
	}
	"""
	permission_classes = (
		IsAuthenticated,
	)

	@model_observer(SprintEffortsHistory)
	async def sprint_efforts_history_change_handler(self, message, observer=None, action=None, **kwargs):
		await self.send_json(dict(message=message, action=action))

	@sprint_efforts_history_change_handler.serializer
	def model_serializer(self, instance: SprintEffortsHistory, action=None, **kwargs):
		return SprintEffortsHistorySerializer(instance).data

	@sprint_efforts_history_change_handler.groups_for_signal
	def sprint_efforts_history_change_handler(self, instance: SprintEffortsHistory, **kwargs):
		yield f'-workspace__{instance.workspace_id}'
		yield f'-pk__{instance.pk}'

	@sprint_efforts_history_change_handler.groups_for_consumer
	def sprint_efforts_history_change_handler(self, workspace=None, sprint_effort_history=None, **kwargs):
		if workspace is not None:
			yield f'-workspace__{workspace.pk}'
		if sprint_effort_history is not None:
			yield f'-pk__{sprint_effort_history.pk}'

	@database_sync_to_async
	def get_workspace_filter_data(self, workspace_pk, **kwargs):
		user = self.scope.get('user')
		person = Person.objects.get(user=user)

		workspace = Workspace.objects.get(id=workspace_pk,
										  participants__in=[person])

		return workspace

	@action()
	async def subscribe_to_sprint_efforts_history_in_workspace(self, workspace_pk, **kwargs):
		try:
			workspace = await self.get_workspace_filter_data(workspace_pk=workspace_pk)
			await self.sprint_efforts_history_change_handler.subscribe(workspace=workspace)
		except Workspace.DoesNotExist:
			print(UNABLE_SUBSCRIBE_NO_WORKSPACE_TEMPLATE.format(obj='sprint efforts history'))

	@action()
	async def unsubscribe_from_sprint_efforts_history_in_workspace(self, workspace_pk, **kwargs):
		try:
			workspace = await self.get_workspace_filter_data(workspace_pk=workspace_pk)
			await self.sprint_efforts_history_change_handler.unsubscribe(workspace=workspace)
		except Workspace.DoesNotExist:
			print(UNABLE_UNSUBSCRIBE_NO_WORKSPACE_TEMPLATE.format(obj='sprint efforts history'))

