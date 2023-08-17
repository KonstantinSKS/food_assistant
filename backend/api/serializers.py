from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Tag, Ingredient, Recipe,
                            AmountOfIngredients, Favorite,
                            ShoppingList,
                            MIN_UNIT_AMOUNT, MAX_UNIT_AMOUNT)
from users.models import User, Subscription


class CreateUserSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'write_only': True},
        }

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')
        user_email_exists = User.objects.filter(email=email).exists()
        user_username_exists = User.objects.filter(username=username).exists()
        if (user_email_exists
                and not user_username_exists):
            raise serializers.ValidationError(
                'User with such email already exists')
        if (not user_email_exists
                and user_username_exists):
            raise serializers.ValidationError(
                'User with such username already exists')
        return data

    def validate_password(self, password):
        validate_password(password)
        return password


class UserReadOnlySerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Subscription.objects.filter(user=self.context['request'].user,
                                            author=obj).exists())


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, max_length=150)
    current_password = serializers.CharField(required=True, max_length=150)

    def validate_new_password(self, new_password):
        validate_password(new_password)
        return new_password

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError(
                {'current_password': 'Введен неправильный пароль.'}
            )
        if (validated_data['current_password']
           == validated_data['new_password']):
            raise serializers.ValidationError(
                {'new_password': 'Новый пароль должен отличаться от текущего.'}
            )
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data


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
    author = UserReadOnlySerializer(read_only=True,
                                    default=serializers.CurrentUserDefault())
    ingredients = IngredientsCreateOrUpdateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(MinValueValidator(MIN_UNIT_AMOUNT),
                    MaxValueValidator(MAX_UNIT_AMOUNT))
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

    validators = [
        serializers.UniqueTogetherValidator(
            queryset=Recipe.objects.all(),
            fields=('author', 'name'),
            message='Такой рецепт уже существет!'
        )
    ]

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Рецепт должен содержать минимум 1 ингредиент!'
            )
        ingredient_list = []
        for ingredient in ingredients:
            ingredient = get_object_or_404(Ingredient, id=ingredient['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'У рецепта не может быть два одинаковых ингредиента!'
                )
            ingredient_list.append(ingredient)
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Для рецепта нужен хотя бы один тег!'
            )
        return tags

    def create_ingredients_amounts(self, ingredients, recipe):
        AmountOfIngredients.objects.bulk_create(
            [AmountOfIngredients(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(recipe=recipe,
                                        ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(recipe=instance,
                                        ingredients=ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadOnlySerializer(
            instance,
            context=self.context
        ).data


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserReadOnlySerializer(read_only=True)
    ingredients = IngredientsReadOnlySerializer(source='recipes',
                                                many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Favorite.objects.filter(user=self.context['request'].user,
                                        recipe=obj).exists()
        )

        # user = self.context['request'].user
        # if user.is_authenticated:
        #    return user.favorites.filter(recipe=obj).exists()
        # return False
        # user = self.context.get('request').user
        #  if not user.is_anonymous:

    def get_is_in_shopping_cart(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and ShoppingList.objects.filter(
                user=self.context['request'].user,
                recipe=obj).exists()
        )
        # user = self.context['request'].user
        # if user.is_authenticated:
        # return user.shoppinglist.filter(recipe=obj).exists()
        # return False
# user = self.context.get('request').user
        # if not user.is_anonymous:


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )

    # def validate(self, obj):
    #    recipe = self.instance
    #    if not Favorite.objects.filter(user=self.context['request'].user,
    #                                   recipe=recipe).exists():
    #        raise serializers.ValidationError(
    #            {'errors': 'Рецепт уже в избранном!'})
    #    return obj


class SubscriptionSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Subscription.objects.filter(user=self.context['request'].user,
                                            author=obj).exists()
        )

    def get_recipes(self, author):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = author.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = FavoriteRecipeSerializer(
            recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeSerializer(UserSerializer):
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = FavoriteRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def validate(self, obj):
        if (self.context['request'].user == obj):
            raise serializers.ValidationError(
                {'errors': 'Нельзя подписаться на самого себя!'})
        return obj

    def get_is_subscribed(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Subscription.objects.filter(user=self.context['request'].user,
                                            author=obj).exists()
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe'
        )
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в избранном!'
            ),
        )

    def to_representation(self, instance):
        request = self.context.get('request')
        return FavoriteRecipeSerializer(
            instance.recipe,
            context={'request': request}).data


# class FavoriteSerializer(serializers.ModelSerializer):

#    class Meta:
#        model = Favorite
#        fields = (
#            'user',
#            'recipe'
#        )
#        validators = [
#            serializers.UniqueTogetherValidator(
#                queryset=Favorite.objects.all(),
#                fields=('user', 'recipe'),
#                message='Рецепт уже в избранном!'
#            )
#        ]

#    def to_representation(self, instance):
#        request = self.context.get('request')
#        return FavoriteRecipeSerializer(
#            instance.recipe,
#            context={'request': request}).data

    # def validate(self, obj):
    #   recipe = self.instance
        # user = self.context['request'].user
        # if recipe.favorites.exists():
    #    if not Favorite.objects.filter(user=self.context['request'].user,
    #                                   recipe=recipe).exists():
    #        raise serializers.ValidationError(
    #            {'errors': 'Рецепт уже в избранном!'})
    #    return obj  # if (self.context['request'].recipe == obj):

    # def validate(self, data):
    #    user = data['user']
    #    recipe = data['recipe']
    #    action = self.context['action']
    #    recipe_in_favorites = Favorite.objects.filter(
    #        recipe=recipe,
    #        user=user
    #    )
    #    if action == 'remove':
    #        recipe_in_favorites.delete()
    #    elif action == 'add':
    #        if recipe_in_favorites:
    #            raise serializers.ValidationError(
    #                detail='Рецепт уже в избранном!')
    #    return data

        # validators = [
        #    serializers.UniqueTogetherValidator(
        #        queryset=Favorite.objects.all(),
        #        fields=('user', 'recipe'),
        #        message='Рецепт уже в избранном!'
        #    )
        # ]


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingList
        fields = (
            'user',
            'recipe'
        )
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=ShoppingList.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в списке покупок!'
            ),
        )

    def to_representation(self, instance):
        request = self.context.get('request')
        return FavoriteRecipeSerializer(
            instance.recipe,
            context={'request': request}).data

