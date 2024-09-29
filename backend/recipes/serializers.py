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
    RecipeTag,
    ShortLink,
    Subscriber,
    UserFavoriteRecipe,
    UserShoppingCartRecipe,
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


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей.
    """

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'avatar',
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


class UserRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта пользователя.
    """

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class UserRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов пользователя.
    """

    model_name = ''

    class Meta:
        fields = (
            'user',
            'recipe',
        )
        read_only_fields = ('user',)

    def validate(self, data):
        user = self.context.get('request').user
        recipe = data.get('recipe')
        if self.Meta.model.objects.filter(
            user=user,
            recipe=recipe,
        ).exists():
            raise ValidationError(
                f'Рецепт уже добавлен в {self.model_name}'
            )
        return data

    def to_representation(self, instance):
        return UserRecipeSerializer(
            instance.recipe,
            context=self.context,
        ).data


class UserFavoriteRecipeSerializer(UserRecipesSerializer):
    """Сериализатор модели UserFavoriteRecipe.
    """

    model_name = 'избранное'

    class Meta(UserRecipesSerializer.Meta):
        model = UserFavoriteRecipe


class UserShoppingCartRecipesSerializer(UserRecipesSerializer):
    """Сериализатор модели UserFavoriteRecipe.
    """

    model_name = 'корзина рецептов'

    class Meta(UserRecipesSerializer.Meta):
        model = UserShoppingCartRecipe


# Переделать
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
    amount = serializers.ReadOnlyField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeTagSerializer(serializers.ModelSerializer):
    """Сериализатор чтения списка тэгов рецепта.
    """
    id = serializers.ReadOnlyField(
        source='tag.id'
    )
    name = serializers.ReadOnlyField(
        source='tag.name'
    )
    slug = serializers.ReadOnlyField(
        source='tag.slug'
    )

    class Meta:
        model = RecipeTag
        fields = (
            'id',
            'name',
            'slug',
        )


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
        source='recipe_ingredients',
        read_only=True,
        many=True,
    )
    tags = RecipeTagSerializer(
        source='recipe_tags',
        read_only=True,
        many=True,
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
            'id',
            'name',
            'image',
            'text',
            'cooking_time',
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
            and UserFavoriteRecipe.objects.filter(
                user=self.context['request'].user,
                recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and UserShoppingCartRecipe.objects.filter(
                user=self.context['request'].user,
                recipe=obj
            ).exists()
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания ингредиента рецепта.
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )


class RecipeCUDSerializer(serializers.ModelSerializer):
    """Сериализатор создания, удаления и редактирования рецептов.
    """

    image = Base64ImageField()
    ingredients = RecipeIngredientCreateSerializer(
        source='recipe_ingredients',
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )

    @staticmethod
    def _set_ingredients_and_tags(ingredients, tags, recipe):
        recipe.tags.set(tags)
        recipe_ingredients = []
        for ingredient in ingredients:
            recipe_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient.get('ingredient'),
                    amount=ingredient.get('amount'),
                )
            )
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def validate(self, data):
        tags = data.get('tags', [])
        if not tags:
            raise ValidationError(
                'Добавьте тэг к рецепту.'
            )

        if len(tags) != len(set(tags)):
            raise ValidationError(
                'Нельзя добавлять одинаковые тэги.'
            )

        ingredients = data.get('recipe_ingredients', [])
        if not ingredients:
            raise ValidationError('Не добавлен ингредиент(ы).')

        unique_ingredients = set()
        for ingredient in ingredients:
            unique_ingredient = ingredient.get('ingredient')
            unique_ingredients.add(unique_ingredient)

        if len(ingredients) != len(unique_ingredients):
            raise ValidationError(
                'Нельзя добавлять одинаковые ингредиенты в рецепт.'
            )

        return data

    def validate_image(self, data):
        if not data:
            raise serializers.ValidationError(
                'Изображение - обязательное поле.'
            )
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_ingredients', [])
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(
            author=self.context.get('request').user, **validated_data,
        )
        self._set_ingredients_and_tags(
            ingredients,
            tags,
            recipe,
        )
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipe_ingredients', [])
        tags = validated_data.pop('tags', [])
        instance.ingredients.clear()
        instance.tags.clear()
        self._set_ingredients_and_tags(
            ingredients,
            tags,
            instance,
        )
        return super().update(instance, validated_data)

    class Meta:
        model = Recipe
        fields = (
            'name',
            'image',
            'text',
            'cooking_time',
            'ingredients',
            'tags',
        )

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class ShortLinkSerializer(serializers.ModelSerializer):
    """Сериализатор для модели коротких ссылок.
    """

    class Meta:
        model = ShortLink
        fields = '__all__'

    def create(self, validated_data):
        full_url = validated_data['full_url']
        short_url, _ = ShortLink.objects.get_or_create(
            full_url=full_url,
        )
        return short_url

    def to_representation(self, instance):
        return {'short-link': instance}
