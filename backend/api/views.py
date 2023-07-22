from django.shortcuts import render

# from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from .serializers import (
    UserSerializer, TagSerializer,
    IngredientSerializer, IngredientsCreateOrUpdateSerializer,
    IngredientsReadOnlySerializer,
    RecipeCreateOrUpdateSerializer, RecipeReadOnlySerializer,
    FavoriteRecipeSerializer, SubscriptionSerializer)
from .pagination import LimitPagesPagination
from .permissions import IsAdminOrReadOnly, IsAdminOrAuthorOrReadOnly
from .filters import IngredientFilter, RecipeFilter
from users.models import User, Subscription
from recipes.models import (Tag, Ingredient, Recipe,
                            AmountOfIngredients)


class UserViewSet(viewsets.ModelViewSet):
    ...


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitPagesPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadOnlySerializer
        return RecipeCreateOrUpdateSerializer


class AmountOfIngredientsViewSet(viewsets.ModelViewSet):
    ...


class ShoppingListViewSet(viewsets.ModelViewSet):
    ...


class FavoriteViewSetviewsets(viewsets.ModelViewSet):
    ...
