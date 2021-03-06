import bleach
from django.db.models import Q
from django.db.models.signals import \
    pre_save, \
    post_save, \
    m2m_changed, \
    post_delete

from django.conf import settings
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from conf.common.mime_settings import FRONTEND_ICON_SET
from libs.helpers.datetimepresets import today_earliest, today_latest
from .api.tasks import send_mentioned_in_message_email, \
    send_mentioned_in_description_email

from enum import Enum

from .models import Project, \
    ProjectBacklog, \
    IssueTypeCategory, \
    IssueStateCategory, \
    Sprint, \
    Issue, \
    IssueMessage, IssueEstimationCategory, SprintEstimation, IssueHistory, IssueTypeCategoryIcon


class ActionM2M(Enum):
    PRE_ADD = 'pre_add'
    POST_ADD = 'post_add'
    PRE_REMOVE = 'pre_remove'
    POST_REMOVE = 'post_remove'
    PRE_CLEAR = 'pre_clear'
    POST_CLEAR = 'post_clear'


@receiver(post_save, sender=Issue)
def put_created_issue_to_backlog(instance: Issue, created: bool, **kwargs):
    """
    Lets put just created issue to Backlog.
    """
    if not created:
        return True

    backlog_with_same_workspace_and_project = ProjectBacklog.objects \
        .filter(workspace=instance.workspace,
                project=instance.project)

    if backlog_with_same_workspace_and_project.exists():
        backlog = backlog_with_same_workspace_and_project.get()
        backlog.issues.add(instance)


@receiver(post_save, sender=Project)
def create_backlog_for_project(instance: Project, created: bool, **kwargs):
    """
    Every project should contain only one Backlog.
    So we provide it.
    """
    project_backlog = ProjectBacklog.objects.filter(workspace=instance.workspace,
                                                    project=instance)

    if created and not project_backlog.exists():
        backlog = ProjectBacklog(workspace=instance.workspace,
                                 project=instance)
        backlog.save()


@receiver(post_save, sender=Project)
def create_icons_for_project(instance: Project, created: bool, **kwargs):
    """
    Every project should contain default icons.
    """
    if not created:
        return False


@receiver(post_save, sender=Project)
def create_default_issue_type_category_for_project(instance: Project, created: bool, **kwargs):
    """
    Every project should contain defaults Issue Types
    So we provide it.
    @todo Better to add default issue types based on current language of project
    """
    issue_types = IssueTypeCategory.objects.filter(workspace=instance.workspace,
                                                   project=instance)

    if created and not issue_types.exists():
        # Colors from https://quasar.dev/style/color-palette
        # Icons from https://materialdesignicons.com/ with 'mdi-' prefix
        icons = \
            IssueTypeCategoryIcon.objects.bulk_create([
                #  Epic
                IssueTypeCategoryIcon(
                    workspace=instance.workspace,
                    project=instance,
                    prefix='mdi-bag-personal',
                    color='#b366ff',
                    ordering=3
                ),
                # User Story
                IssueTypeCategoryIcon(
                    workspace=instance.workspace,
                    project=instance,
                    prefix='mdi-bookmark',
                    color='#8ffc77',
                    ordering=1
                ),
                # Task
                IssueTypeCategoryIcon(
                    workspace=instance.workspace,
                    project=instance,
                    prefix='mdi-file-tree',
                    color='#66b3ff',
                    ordering=2
                ),
                # Bug
                IssueTypeCategoryIcon(
                    workspace=instance.workspace,
                    project=instance,
                    prefix='mdi-bug',
                    color='#f02222',
                    ordering=0
                )]
            )

        IssueTypeCategory.objects.bulk_create([
            IssueTypeCategory(workspace=instance.workspace,
                              project=instance,
                              title=_('Epic'),
                              icon=icons[0],
                              is_subtask=False,
                              is_default=False,
                              ordering=0),
            IssueTypeCategory(workspace=instance.workspace,
                              project=instance,
                              title=_('User Story'),
                              icon=icons[1],
                              is_subtask=True,
                              is_default=True,
                              ordering=1),
            IssueTypeCategory(workspace=instance.workspace,
                              project=instance,
                              title=_('Task'),
                              icon=icons[2],
                              is_subtask=True,
                              is_default=False,
                              ordering=2),
            IssueTypeCategory(workspace=instance.workspace,
                              project=instance,
                              title=_('Bug'),
                              icon=icons[3],
                              is_subtask=False,
                              is_default=False,
                              ordering=3)
        ])


