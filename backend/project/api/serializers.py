from tag.models import Tag
from recipe.models import (
    Recipe,
    RecipeIngredient,
    FavoriteRecipe,
    ShoppingList,
)
from ingredient.models import Ingredient
from users.models import User, Follow
from rest_framework.serializers import (
    ModelSerializer,
    PrimaryKeyRelatedField,
    ReadOnlyField,
)
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
import logging

logger = logging.getLogger(__name__)


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class UserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)
    avatar = Base64ImageField(max_length=None)

    def get_is_subscribed(self, obj: User) -> bool:
        request: Request = self.context["request"]
        if self.context["request"].user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj.id).exists()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "password")


class RecipeIngredientSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = ReadOnlyField(source="ingredient.name")
    measurement_unit = ReadOnlyField(source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeReadSerializer(ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True, many=False)
    ingredients = RecipeIngredientSerializer(many=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField(max_length=None)

    def get_is_favorited(self, obj: Recipe) -> bool:
        request: Request = self.context["request"]
        if request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj: Recipe) -> bool:
        request: Request = self.context["request"]
        if request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )


class RecipeWriteSerializer(ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    tags = PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )

    def create_ingredients(self, recipe: Recipe, ingredients_data: dict):
        ingredient_liist = []
        for ingredient_data in ingredients_data:
            ingredient_liist.append(
                RecipeIngredient(
                    ingredient=ingredient_data.pop("id"),
                    amount=ingredient_data.pop("amount"),
                    recipe=recipe,
                )
            )
        RecipeIngredient.objects.bulk_create(ingredient_liist)

    def create(self, data: dict) -> Recipe:
        request: Request = self.context["request"]
        ingredients_data = data.pop("ingredients")
        tags_data = data.pop("tags")
        recipe = Recipe.objects.create(author=request.user, **data)
        recipe.tags.set(tags_data)
        self.create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance: Recipe, data: dict):
        instance.tags.clear()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        instance.tags.set(data.pop("tags"))
        ingredients = data.pop("ingredients")
        self.create_ingredients(instance, ingredients)
        return super().update(instance, data)

    def to_representation(self, instance: Recipe):
        return RecipeReadSerializer(
            instance, context={"request": self.context.get("request")}
        ).data


class ShoppingCartSerializer(ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = (
            "user",
            "recipe",
        )

    def create(self, data: dict):
        request: Request = self.context["request"]
        recipe = data["recipe"]

        if ShoppingList.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            raise ValidationError("Этот рецепт уже добавлен в корзину.")

        shopping_list = ShoppingList.objects.create(
            user=request.user, recipe=recipe
        )
        return shopping_list


class FavoriteSerializer(ModelSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = ("user", "recipe")

    def validate(self, data: dict) -> dict:
        user = data["user"]
        if user.favorites.filter(recipe=data["recipe"]).exists():
            raise ValidationError("Рецепт уже добавлен в избранное.")
        return data


class RecipeSmallSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class AuthorSerializer(UserSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("recipes_count", "recipes")
        read_only_fields = ("email", "username", "first_name", "last_name")

    def get_recipes(self, obj: User):
        request: Request = self.context["request"]
        limit = request.GET.get("recipes_limit")
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = RecipeSmallSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj: User) -> int:
        return obj.recipes.count()
