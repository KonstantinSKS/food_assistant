from django.contrib import admin

from .models import (Tag, Ingredient, Recipe,
                     AmountOfIngredients, ShoppingList, Favorite)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',)
    list_filter = ('name', 'slug',)
    search_fields = ('name', 'slug',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    ...


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    ...


@admin.register(AmountOfIngredients)
class AmountOfIngredientsAdmin(admin.ModelAdmin):
    ...


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    ...


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    ...
