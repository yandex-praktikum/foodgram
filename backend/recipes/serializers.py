"""backend/recipes/serializers.py

"""
from django.contrib.auth import get_user_model
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Ingredient,
    Tag,
    RecipeIngredient,
    Recipe,
)

User = get_user_model()

class IngredientReadSerializer(serializers.ModelSerializer):
    """Сериализатор чтения списка ингредиентов.
    """

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class TagReadSerializer(serializers.ModelSerializer):
    """Сериализатор чтения тегов .
    """

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug',
        )


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
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


class UserReadSerializer(serializers.ModelSerializer):
    pass


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор чтения рецептов.
    """
    image = Base64ImageField(
        read_only=True,
        allow_null=True
    )
    author = UserReadSerializer(
        read_only=True
    )
    ingredients = RecipeIngredientReadSerializer(
        source='recipes',
        read_only=True, 
        many=True, 
    )
    tags = TagReadSerializer(
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
            'name', 'image', 'image_url', 'text', 'cooking_time',
            'pub_date', 'author', 'ingredients', 'tags',
            'is_favorited', 'is_in_shopping_cart',
        )
        read_only_fields = ('author',)

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_is_favorited(self, obj):
        pass
        #return (
        #    self.context.get('request').user.is_authenticated
        #    and Favorite.objects.filter(
        #        user=self.context['request'].user, recipe=obj
        #    ).exists()
        #)

    def get_is_in_shopping_cart(self, obj):
        pass
        #return (
        #    self.context.get('request').user.is_authenticated
        #    and ShoppingCart.objects.filter(
        #        user=self.context['request'].user,
        #        recipe=obj
        #    ).exists()
        #)

