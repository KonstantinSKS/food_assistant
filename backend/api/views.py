from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet


class UserViewSet(ModelViewSet):
    ...


class TagViewSet(ModelViewSet):
    ...


class IngredientViewSet(ModelViewSet):
    ...


class RecipeViewSet(ModelViewSet):
    ...


class AmountOfIngredientsViewSet(ModelViewSet):
    ...


class ShoppingListViewSet(ModelViewSet):
    ...


class FavoriteViewSet(ModelViewSet):
    ...
