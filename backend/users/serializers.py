import base64

from django.core.files.base import ContentFile
from django.core.validators import MaxLengthValidator, RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from food.models import Subscribe
from users.models import User

from .constants import (MAX_LEN_EMAIL, MAX_LEN_FIRST_NAME, MAX_LEN_LAST_NAME,
                        MAX_LEN_USERNAME)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели пользователей"""
    username = serializers.CharField(
        max_length=MAX_LEN_USERNAME,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            MaxLengthValidator(MAX_LEN_USERNAME),
            RegexValidator(r'^[\w.@+-]+$',
                           message='Username must consist of letters,'
                           'digits, or @.+_ characters.')
        ]
    )
    email = serializers.CharField(
        max_length=MAX_LEN_EMAIL,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            MaxLengthValidator(MAX_LEN_EMAIL),
        ])
    first_name = serializers.CharField(
        max_length=MAX_LEN_FIRST_NAME,
        validators=[
            MaxLengthValidator(MAX_LEN_FIRST_NAME),
        ]
    )
    last_name = serializers.CharField(
        max_length=MAX_LEN_LAST_NAME,
        validators=[
            MaxLengthValidator(MAX_LEN_LAST_NAME),
        ]
    )

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'is_subscribed': {'read_only': True},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.name)
        instance.last_name = validated_data.get('last_name', instance.name)
        instance.image = validated_data.get('image', instance.image)

        instance.save()
        return instance


class UserListRetrieveSerializer(serializers.ModelSerializer):
    """Сериализатор модели пользователей для чтения"""
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField('get_avatar_url',)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password', 'is_subscribed',
                  'avatar')
        extra_kwargs = {
            'password': {'write_only': True},
            'is_subscribed': {'read_only': True},
        }

    def get_avatar_url(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None

    def get_is_subscribed(self, obj):
        request_user = self.context.get('request').user
        if not request_user.is_anonymous:
            # user это пользователь у которого нужно проверить
            # подписку на author автора рецепта
            return Subscribe.objects.filter(
                user=request_user, author=obj
            ).exists()
        return False


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserUpdateAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор обновления аватара пользователя."""
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def get_avatar_url(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None


class SetPasswordSerrializer(serializers.Serializer):
    """Сериализатор для смены пароля пользователя."""
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('current_password', 'new_password')
