from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def username_validator(username):
    invalid_username = 'me'
    if username == invalid_username:
        raise ValidationError(
            _(
                '%(username)s недопустимо использовать как имя пользователя.'
            ),
            params={'username': username},
        )
    return username
