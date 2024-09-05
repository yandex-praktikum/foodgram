from django.contrib import admin

from .models import Recipe, Ingredients, Tag

admin.site.register(Recipe)
admin.site.register(Ingredients)
admin.site.register(Tag)
