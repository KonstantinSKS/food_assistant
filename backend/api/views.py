from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticated, AllowAny)

from .serializers import (
    CreateUserSerializer, UserReadOnlySerializer, SetPasswordSerializer,
    TagSerializer, IngredientSerializer, RecipeCreateOrUpdateSerializer,
    RecipeReadOnlySerializer, FavoriteSerializer,  # FavoriteRecipeSerializer
    SubscriptionSerializer, SubscribeSerializer, ShoppingCartSerializer)
from .pagination import LimitPagesPagination
from .permissions import IsAdminOrReadOnly, IsAdminOrAuthorOrReadOnly
from .filters import IngredientFilter, RecipeFilter
# from .utils import create_model_instance, delete_model_instance
from . viewsets import CreateReadViewSet

from users.models import User, Subscription
from recipes.models import (Tag, Ingredient, Recipe, Favorite, ShoppingList,
                            AmountOfIngredients)


class CustomUserViewSet(CreateReadViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserReadOnlySerializer
        return CreateUserSerializer

    @action(detail=False, methods=['get'],
            pagination_class=None,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserReadOnlySerializer(
            request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = SetPasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'detail': 'Пароль успешно изменен!'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=request.user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(Subscription, user=request.user,
                              author=author).delete()
            return Response({'detail': 'Успешная отписка!'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages,
            many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)


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

    @action(detail=True, methods=['post', 'delete'],
            # url_path='favorite', url_name='favorite',
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = get_object_or_404(User, id=request.user.id)

        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': user.id, 'recipe': recipe.id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Favorite.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(Favorite, user=request.user,
                              recipe=recipe).delete()
            return Response({'detail': 'Рецепт успешно удален из избранного!'},
                            status=status.HTTP_204_NO_CONTENT)

        # recipe = get_object_or_404(Recipe, id=pk)
        # if request.method == 'POST':
        #    return create_model_instance(request, recipe, FavoriteSerializer)

        # if request.method == 'DELETE':
        #    error_message = 'Рецепт удален из избранного!'
        #    return delete_model_instance(request, Favorite,
        #                                 recipe, error_message)
    # def favorite(self, request, **kwargs):
    #    recipe = get_object_or_404(Recipe, id=kwargs['pk'])
    #    if request.method == 'POST':
    #        serializer = FavoriteRecipeSerializer(
    #            recipe, data=request.data, context={'request': request})
    #        serializer.is_valid(raise_exception=True)
    # if not Favorite.objects.filter(user=request.user,
    # recipe=recipe).exists():
    #        Favorite.objects.create(user=request.user, recipe=recipe)
    # avorite_recipe_serializer = FavoriteRecipeSerializer(recipe)
    #        return Response(serializer.data,
    #                        status=status.HTTP_201_CREATED)
    #    if request.method == 'DELETE':
    #        get_object_or_404(Favorite, user=request.user,
    #                          recipe=recipe).delete()
    #        return Response(
    #            {'detail': 'Рецепт успешно удален из избранного.!'},
    #            status=status.HTTP_204_NO_CONTENT)

#  def favorite(self, request, pk):
        # recipe = get_object_or_404(Recipe, pk=pk)

        # if self.request.method == 'POST':
        #  serializer = FavoriteSerializer(
        #    data={'user': request.user.id, 'recipe': recipe.id}
        #  )
        #  serializer.is_valid(raise_exception=True)
        #  Favorite.objects.create(user=self.request.user, recipe=recipe)
        #  favorite_recipe_serializer = FavoriteRecipeSerializer(recipe)
        #  return Response(
        #    favorite_recipe_serializer.data,
        #  status=status.HTTP_201_CREATED)

        # if self.request.method == 'DELETE':
        #    get_object_or_404(Favorite, user=request.user,
        #                      recipe=recipe).delete()
        #  return Response({'detail': 'Рецепт успешно удален из избранного.'},
        #                    status=status.HTTP_204_NO_CONTENT)

        # get_object_or_404(Favorite, user=self.request.user,
        #                  recipe=recipe).delete()
        # return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            # url_path='shopping_cart',
            # url_name='shopping_cart',
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = get_object_or_404(User, id=request.user.id)

        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={'user': user.id, 'recipe': recipe.id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Favorite.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(ShoppingList, user=request.user,
                              recipe=recipe).delete()
            return Response(
                {'detail': 'Рецепт успешно удален из списка покупок!'},
                status=status.HTTP_204_NO_CONTENT)
        # recipe = get_object_or_404(Recipe, id=pk)
        # if request.method == 'POST':
        #    return create_model_instance(request, recipe,
        #                                 ShoppingCartSerializer)

        # if request.method == 'DELETE':
        #    error_message = 'Рецепт удален из списка покупок!'
        #    return delete_model_instance(request, ShoppingList,
        #                                 recipe, error_message)
    # def shopping_cart(self, request, **kwargs):
    #    recipe = get_object_or_404(Recipe, id=kwargs['pk'])
    #    if request.method == 'POST':
    #        serializer = ShoppingCartSerializer(
    #            recipe, data=request.data, context={'request': request})
    #        serializer.is_valid(raise_exception=True)
    #        ShoppingList.objects.create(user=request.user, recipe=recipe)
    # favorite_recipe_serializer = FavoriteRecipeSerializer(recipe)
    #        return Response(serializer.data,
    #                        status=status.HTTP_201_CREATED)
    # if request.method == 'DELETE':
    #        get_object_or_404(ShoppingList, user=request.user,
    #                          recipe=recipe).delete()
    #        return Response(
    #            {'detail': 'Рецепт успешно удален из списка покупок!'},
    #            status=status.HTTP_204_NO_CONTENT)
    # def shopping_cart(self, request, pk):
    #    recipe = get_object_or_404(Recipe, id=pk)
    #    if request.method == 'POST':
    #        return self.add_to_list(
    #            request.user,
    #            recipe,
    #            ShoppingCartSerializer
    #        )
    #    return self.remove_from_list(
    #        request.user,
    #        recipe,
    #        ShoppingCartSerializer
    #    )
#   def shopping_cart(self, request, pk):
        # recipe = get_object_or_404(Recipe, pk=pk)
        # if self.request.method == 'POST':
        #    serializer = ShoppingCartSerializer(
        #        data={'user': request.user.id, 'recipe': recipe.id}
        #    )
        #    serializer.is_valid(raise_exception=True)
        #    ShoppingList.objects.create(user=self.request.user, recipe=recipe)
        #    favorite_recipe_serializer = FavoriteRecipeSerializer(recipe)
        #    return Response(
        #        favorite_recipe_serializer.data,
        #       status=status.HTTP_201_CREATED)

        # if self.request.method == 'DELETE':
        #    get_object_or_404(ShoppingList, user=self.request.user,
        #                      recipe=recipe).delete()
        #    return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = self.request.user
        ingredients = (AmountOfIngredients.objects.filter(
            recipe__shoppinglist__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
        )
        count = 1
        text = 'Список покупок:\n'
        filename = f'{user.username}_shopping_list.txt'
        for item in ingredients:
            name, measurement_unit, amount = list(item.values())
            text += f'{count}. {name} ({measurement_unit}) — {amount}\n'
            count += 1
        response = HttpResponse(text, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


# class FavoriteViewSet(viewsets.ModelViewSet):
#    serializer_class = FavoriteSerializer
#    permission_classes = (IsAuthenticated,)

#    def get_queryset(self):
#        recipe_id = self.kwargs.get('recipe_id')
#        recipe = get_object_or_404(Recipe, id=recipe_id)
#        return recipe.favorites.all()
