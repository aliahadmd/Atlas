from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
from django.conf import settings
from allauth.account.decorators import secure_admin_login
from django.views.generic.base import TemplateView
from django.views.generic import TemplateView


admin.autodiscover()
admin.site.login = secure_admin_login(admin.site.login)

urlpatterns = [
    path('', TemplateView.as_view(template_name='homepage.html'), name='homepage'),
    path('rm/', include('risk_management.urls')),
    path('pm/', include('portfolio_management.urls')),
    path('accounts/', include('allauth.urls')),
    path("accounts/profile/", TemplateView.as_view(template_name="profile.html"), name='dj-allauth-profile'),
    path('admin/', admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    
]


urlpatterns += [
        path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
        path('static/<path:path>', serve, {'document_root': settings.STATIC_ROOT}),
    ]
