import secrets

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailOrPhoneBackend(ModelBackend):
    """Authenticate using email or phone number."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email') or kwargs.get('phone')
        if username is None or password is None:
            return None

        user = None
        try:
            if '@' in username:
                user = User.objects.get(email__iexact=username)
            else:
                user = User.objects.get(phone=username)
        except User.DoesNotExist:
            User().set_password(password)
            return None

        if user.is_locked:
            return None

        if user.check_password(password):
            user.reset_failed_logins()
            return user

        user.record_failed_login()
        return None


class LDAPBackend(ModelBackend):
    """LDAP/Active Directory authentication (optional)."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        from django.conf import settings

        if not settings.LDAP_SERVER_URI:
            return None

        try:
            import ldap
            from django_auth_ldap.config import LDAPSearch

            conn = ldap.initialize(settings.LDAP_SERVER_URI)
            conn.simple_bind_s(settings.LDAP_BIND_DN, settings.LDAP_BIND_PASSWORD)
            result = conn.search_s(
                settings.LDAP_USER_SEARCH_BASE,
                ldap.SCOPE_SUBTREE,
                f'(sAMAccountName={username})',
            )
            if not result:
                return None

            user_dn = result[0][0]
            conn.simple_bind_s(user_dn, password)

            company = getattr(request, 'tenant', None) if request is not None else None
            try:
                user = User.objects.get(username=username)
                if company and not user.company_id:
                    user.company = company
                    user.save(update_fields=['company'])
                return user
            except User.DoesNotExist:
                return User.objects.create_user(
                    username=username,
                    email=f'{username}@ldap.local',
                    password=secrets.token_urlsafe(32),
                    company=company,
                )
        except ImportError:
            return None
        except Exception:
            return None
