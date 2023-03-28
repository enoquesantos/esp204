from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.urls import re_path
from django.views.generic.base import RedirectView
from django.views.generic.base import TemplateView

from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenVerifyView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.config import views as config_views

admin.site.index_template = settings.BASE_DIR + "/templates/admin/index.html"
admin.autodiscover()

# custom error pages in admin
handler400 = 'apps.config.views.bad_request'
handler403 = 'apps.config.views.permission_denied'
handler404 = 'apps.config.views.page_not_found'
handler500 = 'apps.config.views.server_error'

urlpatterns = [
    # home do site default
    re_path(r'^$', config_views.home, name='home'),

    # advanced editor
    path('tinymce/', include('tinymce.urls')),

    # admin login view
    re_path(r'^admin/login/', config_views.login_view),

    # django admin url's
    path('admin/', admin.site.urls),

    # rest framework auth (token creation and refresh)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # manifest, icons and logo
    path('favicon.ico', RedirectView.as_view(url=settings.MEDIA_URL + "assets/favicon.ico")),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),

    # request to create new password view (with email input form)
    path('accounts/password-reset/', config_views.password_reset, name="password_reset"),

    # view to confirm new password creation (with two pass inputs form...)
    path('accounts/password-reset-confirm/<uidb64>/<token>/', config_views.PasswordResetConfirmViewCustom.as_view(template_name="accounts/password_reset_confirm.html"), name='password_reset_confirm'),

    # last password view with only success message
    re_path('reset/done/', config_views.PasswordResetCompleteViewCustom.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)