from django.urls import path
from rest_framework import routers

from . import views
from .views import PersonInvitationRequestRetrieveUpdateView

app_name = 'core_api'

router = routers.SimpleRouter()
router.register('workspaces', views.WorkspaceViewSet, basename='workspaces')
router.register('projects', views.ProjectViewSet, basename='projects')
router.register('persons', views.PersonsViewSet, basename='collaborators')
router.register('issues', views.IssueViewSet, basename='issues')
router.register('issues-history', views.IssueHistoryViewSet, basename='issue-history')
router.register('issue-types', views.IssueTypeCategoryViewSet, basename='issue-types')
router.register('issue-type-icons', views.IssueTypeIconViewSet, basename='issue-type-icons')
router.register('issue-states', views.IssueStateCategoryViewSet, basename='issue-states')
router.register('issue-estimations', views.IssueEstimationCategoryViewSet, basename='issue-estimations')
router.register('issue-messages', views.IssueMessagesViewSet, basename='issue-messages')
router.register('issue-attachments', views.IssueAttachmentViewSet, basename='issue-attachments')
router.register('backlogs', views.ProjectBacklogViewSet, basename='backlogs')
router.register('sprints', views.SprintViewSet, basename='sprints')
router.register('sprint-efforts-history', views.SprintEffortsHistoryViewSet, basename='sprint-estimations')
router.register('sprint-durations', views.SprintDurationViewSet, basename='sprint-durations')
router.register('working-days', views.ProjectWorkingDaysViewSet, basename='working-days')
router.register('non-working-days', views.ProjectNonWorkingDayViewSet, basename='non-working-days')

urlpatterns = router.urls
urlpatterns += [path('issue/ordering/',
                     views.IssueListUpdateApiView.as_view(),
                     name='issue-ordering'),
                path('person-invitation-requests/',
                     views.PersonInvitationRequestListCreateView.as_view(),
                     name='person-invitations-requests-list'),
				path('person-invitation-requests/<key>/',
					 PersonInvitationRequestRetrieveUpdateView.as_view(),
					 name='person-invitations-requests-detail'),
                path('issue-messages-packed/<int:issue_id>/',
                     views.IssueMessagesPackedView.as_view(),
                     name='issue-messages-packed')]
