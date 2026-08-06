from django import forms
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from apps.core.models import Company


class PasswordChangeForm(DjangoPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class TenantRegistrationForm(forms.Form):
    company_name = forms.CharField(
        max_length=255,
        label='Organization name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Acme Corporation'}),
    )
    company_slug = forms.SlugField(
        max_length=100,
        label='Your portal link name',
        help_text='Used in your unique URL, e.g. /t/acme-corp/',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'acme-corp'}),
    )
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    admin_email = forms.EmailField(
        label='Work email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@company.com'}),
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    password2 = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def clean_company_slug(self):
        slug = self.cleaned_data['company_slug'].lower()
        if Company.objects.filter(slug=slug).exists():
            raise ValidationError('This portal name is already taken. Choose another.')
        return slug

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError('Passwords do not match.')
        if p1:
            validate_password(p1)
        return cleaned

    def suggest_slug(self):
        name = self.data.get('company_name', '')
        base = slugify(name)[:80] or 'organization'
        slug = base
        n = 1
        while Company.objects.filter(slug=slug).exists():
            slug = f'{base}-{n}'
            n += 1
        return slug
