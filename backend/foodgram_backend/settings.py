"""Настройки Django для проекта foodgram_backend.

"""

from pathlib import Path

from .constants import PGINATION_PAGE_SIZE

# Создайте пути внутри проекта следующим образом: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ПРЕДУПРЕЖДЕНИЕ ПО БЕЗОПАСНОСТИ: храните секретный ключ, используемый в рабочей среде, в секрете!
SECRET_KEY = 'django-insecure-0t2za3mlh@(8)94t1*am$#nx!x-3v5_40jxa2un2$*-b=ycqd6'

# ПРЕДУПРЕЖДЕНИЕ ПО БЕЗОПАСНОСТИ: не запускайте программу в режиме отладки в рабочей среде!
DEBUG = True

# Cписок сайтов, с которыми приложение может устанавливать соединение и принимать запросы.
ALLOWED_HOSTS = ['*']


# Определение используемых приложений
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'djoser',
    'rest_framework',
    'rest_framework.authtoken',
    'recipes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Файл URL-адресов.
ROOT_URLCONF = 'foodgram_backend.urls'

# Шаблоны
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# 
WSGI_APPLICATION = 'foodgram_backend.wsgi.application'


# База данных

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Проверка пароля
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 9,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Интернационализация
LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Asia/Yekaterinburg'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Статические файлы (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Тип поля первичного ключа по умолчанию
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Переопределение модели пользователя по умолчанию
AUTH_USER_MODEL = 'recipes.User'

# Настройки djoser
DJOSER = {
    'LOGIN_FIELD': 'email',
    'HIDE_USERS': False,
    'SERIALIZERS': {
        'current_user': 'recipes.serializers.UserSerializer',
        'user': 'recipes.serializers.UserSerializer',
        'user_list': 'recipes.serializers.UserSerializer',
    },
    'PERMISSIONS': {
        'current_user': ('djoser.permissions.CurrentUserOrAdminOrReadOnly',),
        'user': ('djoser.permissions.CurrentUserOrAdminOrReadOnly',),
        'user_create': ('rest_framework.permissions.AllowAny',),
        'user_list': ('rest_framework.permissions.AllowAny',),
    }
}

# Настройки rest_framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': PGINATION_PAGE_SIZE,
}
