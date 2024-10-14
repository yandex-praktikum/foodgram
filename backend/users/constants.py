"""Константы."""

MAX_LEN_EMAIL = 254
MAX_LEN_USERNAME = 150
MAX_LEN_FIRST_NAME = 150
MAX_LEN_LAST_NAME = 150

RESTRICTED_USERNAMES = ('me', 'admin', 'null')
HTTP_METHOD_NAMES = ('get', 'post', 'delete', 'head',
                     'options', 'trace', 'patch')

USER = 'user'
ADMIN = 'admin'
ROLES = [
    (USER, 'user'),
    (ADMIN, 'admin')
]
