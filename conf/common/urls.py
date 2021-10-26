from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenRefreshView

from apps.core.api.views import PersonRegistrationRequestVerifyView, \
	PersonSetPasswordView, \
	UserUpdateView, \
	PersonAvatarUpload, \
	PersonRegistrationRequestView, \
	PersonForgotPasswordRequestConfirmView, \
	CheckConnection, SprintGuidelineView

from apps.core.api.views import TokenObtainPairExtendedView
from apps.core.views import MainView

API_TITLE = 'PmDragon API'
API_DESCRIPTION = 'Web API for PmDragon service'
schema_url_patterns = [
	url(r'^api/', include('apps.core.api.urls'))
]

schema_view = get_schema_view(
	openapi.Info(
		title="PmDragon API",
		default_version='v1',
		description="Swagger documentation for PmDragon API",
		contact=openapi.Contact(email="cybersturmer@ya.ru"),
		license=openapi.License(name="MIT License"),
	),
	public=True,
	permission_classes=(AllowAny,),
)

app_name = 'auth_api'

urlpatterns = [
	path('', MainView.as_view()),
	path('admin/', admin.site.urls),
	path('login/', auth_views.LoginView.as_view(), name='login'),

	path('schema/', schema_view.without_ui(cache_timeout=0), name='openapi-schema'),

	path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

	path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc-ui'),

	path('api/check/',
		 CheckConnection.as_view(),
		 name='check_connection'),

	path('api/auth/obtain/',
		 TokenObtainPairExtendedView.as_view(),
		 name='token-obtain'),

	path('api/auth/refresh/',
		 TokenRefreshView.as_view(),
		 name='token-refresh'),

	path('api/auth/password/change/',
		 PersonSetPasswordView.as_view(),
		 name='person_set_password'),

	path('api/auth/person-password-forgot-requests/',
		 PersonForgotPasswordRequestConfirmView.as_view({'post': 'create'}),
		 name='person-forgot-requests-list'),

	path('api/auth/person-password-forgot-requests/<key>/',
		 PersonForgotPasswordRequestConfirmView.as_view({
			 'get': 'retrieve',
			 'patch': 'partial_update'
		 }),
		 name='person-forgot-requests-detail'),

	path('api/auth/persons/',
		 PersonRegistrationRequestVerifyView.as_view(),
		 name='person_create'),

	path('api/auth/person-registration-requests/',
		 PersonRegistrationRequestView.as_view({'post': 'create'}),
		 name='person-registration-requests-list'),

	path('api/auth/person-registration-requests/<key>/',
		 PersonRegistrationRequestView.as_view({'get': 'retrieve'}),
		 name='person-registration-requests-detail'),

	path('api/core/sprint-guideline/<key>/',
		 SprintGuidelineView.as_view(),
		 name='sprint-guideline'),

	path('api/auth/me/',
		 UserUpdateView.as_view(),
		 name='me'),

	path('api/auth/avatar/',
		 PersonAvatarUpload.as_view(),
		 name='avatar'),

	path('api/core/', include('apps.core.api.urls', namespace='core_api'))
]

# @todo Refactor it.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
