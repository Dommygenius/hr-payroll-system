from django.contrib.auth import views as auth_views
from django.urls import path

from apps.accounts.forms import PasswordChangeForm
from apps.accounts.views import profile_view

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
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