#    class Meta:
#        model = ShoppingList
#        fields = (
#            'user',
#            'recipe'
#        )
#        validators = [
#            serializers.UniqueTogetherValidator(
#                queryset=ShoppingList.objects.all(),
#                fields=('user', 'recipe'),
#                message='Рецепт уже в списке покупок!'
#            )
#        ]

#    def to_representation(self, instance):
#        request = self.context.get('request')
#        return FavoriteRecipeSerializer(
#            instance.recipe,
#            context={'request': request}).data

    # def validate(self, obj):
    #    recipe = self.instance
    #    if not ShoppingList.objects.filter(user=self.context['request'].user,
    #                                       recipe=recipe).exists():
    #        raise serializers.ValidationError(
    #            {'errors': 'Рецепт уже в списке покупок!'})
    #    return obj

    # user = serializers.ReadOnlyField()
    # recipe = serializers.ReadOnlyField()

    # class Meta:
    #    model = ShoppingList
    #    fields = (
    #        'user',
    #        'recipe'
    #    )

    # def validate(self, obj):
    #    recipe = self.instance
        # user = self.context['request'].user
    #    if recipe.shoppinglist.exists():
    #        raise serializers.ValidationError(
    #            {'errors': 'Рецепт уже в списке покупок!'})
    #    return obj  # if (self.context['request'].recipe == obj):

    # def validate(self, data):
    #    user = data['user']
    #    recipe = data['recipe']
    #    action = self.context['action']
    #    recipe_in_sh_cart = ShoppingList.objects.filter(
    #        recipe=recipe,
    #        user=user
    #    )
    #    if action == 'remove':
    #        recipe_in_sh_cart.delete()
    #    elif action == 'add':
    #        if recipe_in_sh_cart:
    #            raise serializers.ValidationError(
    #                detail='Рецепт уже добавлен в список покупок!')
    #    return data

    # validators = [
    #    serializers.UniqueTogetherValidator(
    #        queryset=ShoppingList.objects.all(),
    #        fields=('user', 'recipe'),
    #        message='Рецепт уже добавлен в список покупок!'
    #    )
    # ]