@receiver(post_save, sender=Project)
def create_default_issue_state_category_for_project(instance: Project, created: bool, **kwargs):
    """
    Every project should contain issue states.
    So we provide it.
    @todo Better to add states based on current language of project
    """
    issue_states = IssueStateCategory.objects.filter(workspace=instance.workspace,
                                                     project=instance)

    if created and not issue_states.exists():
        todo = IssueStateCategory(workspace=instance.workspace,
                                  project=instance,
                                  title=_('Todo'),
                                  is_default=True,
                                  is_done=False)

        todo.save()

        in_progress = IssueStateCategory(workspace=instance.workspace,
                                         project=instance,
                                         title=_('In Progress'),
                                         is_default=False,
                                         is_done=False)

        in_progress.save()

        verify = IssueStateCategory(workspace=instance.workspace,
                                    project=instance,
                                    title=_('Verify'),
                                    is_default=False,
                                    is_done=False)

        verify.save()

        done = IssueStateCategory(workspace=instance.workspace,
                                  project=instance,
                                  title=_('Done'),
                                  is_default=False,
                                  is_done=True)

        done.save()


@receiver(post_save, sender=Project)
def create_default_issue_estimation_for_project(instance: Project, created: bool, **kwargs):
    issue_estimations = IssueEstimationCategory.objects.filter(workspace=instance.workspace,
                                                               project=instance)

    if created and not issue_estimations.exists():
        xs = IssueEstimationCategory(workspace=instance.workspace,
                                     project=instance,
                                     title=_('XS'),
                                     value=1)
        xs.save()

        sm = IssueEstimationCategory(workspace=instance.workspace,
                                     project=instance,
                                     title=_('SM'),
                                     value=2)
        sm.save()

        m = IssueEstimationCategory(workspace=instance.workspace,
                                    project=instance,
                                    title=_('M'),
                                    value=3)
        m.save()

        l_ = IssueEstimationCategory(workspace=instance.workspace,
                                     project=instance,
                                     title=_('L'),
                                     value=5)
        l_.save()

        xl = IssueEstimationCategory(workspace=instance.workspace,
                                     project=instance,
                                     title=_('XL'),
                                     value=8)
        xl.save()

        xxl = IssueEstimationCategory(workspace=instance.workspace,
                                      project=instance,
                                      title=_('XXL'),
                                      value=13)
        xxl.save()


@receiver(m2m_changed, sender=Sprint.issues.through)
@receiver(m2m_changed, sender=ProjectBacklog.issues.through)
def arrange_issue_in_sprints(sender, action, instance, **kwargs):
    """
    1) Find any sprints that have the same issues.
    2) Iterate all over sprints to remove issues that
    bind to sprint or Backlog from sprints.
    """
    if action != ActionM2M.POST_ADD.value:
        return True

    base_query = Q(issues__in=instance.issues.all())
    additional_query = {
        sender is Sprint.issues.through: ~Q(id=instance.pk),
        sender is ProjectBacklog.issues.through: Q()
    }[True]

    sprint_with_intersection_of_issues = Sprint.objects \
        .filter(base_query, additional_query)

    if not sprint_with_intersection_of_issues.exists():
        return True

    to_remove = instance.issues.values_list('id', flat=True)
    for _sprint in sprint_with_intersection_of_issues.all():
        _sprint.issues.remove(*to_remove)


@receiver(m2m_changed, sender=Sprint.issues.through)
def arrange_issue_in_backlog(action, instance, **kwargs):
    """
    1) Find Backlog that have same issues as sender Sprint.
    2) Remove that issues from Backlog.
    """

    """
    We need to track only post add action """
    if action != ActionM2M.POST_ADD.value:
        return True

    base_query = Q(workspace=instance.workspace) & Q(project=instance.project) & Q(issues__in=instance.issues.all())
    to_remove = instance.issues.values_list('id', flat=True)

    try:
        backlog = ProjectBacklog.objects.filter(base_query).get()
        backlog.issues.remove(*to_remove)

    except ProjectBacklog.DoesNotExist:
        pass


@receiver(post_save, sender=IssueMessage)
def signal_mentioned_in_message_emails(instance: IssueMessage, created: bool, **kwargs):
    """
    1) Check if someone was mentioned
    2) Send an email if someone was mentioned
    """

    if not created or settings.DEBUG:
        return False

    send_mentioned_in_message_email.delay(instance.pk)


@receiver(post_save, sender=Issue)
def signal_mentioned_in_description_emails(instance: Issue, created: bool, **kwargs):
    """
    Send an email if someone was mentioned in issue description
    """
    if not created or settings.DEBUG:
        return False

    send_mentioned_in_description_email.delay(instance.pk)


