from django.core.validators import MaxLengthValidator, RegexValidator
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from food.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                         ShoppingCart, ShortLink, Subscribe, Tag)
from users.serializers import Base64ImageField, UserListRetrieveSerializer

from . import constants


class TagSerializer(serializers.ModelSerializer):
    """Serializer для модели Tag."""
    name = serializers.CharField(
        max_length=constants.MAX_LEN_TAG_NAME,
        validators=[
            MaxLengthValidator(constants.MAX_LEN_TAG_NAME,
                               message='Max tag name length – 32 characters'),
        ]
    )
    slug = serializers.CharField(
        validators=[
            UniqueValidator(queryset=Tag.objects.all()),
            MaxLengthValidator(constants.MAX_LEN_TAG_SLUG,
                               message='Max tag slug length – 32 characters'),
            RegexValidator(r'^[-a-zA-Z0-9_]+$',
                           message='Tag slug must consist of letters, '
                           'digits, or -_ characters.')
        ]
    )

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
        read_only_fields = ('id', 'name', 'slug')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериалайзер модели Favorite."""
    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        read_only=True
    )
    name = serializers.ReadOnlyField(
        source='recipe.name',
        read_only=True
    )
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True
    )
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True
    )

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериалайзер модели ShoppingCart."""
    name = serializers.ReadOnlyField(
        source='recipe.name',
        read_only=True)
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер модели Ingredient."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = '__all__',


class AddIngredientSerializer(serializers.ModelSerializer):
    """
    Serializer для поля ingredient модели Recipe - создание ингредиентов.
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Serializer для связаной модели Recipe и Ingredient."""
    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    """Serializer для чтения модели Recipe."""
    author = UserListRetrieveSerializer()
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='recipe_ingredients',
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Favorite.objects.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return ShoppingCart.objects.filter(recipe=obj).exists()
        return False


class RecipeCreateUpdateDeleteSerilizer(serializers.ModelSerializer):
    """Serializer для создания, редактирования, удаления модели Recipe."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        allow_empty=False,
        allow_null=False,
    )
    author = UserListRetrieveSerializer(read_only=True)
    ingredients = AddIngredientSerializer(
        many=True,
        write_only=True
    )
    name = serializers.CharField(
        max_length=constants.MAX_LEN_RECIPE_NAME
    )
    image = Base64ImageField()
    text = serializers.CharField()
    cooking_time = serializers.IntegerField(
        min_value=constants.MIN_COOKING_TIME_VALUE
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Favorite.objects.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return ShoppingCart.objects.filter(recipe=obj).exists()
        return False

    def validate_tags(self, value):
        if not value:
            raise ValidationError(
                {'tags': 'Нужно выбрать тег!'})
        if len(value) != len(set(value)):
            raise ValidationError(
                {'tags': 'Теги повторяются'})
        return value

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError(
                {'ingredients': 'Нужно выбрать ингредиент!'})
        ingredients_list = []
        for ingredient in value:
            if int(ingredient['amount']) <= 0:
                raise ValidationError(
                    {'amount': 'Количество должно быть больше 0!'})
            ingredients_list.append(ingredient['id'])
        if len(ingredients_list) != len(set(ingredients_list)):
            raise ValidationError(
                {'ingredients': 'Ингредиенты повторяются'})
        return value

    def to_representation(self, instance):
        new_instance = super().to_representation(instance)
        new_instance['ingredients'] = IngredientRecipeSerializer(
            instance.recipe_ingredients.all(),
            many=True
        ).data
        new_instance['tags'] = TagSerializer(
            instance.tags.all(),
            many=True
        ).data
        return new_instance

    def add_ingredients(self, ingredients, model):
        for ingredient in ingredients:
            IngredientRecipe.objects.update_or_create(
                recipe=model,
                ingredient=ingredient['id'],
                amount=ingredient['amount'])

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        author = self.context['request'].user

        recipe = Recipe.objects.create(author=author, **validated_data)

        self.add_ingredients(ingredients, recipe)
        recipe.tags.set(tags_data)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])

        self.validate_ingredients(ingredients)
        self.validate_tags(tags_data)

        instance = super().update(instance, validated_data)
        instance.ingredients.clear()
        instance.tags.clear()

        self.add_ingredients(ingredients, instance)
        instance.tags.set(tags_data)
        instance.save()

        return super().update(instance, validated_data)


class RecipeMiniSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода рецепта в FollowSerializer."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image',)


class SubscribeListCreateDeleteSerializer(serializers.ModelSerializer):
    """Serializer для модели Subscribe."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField('get_avatar_url',)

    class Meta:
        model = Subscribe
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def get_avatar_url(self, obj):
        if obj.author.avatar:
            return obj.author.avatar
        return None

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Subscribe.objects.filter(
                user=obj.user,
                author=obj.author
            ).exists()
        return False

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author)
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return RecipeMiniSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def validate(self, data):
        author = self.context.get('author')
        user = self.context.get('request').user
        if Subscribe.objects.filter(
                author=author,
                user=user
        ).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Невозможно подписаться на себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def to_representation(self, instance):
        print('!!!!!!!!!!', instance)
        res = super().to_representation(instance)
        print('??????????', res)
        return res


class ShortLinkSerializer(serializers.ModelSerializer):
    """Сериализатор для коротких ссылок"""
    class Meta:
        model = ShortLink
        fields = '__all__'
        extra_kwargs = {'long_url': {'validators': []}}

    def create(self, validated_data):
        long_url = validated_data['long_url']
        short_url, created = ShortLink.objects.get_or_create(
            long_url=long_url
        )
        if created:
            status_code = status.HTTP_200_OK
        else:
            if short_url:
                status_code = status.HTTP_200_OK
            else:
                status_code = status.HTTP_400_BAD_REQUEST
        return short_url, status_code

    def to_representation(self, instance):
        instance = super().to_representation(instance)
        result = dict()
        result['short-link'] = instance['short_url']
        return result
