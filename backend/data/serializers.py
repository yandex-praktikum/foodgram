from rest_framework import serializers

from .models import Recipe, Ingredients


class RecipeSerializer(serializers.ModelSerializer):


    class Meta:
        model = Recipe
        fields = ('id', 'name', 'description')


class IngredientsSerializer(serializers.ModelSerializer):


    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')