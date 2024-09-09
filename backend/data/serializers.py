from rest_framework import serializers

from .models import Recipe, Ingredients, Tag


class RecipeSerializer(serializers.ModelSerializer):


    class Meta:
        model = Recipe
        fields = ('id', 'author', 'image', 'name', 'description', 'ingredients', 'cook_time', 'tags', 'pub_date')


class IngredientsSerializer(serializers.ModelSerializer):


    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class TagSeriallizer(serializers.ModelSerializer):


    class Meta:
        model = Tag
        fields = ('id', 'name')