@receiver(post_save, sender=Issue)
def signal_sprint_estimation_change(instance: Issue, created: bool, **kwargs):
    """
    Create Sprint Estimation on changing Issue, that belong to started sprint
    We watching such changes as estimation category and state category
    """

    """
    First of all getting started sprint to understand do this issue belong to it"""
    sprint = Sprint.objects \
        .filter(workspace=instance.workspace,
                project=instance.project,
                is_started=True,
                issues__in=[instance])

    """
    If we don't have a started sprint or this sprint do not include current issue
    then we just exit """
    if not sprint.exists():
        return True

    _sprint = sprint.get()
    sprint_estimation = SprintEstimation.objects \
        .filter(workspace=instance.workspace,
                project=instance.project,
                sprint=_sprint,
                updated_at__range=(today_earliest(), today_latest()))

    """
    We dont need multiple estimation per day, so we have to save just the last one """
    if sprint_estimation.exists():
        _sprint_estimation: SprintEstimation = sprint_estimation.latest('updated_at')
        _sprint_estimation.calculate_estimations()
        _sprint_estimation.save()
    else:
        _sprint_estimation = SprintEstimation(workspace=instance.workspace,
                                              project=instance.project,
                                              sprint=_sprint)
        _sprint_estimation.calculate_estimations()
        _sprint_estimation.save()


def set_default_for_instance(instance, sender):
    """
    Just set default is somehow default value was deleted.
     """
    if not instance.is_default:
        return True

    categories = sender.objects \
        .filter(workspace=instance.workspace,
                project=instance.project)

    if not categories.exists() or categories.filter(is_default=True).exists():
        return True

    new_default_category = categories.all().order_by('id').first()
    new_default_category.is_default = True
    new_default_category.save()


@receiver(post_delete, sender=IssueTypeCategory)
def signal_set_issue_type_category_by_default_if_no_exists(instance: IssueTypeCategory, **kwargs):
    return set_default_for_instance(instance=instance, sender=IssueTypeCategory)


@receiver(post_delete, sender=IssueStateCategory)
def signal_set_issue_state_category_by_default_if_no_exists(instance: IssueStateCategory, **kwargs):
    return set_default_for_instance(instance=instance, sender=IssueStateCategory)


@receiver(pre_save, sender=Issue)
def signal_set_issue_history(instance: Issue, **kwargs):
    """
    Create History Entry on Issue Changing
    Pre_save signal is crucial cuz we have to compare
    instance data with database values.
    """
    if not instance.id:
        return True

    all_fields = Issue._meta.concrete_fields
    db_version = Issue.objects.get(pk=instance.id)

    foreign_data = [
        'workspace',
        'project',
        'type_category',
        'state_category',
        'estimation_category',
        'assignee'
    ]

    do_not_watch_fields = [
        'workspace',
        'number',
        'created_by',
        'updated_by',
        'created_at',
        'updated_at'
    ]

    for field in all_fields:
        _db_value = getattr(db_version, field.name)
        _instance_value = getattr(instance, field.name)

        """
        If value is the same or we decided do not track it - let's skip it
        in creating history entry"""
        if _db_value == _instance_value or \
                field.name in do_not_watch_fields:
            continue

        _edited_field_verbose_name = field.verbose_name

        if field.name in foreign_data:
            _str_before = 'None' if _db_value is None else getattr(_db_value, 'title')
            _str_after = 'None' if _instance_value is None else getattr(_instance_value, 'title')
        else:
            _str_before = bleach.clean(
                text=str(_db_value),
                tags=[],
                strip=True
            )

            _str_after = bleach.clean(
                text=str(_instance_value),
                tags=[],
                strip=True
            )

        if len(_str_before) > 60:
            _str_before = f'{_str_before[0:60]}...'

        if len(_str_after) > 60:
            _str_after = f'{_str_after[0:60]}...'

        """
        Issue history instance """
        history_entry = IssueHistory(
            issue=instance,
            entry_type=FRONTEND_ICON_SET + 'playlist-edit',
            edited_field=_edited_field_verbose_name,
            before_value=_str_before,
            after_value=_str_after,
            changed_by=instance.updated_by
        )

        history_entry.save()


@receiver(post_save, sender=Issue)
def signal_set_create_issue_history(instance: Issue, created: bool, **kwargs):
    """
    Create History Entry on Issue Creation """

    if not created:
        return True

    history_entry = IssueHistory(
        issue=instance,
        entry_type=FRONTEND_ICON_SET + 'playlist-plus',
        edited_field=None,
        before_value=None,
        after_value=None,
        changed_by=instance.updated_by
    )

    history_entry.save()
