"""django-allauth adapters — bind social/signup users to the active tenant company."""
from __future__ import annotations

from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.shortcuts import redirect

from apps.core.models import Company


def resolve_oauth_company(request):
    """Prefer request.tenant, then session stash from tenant login portal."""
    tenant = getattr(request, 'tenant', None)
    if tenant is not None:
        return tenant
    company_id = request.session.get('oauth_company_id')
    if not company_id:
        return None
    return Company.objects.filter(pk=company_id, is_active=True).first()


class HrmsAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        company = resolve_oauth_company(request)
        if company and not user.company_id:
            user.company = company
        if commit:
            user.save()
        return user


class HrmsSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        company = resolve_oauth_company(request)
        if not company:
            return
        if sociallogin.is_existing:
            existing = sociallogin.user
            if existing.company_id and existing.company_id != company.id:
                messages.error(
                    request,
                    'This social account belongs to a different organization. '
                    'Sign in from that organization’s portal.',
                )
                login_path = '/accounts/login/'
                if company.slug:
                    login_path = f'/t/{company.slug}/accounts/login/'
                raise ImmediateHttpResponse(redirect(login_path))

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        company = resolve_oauth_company(request)
        if company and not getattr(user, 'company_id', None):
            user.company = company
        return user

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form=form)
        company = resolve_oauth_company(request)
        if company and not user.company_id:
            user.company = company
            user.save(update_fields=['company'])
        return user
