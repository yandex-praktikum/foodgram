from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def username_validator(username):
    invalid_usernames = [
        'admin',
        'adminadmin',
        'admin_admin',
        'me',
        'meme',
        'mememe',
        'password',
        'set_password',
        'subscriptions',
        'subscribe',
        'subscriber',
        'superuser',
        'super_user',
        'user'
    ]
    if username in invalid_usernames:
        raise ValidationError(
            _(
                '%(username)s недопустимо использовать как имя пользователя.'
            ),
            params={'username': username},
        )
    return username


def password_validator(password):
    pass
