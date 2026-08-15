from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class LockedModelBackend(ModelBackend):
    """Django ModelBackend that honors account lockout."""

    def user_can_authenticate(self, user):
        if user is not None and getattr(user, 'is_locked', False):
            return False
        return super().user_can_authenticate(user)


class EmailOrPhoneBackend(LockedModelBackend):
    """Authenticate using email or phone number."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email') or kwargs.get('phone')
        if username is None or password is None:
            return None

        try:
            if '@' in username:
                user = User.objects.get(email__iexact=username)
            else:
                user = User.objects.get(phone=username)
        except User.DoesNotExist:
            User().set_password(password)
            return None

        if not self.user_can_authenticate(user):
            return None

        if user.check_password(password):
            user.reset_failed_logins()
            return user

        user.record_failed_login()
        return None


class LDAPBackend(LockedModelBackend):
    """LDAP/Active Directory authentication (optional). Does not auto-provision users."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        from django.conf import settings

        if not settings.LDAP_SERVER_URI:
            return None

        try:
            import ldap

            conn = ldap.initialize(settings.LDAP_SERVER_URI)
            conn.simple_bind_s(settings.LDAP_BIND_DN, settings.LDAP_BIND_PASSWORD)
            safe_username = ldap.filter.escape_filter_chars(username or '')
            result = conn.search_s(
                settings.LDAP_USER_SEARCH_BASE,
                ldap.SCOPE_SUBTREE,
                f'(sAMAccountName={safe_username})',
            )
            if not result:
                return None

            user_dn = result[0][0]
            conn.simple_bind_s(user_dn, password)

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None
            if not self.user_can_authenticate(user):
                return None
            return user
        except ImportError:
            return None
        except Exception:
            return None
