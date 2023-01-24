import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from users.models import Subscription, User
from django.core import exceptions
from django.contrib.auth.password_validation import validate_password


class CustomUserCreateSerializer(UserCreateSerializer):
    """User model (create user) Serializer."""
    password = serializers.CharField(
        style={
            'input_type': 'password'
        },
        write_only=True,
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )


class CustomUserSerializer(UserSerializer):
    """User model Serializer."""
    is_subscribed = serializers.BooleanField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )


class SetPasswordSerializer(serializers.Serializer):
    """Set password for User model Serializer."""
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, data):
        new_password = data.get('new_password')

        try:
            validate_password(new_password)
        except exceptions.ValidationError as err:
            raise serializers.ValidationError(
                {'new_password': err.messages}
            )
        return super().validate(data)

    def update(self, instance, validated_data):
        current_password = validated_data.get('current_password')
        new_password = validated_data.get('new_password')
        if not instance.check_password(current_password):
            raise serializers.ValidationError(
                {
                    'current_password': 'Wrong password'
                }
            )
        if current_password == new_password:
            raise serializers.ValidationError(
                {
                    'new_password': 'The new password must be different from '
                                    'the current password'
                }
            )
        instance.set_password(new_password)
        instance.save()
        return validated_data


class IngredientSerializer(serializers.ModelSerializer):
    """Ingredient model Serializer."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Tag model Serializer."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    """IngredientAmount model Serializer."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class Base64ImageField(serializers.ImageField):
    """Serializer for image field."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            img_format, img_str = data.split(';base64,')
            ext = img_format.split('/')[-1]
            data = ContentFile(base64.b64decode(img_str), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Recipe model Serializer."""
    tags = TagSerializer(
        read_only=True,
        many=True
    )
    author = CustomUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    ingredients = IngredientAmountSerializer(
        many=True,
        source='ingredients_amount'
    )
    is_favorited = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()
    image = Base64ImageField(
        required=False,
        allow_null=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )


class RecipeWriteSerializer(RecipeSerializer):
    """Recipe model (create recipe) Serializer."""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    @staticmethod
    def save_ingredients(recipe, ingredients):
        ingredients_list = []
        for ingredient in ingredients:
            current_ingredient = ingredient['ingredient']['id']
            current_amount = ingredient.get('amount')
            ingredients_list.append(
                IngredientAmount(
                    recipe=recipe,
                    ingredient=current_ingredient,
                    amount=current_amount
                )
            )
        IngredientAmount.objects.bulk_create(ingredients_list)

    def validate(self, data):
        if data.get('cooking_time') <= 0:
            raise serializers.ValidationError(
                {
                    'error': 'Cooking time cannot be less than minutes'
                }
            )
        ingredients_list = []
        for ingredient in data.get('ingredients_amount'):
            if ingredient.get('amount') <= 0:
                raise serializers.ValidationError(
                    {
                        'error': 'The ingredients number cannot be less than 1'
                    }
                )
            ingredients_list.append(ingredient['ingredient']['id'])

        if len(ingredients_list) > len(set(ingredients_list)):
            raise serializers.ValidationError(
                {
                    'error': 'Ingredients should not be repeated'
                }
            )
        return data

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients_amount')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data, author=author)
        recipe.tags.add(*tags)
        self.save_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        ingredients = validated_data.pop('ingredients_amount')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.add(*tags)
        instance.ingredients.clear()
        recipe = instance
        self.save_ingredients(recipe, ingredients)
        instance.save()
        return instance


class FavoriteSerializer(RecipeSerializer):
    """Favorite model Serializer."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(RecipeSerializer):
    """ShoppingCart model Serializer."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(CustomUserSerializer):
    """Subscription model Serializer."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')

        if recipes_limit:
            recipes = obj.recipes.all()[:(int(recipes_limit))]
        else:
            recipes = obj.recipes.all()
        return FavoriteSerializer(recipes, many=True).data


class SubscribeSerializer(CustomUserSerializer):
    """Subscribe Serializer."""

    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def validate(self, data):
        user = self.context.get('request').user
        author = data.get('author')
        if user == author:
            raise serializers.ValidationError(
                {
                    'error': 'You cannot subscribe to yourself'
                }
            )
        return data
