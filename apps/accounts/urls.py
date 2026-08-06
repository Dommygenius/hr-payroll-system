from django.contrib.auth import views as auth_views
from django.urls import path

from apps.accounts.forms import PasswordChangeForm
from apps.accounts.views import profile_view


class TenantLoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['auth_layout'] = True
        return context

    def get_success_url(self):
        from django.conf import settings
        from apps.core.tenant import get_portal_path
        tenant = getattr(self.request, 'tenant', None)
        if tenant:
            return get_portal_path(tenant.slug, '/dashboard/')
        company = getattr(self.request.user, 'company', None)
        if company:
            return get_portal_path(company.slug, '/dashboard/')
        return settings.LOGIN_REDIRECT_URL


class TenantLogoutView(auth_views.LogoutView):
    def get_next_page(self):
        from apps.core.tenant import get_portal_path
        tenant = getattr(self.request, 'tenant', None)
        if tenant:
            return get_portal_path(tenant.slug, '/accounts/login/')
        return super().get_next_page()


urlpatterns = [
    path('login/', TenantLoginView.as_view(), name='login'),
    path('logout/', TenantLogoutView.as_view(), name='logout'),
    path('profile/', profile_view, name='accounts-profile'),
    path(
        'password-change/',
        auth_views.PasswordChangeView.as_view(
            template_name='accounts/password_change.html',
            form_class=PasswordChangeForm,
            success_url='/accounts/profile/',
        ),
        name='password_change',
    ),
]
