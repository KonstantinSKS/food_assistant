from django.contrib import admin

from .models import (Tag, Ingredient, Recipe,
                     AmountOfIngredients, ShoppingList,
                     Favorite, MIN_UNIT_AMOUNT)


class RecipeIngredientInline(admin.TabularInline):
    model = AmountOfIngredients
    extra = MIN_UNIT_AMOUNT


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
    list_display = (
        'id',
        'name',
        'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
        'favorites',)
    list_filter = (
        'author',
        'name',
        'tags',)
    search_fields = ('name',)
    inlines = (RecipeIngredientInline,)
    empty_value_display = '-пусто-'

    def favorites(self, obj):
        return obj.favorites.count()


@admin.register(AmountOfIngredients)
class AmountOfIngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'ingredient',
        'amount',
    )
    list_filter = ('ingredient',)


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    list_filter = ('user', 'recipe')
    search_fields = ('user',)
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    list_filter = ('user', 'recipe')
    search_fields = ('user',)
    empty_value_display = '-пусто-'
