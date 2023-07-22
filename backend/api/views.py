from django.shortcuts import render

# from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets
from .serializers import (
    UserSerializer, TagSerializer,
    IngredientSerializer, IngredientsCreateOrUpdateSerializer,
    IngredientsReadOnlySerializer,
    RecipeCreateOrUpdateSerializer, RecipeReadOnlySerializer,
    FavoriteRecipeSerializer, SubscriptionSerializer)
from users.models import User, Subscription
from recipes.models import (Tag, Ingredient, Recipe,
                            AmountOfIngredients)


class UserViewSet(viewsets.ModelViewSet):
    ...


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    ...


class RecipeViewSet(viewsets.ModelViewSet):
    ...


class AmountOfIngredientsViewSet(viewsets.ModelViewSet):
    ...


class ShoppingListViewSet(viewsets.ModelViewSet):
    ...


class FavoriteViewSetviewsets(viewsets.ModelViewSet):
    ...
