from rest_framework import serializers, validators
from django.core.validators import MinValueValidator
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
# from django.shortcuts import get_object_or_404

from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Tag, Ingredient, Recipe,
                            AmountOfIngredients, Favorite)
from users.models import User, Subscription


class UserCreateSerializer(UserCreateSerializer):

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
            'password': {'write_only': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
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


class UserReadOnlySerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
# default=False

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
    amount = serializers.IntegerField(
        validators=(MinValueValidator(1),)
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
        validators=(MinValueValidator(1),)
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
        #validators = [
            #validators.UniqueTogetherValidator(
                #queryset=AmountOfIngredients.objects.all(),
                #fields=('recipe', 'ingredient')
            #)
        #]

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
            if ingredients.count(ingredient) > 1:
                raise serializers.ValidationError(
                    'У рецепта не может быть два одинаковых ингредиента!'
                )
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Для рецепта нужен хотя бы один тег!'
            )
        return tags

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                'Время приготовления меньше 1 минуты!'
            )
        return cooking_time

    #def create_AmountOfIngredients(self, ingredients, recipe):
        #for ingredient in ingredients:
            #ingredient = get_object_or_404(Ingredient, pk=ingredient['id'])
            #amount = ingredient['amount']
            #AmountOfIngredients.objects.create(
                #recipe=recipe,
                #ingredient=ingredient,
                #amount=amount,
            #)

    def create_ingredients_amounts(self, ingredients, recipe):
        for ingredient in ingredients:
            ing, _ = AmountOfIngredients.objects.get_or_create(
                ingredient=get_object_or_404(
                    Ingredient.objects.filter(id=ingredient['id'])
                ),
                amount=ingredient['amount'],
            )
            recipe.ingredients.add(ing.id)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(recipe=recipe,
                                        ingredients=ingredients)
        return recipe

    # def create(self, validated_data):
        # author = self.context.get('request').user эту строку не надо?
        #ingredients = validated_data.pop('ingredients')
        #tags = validated_data.pop('tags')
        #recipe = Recipe.objects.create(**validated_data)
        #recipe.tags.set(tags)
        #for ingredient in ingredients:
            #amount = ingredient['amount']
            #ingredient = get_object_or_404(Ingredient, pk=ingredient['id'])

            #AmountOfIngredients.objects.create(
                # recipe=recipe, эту строку не надо?
                #ingredient=ingredient,
                #amount=amount
            #)
        #self.create_AmountOfIngredients(
            #recipe, ingredients)

        #return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(recipe=instance,
                                        ingredients=ingredients)
        return super().update(instance, validated_data)

    # def to_representation(self, instance):


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientsReadOnlySerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    # serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField()
    # serializers.BooleanField(read_only=True)
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

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return user.shoppinglist.filter(recipe=recipe).exists()


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
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
# Не понятно, будет ли работать этот сериализатор ?

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

    # def validate(self, data):
        # if self.context['request'].method == 'POST':
            # user = self.context.get('user')
            # author = self.context.get('author')  # author = self.instance
            # if User.objects.filter(
                    # user=user, author=author).exists():
                # raise serializers.ValidationError(
                    # 'Вы уже подписаны на этого пользователя!')
            # if user == author:
                # raise serializers.ValidationError(
                    # 'Нельзя подписаться на самого себя!')
        # return data

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
        serializer = FavoriteRecipeSerializer(recipes, many=True, read_only=True)
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
            raise serializers.ValidationError({'errors': 'Нельзя подписаться на самого себя!'})
        return obj

    def get_is_subscribed(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Subscription.objects.filter(user=self.context['request'].user,
                                            author=obj).exists()
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()
