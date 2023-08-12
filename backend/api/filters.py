import django_filters

from recipes.models import Ingredient, Recipe, Tag
from users.models import User


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name',
                                     lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.BooleanFilter(
        method='is_favorited_filter')
    author = django_filters.ModelChoiceFilter(
        queryset=User.objects.all())
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='is_in_shopping_cart_filter')
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = (
            # 'is_favorited',
            'author',
            # 'is_in_shopping_cart',
            'tags',
        )

    def is_favorited_filter(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorites__user=user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shoppinglist__user=user)
        return queryset
