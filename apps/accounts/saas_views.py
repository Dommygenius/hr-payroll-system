"""Web views for SaaS tenant registration and portal."""
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.accounts.forms import TenantRegistrationForm
from apps.core.tenant import bootstrap_tenant, get_portal_url


@require_http_methods(['GET', 'POST'])
def tenant_register_view(request):
    if request.user.is_authenticated and getattr(request.user, 'company', None):
        return redirect(get_portal_url(request.user.company.slug, '/dashboard/', request))

    form = TenantRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        company, user = bootstrap_tenant(
            company_name=form.cleaned_data['company_name'],
            slug=form.cleaned_data['company_slug'],
            admin_email=form.cleaned_data['admin_email'],
            password=form.cleaned_data['password1'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
        )
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        portal_url = get_portal_url(company.slug, '/dashboard/', request)
        return render(request, 'accounts/register_complete.html', {
            'company': company,
            'portal_url': portal_url,
            'login_url': get_portal_url(company.slug, '/accounts/login/', request),
            'auth_layout': True,
        })

    suggested = form.suggest_slug() if request.method == 'GET' else form.data.get('company_slug', '')
    if request.method == 'GET' and not form.data:
        form = TenantRegistrationForm(initial={'company_slug': suggested})
    return render(request, 'accounts/register.html', {
        'form': form,
        'suggested_slug': suggested,
        'auth_layout': True,
    })


@require_http_methods(['GET'])
def saas_landing_view(request):
    from apps.core.tenant import get_portal_url

    tenant = getattr(request, 'tenant', None)
    if tenant:
        if request.user.is_authenticated:
            return redirect(get_portal_url(tenant.slug, '/dashboard/', request))
        return redirect(get_portal_url(tenant.slug, '/accounts/login/', request))

    if request.user.is_authenticated:
        company = getattr(request.user, 'company', None)
        if company:
            return redirect(get_portal_url(company.slug, '/dashboard/', request))
    return render(request, 'landing.html', {'auth_layout': True})
