"""Сериализаторы.

backend/recipes/serializers.py
"""
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.tokens import default_token_generator
from django.core import exceptions as django_exceptions
from django.core.validators import EmailValidator
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ValidationError


from recipes.constants import (
    USERNAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    FIRST_NAME_MAX_LENGTH,
    LAST_NAME_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
)
from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    RecipeIngredient,
    UserFavoriteRecipes,
    UserShoppingCartRecipes,
    UserSubscription,
)
from recipes.validators import (
    username_validator,
    password_validator
)

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор чтения списка ингредиентов.
    """

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор чтения тегов .
    """

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug',
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор чтения списка ингредиентов рецепта.
    """
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class UserSerializer(UserSerializer):
    """Сериализатор чтения пользователей.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'is_subscribed',
        )

    def get_is_subscribed(self, object):
        if (
            self.context.get('request')
            and not self.context['request'].user.is_anonymous
        ):
            return UserSubscription.objects.filter(
                user=self.context['request'].user,
                author=object
            ).exists()
        return False


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя.
    """
    username = serializers.CharField(
        required=True,
        max_length=USERNAME_MAX_LENGTH,
        validators=[
            UnicodeUsernameValidator(
                message=(
                    'Имя пользователя содержит недопустимые символы. '
                    'В имени пользователя допускается использовать буквы, '
                    'цифры и символы _.@+-'
                )
            ),
            username_validator
        ]
    )
    email = serializers.EmailField(
        required=True,
        max_length=EMAIL_MAX_LENGTH,
        validators=[EmailValidator]
    )
    first_name = serializers.CharField(
        max_length=FIRST_NAME_MAX_LENGTH,
        required=True,
    )
    last_name = serializers.CharField(
        max_length=LAST_NAME_MAX_LENGTH,
        required=True,
    )
    password = serializers.CharField(
        required=True,
        min_length=PASSWORD_MIN_LENGTH,
        validators=[password_validator]
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
        )

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')
        user_by_email = User.objects.filter(email=email).first()
        user_by_username = User.objects.filter(username=username).first()
        errors = {}
        if user_by_email and not user_by_username:
            errors["email"] = [f'Пользователь с {email} уже существует.']
        elif not user_by_email and user_by_username:
            errors["username"] = [f'Пользователь {username} уже существует.']
        else:
            if user_by_email != user_by_username:
                errors["email"] = [
                    f'Пользователь с {email} уже существует, '
                    f'и это не {username}.'
                ]
                errors["username"] = [
                    f'Пользователь {username} уже существует, '
                    'и у него другой адрес электронной почты.'
                ]
        if errors:
            raise ValidationError(errors)
        return data


class UserConfirmationCodeSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=USERNAME_MAX_LENGTH,
        validators=[
            UnicodeUsernameValidator(
                message=(
                    'Имя пользователя содержит недопустимые символы. '
                    'В имени пользователя допускается использовать буквы, '
                    'цифры и символы _.@+-'
                )
            ),
            username_validator,
        ]
    )
    confirmation_code = serializers.CharField(
        required=True
    )

    def validate(self, data):
        user = get_object_or_404(User, username=data['username'])
        if not default_token_generator.check_token(
            user, data['confirmation_code']
        ):
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения'}
            )
        return data


class UserPasswordChangSerializer(serializers.Serializer):
    """Сериализатор для изменения пароля пользователя.
    """
    current_password = serializers.CharField()
    new_password = serializers.CharField(
        validators=[password_validator]
    )

    def validate(self, data):
        current_password = data['current_password']
        new_password = data['new_password']
        user = self.context['request'].user
        errors = {}
        try:
            validate_password(new_password)
        except django_exceptions.ValidationError as e:
            errors["new_password"] = [
                e.messages
            ]
        if not authenticate(username=user, password=current_password):
            errors["current_password"] = [
                'Введен неправильный пароль.'
            ]
        if (
            current_password == new_password
        ):
            errors["new_password"] = [
                'Новый пароль должен отличаться от текущего.'
            ]
        if errors:
            raise ValidationError(errors)
        return data

    def update(self, data):
        User.objects.filter(
            username=self.context['request'].user
        ).update(
            password=make_password(data.get('new_password'))
        )
        return data


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор чтения рецептов.
    """
    image = Base64ImageField(
        read_only=True,
        allow_null=True
    )
    author = UserSerializer(
        read_only=True
    )
    ingredients = RecipeIngredientSerializer(
        source='recipes',
        read_only=True,
        many=True,
    )
    tags = TagSerializer(
        read_only=True,
        many=True
    )
    is_favorited = serializers.SerializerMethodField(
        read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'name',
            'image',
            'text',
            'cooking_time',
            'pub_date',
            'author',
            'ingredients',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )
        read_only_fields = ('author',)

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_is_favorited(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and UserFavoriteRecipes.objects.filter(
                user=self.context['request'].user,
                recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and UserShoppingCartRecipes.objects.filter(
                user=self.context['request'].user,
                recipe=obj
            ).exists()
        )


class UserFavoriteRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор чтения избранных рецептов пользователя.
    """
    id = serializers.IntegerField(
        source='recipe.id'
    )
    name = serializers.CharField(
        source='recipe.name'
    )
    image = Base64ImageField(
        source='recipe.image'
    )
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time'
    )

    class Meta:
        model = UserFavoriteRecipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if UserFavoriteRecipes.objects.filter(
                user=user,
                recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                f'Рецепт {recipe} уже есть в Избранном пользователя {user}'
            )
        return data


class UserShoppingCartRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор чтения корзины рецептов пользователя.
    """
    id = serializers.IntegerField(
        source='recipe.id'
    )
    name = serializers.CharField(
        source='recipe.name'
    )
    image = Base64ImageField(
        source='recipe.image'
    )
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time'
    )

    class Meta:
        model = UserShoppingCartRecipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if UserShoppingCartRecipes.objects.filter(
                user=user,
                recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                f'Рецепт {recipe} уже есть в корзине пользователя {user}'
            )
        return data


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор чтения подписок пользователя.
    """
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and UserSubscription.objects.filter(
                user=self.context['request'].user,
                author=obj
            ).exists()
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class UserSubscriptionChangSerializer(serializers.ModelSerializer):
    """Сериализатор изменения подписок пользователя.
    """
    username = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def validate(self, obj):
        if (self.context['request'].user == obj):
            raise serializers.ValidationError({'errors': 'Ошибка подписки.'})
        return obj

    def get_is_subscribed(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and UserSubscription.objects.filter(
                user=self.context['request'].user,
                author=obj
            ).exists()
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
