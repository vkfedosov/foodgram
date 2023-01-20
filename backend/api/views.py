from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User

from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          ShoppingCartSerializer, SubscriptionSerializer,
                          TagSerializer)


class SubscriptionsViewSet(viewsets.GenericViewSet):
    """Subscription and list of subscriptions."""
    queryset = User.objects.all()
    serializer_class = SubscriptionSerializer

    @action(detail=True,
            methods=['POST', 'DELETE'],
            permission_classes=[IsAuthorOrAdminOrReadOnly])
    def subscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(User, pk=pk)
        serializer = self.get_serializer(author)

        if self.request.method == 'POST':
            if user == author:
                message = {'error': 'You cannot subscribe to yourself'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            if Subscription.objects.filter(user=user, author=author).exists():
                message = {'error': 'You are already subscribed to the author'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            Subscription.objects.get_or_create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if user == author:
                message = {'error': 'You cannot unsubscribe to yourself'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            subscribe = Subscription.objects.filter(user=user, author=author)
            if subscribe.exists():
                subscribe.delete()
                message = {'detail': 'You have successfully unsubscribed'}
                return Response(message, status=status.HTTP_204_NO_CONTENT)
            message = {'error': 'You are already unsubscribed to the author'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['GET'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(subscribing__user=user)
        result = User.objects.filter(id__in=subscriptions)
        page = self.paginate_queryset(result)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Tag list."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ingredient list."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Recipe list."""
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()
        tags = self.request.query_params.get('tags')
        if tags:
            queryset = queryset.filter(tags__slug=tags)

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        user = self.request.user
        if user.is_anonymous:
            return queryset

        is_in_shopping = self.request.query_params.get('is_favorited')
        if is_in_shopping == '1':
            queryset = queryset.filter(shopping_cart__user=user)
        elif is_in_shopping == '0':
            queryset = queryset.exclude(shopping_cart__user=user)

        is_favorited = self.request.query_params.get('is_in_shopping_cart')
        if is_favorited == '1':
            queryset = queryset.filter(favorite__user=user)
        if is_favorited == '0':
            queryset = queryset.exclude(favorite__user=user)
        return queryset


class FavoriteViewSet(viewsets.GenericViewSet):
    """Favorite Recipes."""
    queryset = Recipe.objects.all()
    serializer_class = FavoriteSerializer

    @action(detail=True,
            methods=['POST', 'DELETE'],
            permission_classes=[IsAuthorOrAdminOrReadOnly])
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = self.get_serializer(recipe)

        if self.request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                message = {'error': 'You have already added the recipe to '
                                    'favorites'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.get_or_create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            favorite = Favorite.objects.filter(user=user, recipe=recipe)
            if favorite.exists():
                favorite.delete()
                message = {'detail': 'You have successfully unfavorited'}
                return Response(message, status=status.HTTP_204_NO_CONTENT)
            message = {'error': 'You have successfully removed a recipe from '
                                'favorites'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartViewSet(viewsets.GenericViewSet):
    """Shopping cart and list of ingredients to buy."""
    queryset = Recipe.objects.all()
    serializer_class = ShoppingCartSerializer

    @action(detail=True,
            methods=['POST', 'DELETE'],
            permission_classes=[IsAuthorOrAdminOrReadOnly])
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = self.get_serializer(recipe)

        if self.request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                message = {'error': 'You have already added the recipe to '
                                    'shopping cart'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            favorite = ShoppingCart.objects.filter(user=user, recipe=recipe)
            if favorite.exists():
                favorite.delete()
                message = {'detail': 'You have successfully removed recipe '
                                     'from shopping cart'}
                return Response(message, status=status.HTTP_204_NO_CONTENT)
            message = {'error': 'You have successfully removed a recipe from '
                                'shopping cart'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['GET'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientAmount.objects.filter(
            recipe__shopping_cart__user=user).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
            total_amount=Sum('amount'))
        data = []
        for ingredient in ingredients:
            data.append(
                f'{ingredient["ingredient__name"]} '
                f'{ingredient["ingredient__measurement_unit"]}: '
                f'{ingredient["total_amount"]}')
        content = 'Shopping Cart:\n\n'.join(data)
        filename = 'shopping_cart.txt'
        request = HttpResponse(content, content_type='text/plain')
        request['Content-Disposition'] = f'attachment; filename={filename}'
        return request
