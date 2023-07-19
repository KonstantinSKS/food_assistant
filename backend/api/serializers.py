from rest_framework import serializers
from django.core.validators import MinValueValidator

from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Tag, Ingredient, Recipe,
                            AmountOfIngredients)
from users.models import User, Subscription


class UserSerializer(serializers.ModelSerializer):
    ...
# !!!!


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientsCreateOrUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        validators=(MinValueValidator(1))
    )

    class Meta:
        model = AmountOfIngredients
        fields = (
            'id',
            'amount',
        )


class IngredientsReadOnlySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = AmountOfIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeCreateOrUpdateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientsCreateOrUpdateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(MinValueValidator(1))
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Рецепт должен содержать минимум 1 ингредиент!'
            )
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество не может быть меньше 1 единицы!'
                )
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Для рецепта нужен хотя бы один тег!'
            )
        return tags


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientsReadOnlySerializer(many=True)
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscriptionSerializer(UserSerializer):
    recipes = FavoriteRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Subscription.objects.filter(user=self.context['request'].user,
                                            author=obj).exists()

        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def validate(self, data):
        if self.context['request'].method == 'POST':
            user = self.context.get('user')
            author = self.context.get('author') # author = self.instance
            if User.objects.filter(
                    user=user, author=author).exists():
                raise serializers.ValidationError(
                    'Вы уже подписаны на этого пользователя!')
            if user == author:
                raise serializers.ValidationError(
                    'Нельзя подписаться на самого себя!')
        return data
