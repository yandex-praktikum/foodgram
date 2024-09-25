"""Сериализаторы.

backend/recipes/serializers.py
"""


from django.contrib.auth import get_user_model
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.validators import UniqueTogetherValidator


from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    RecipeIngredient,
    Subscriber,
    UserFavoriteRecipes,
    UserShoppingCartRecipes,
)

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов.
    """

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов.
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


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей.
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
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, object):
        user = self.context.get('request').user
        return Subscriber.objects.filter(
            user=user.id, author=object
        ).exists()


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор аватаров пользователей.
    """

    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = (
            'avatar',
        )

    def validate_avatar(self, data):
        if not data:
            raise serializers.ValidationError(
                'Аватар необходимо указать!.'
            )
        return data


class UserRecipesSerializer(UserSerializer):
    """Сериализатор рецептов пользователей.
    """

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta(UserSerializer.Meta):
        model = User
        #fields = (
        #    UserSerializer.Meta.fields[:BASE_USER_FIELDS_LIMIT] + (
        #        'recipes',
        #        'recipes_count',
        #        'avatar',
        #    )
        #)

    def get_recipes(self, obj):
        request = self.context.get('request')
        queryset = obj.recipes.all()
        limit = request.query_params.get('recipes_limit')
        if limit:
            try:
                queryset = queryset[:int(limit)]
            except (TypeError, ValueError):
                pass
        return UserRecipesSerializer(  # ВНИМАНИЕ!!! Сам себя возвращает?
            queryset,
            many=True,
        ).data


class SubscriberSerializer(serializers.ModelSerializer):
    """Сериализатор подписчикиов.
    """

    class Meta:
        model = Subscriber
        fields = (
            'author',
            'user',
        )
        validators = [
            UniqueTogetherValidator(
                fields=('author', 'user'),
                queryset=model.objects.all(),
                message='Вы уже подписаны на этого автора.',
            )
        ]

    def validate_author(self, data):
        if self.context.get('request').user == data:
            raise ValidationError(
                'Подписаться на себя нельзя.'
            )
        return data

    def to_representation(self, instance):
        return UserRecipesSerializer(
            instance.author,
            context=self.context,
        ).data


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
