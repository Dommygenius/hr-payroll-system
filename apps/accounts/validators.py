import re

from django.core.exceptions import ValidationError


class PasswordComplexityValidator:
    """Require uppercase, lowercase, digit, and special character."""

    def validate(self, password, user=None):
        if len(password) < 10:
            raise ValidationError('Password must be at least 10 characters long.')
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one digit.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character.')

    def get_help_text(self):
        return (
            'Your password must be at least 10 characters and contain uppercase, '
            'lowercase, digit, and special character.'
        )
