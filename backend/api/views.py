from django.db.models import Sum, F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)

from users.models import Subscription, User

from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeWriteSerializer, RecipeSerializer,
                          ShoppingCartSerializer, SubscriptionSerializer,
                          TagSerializer, SubscribeSerializer,
                          SetPasswordSerializer, CustomUserSerializer,
                          CustomUserCreateSerializer)
from .filters import RecipeFilter


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """User, subscription and list of subscriptions."""

    def get_serializer_class(self):
        if self.action is 'subscriptions':
            return SubscriptionSerializer
        elif self.action is 'subscribe':
            return SubscribeSerializer
        elif self.action is 'set_password':
            return SetPasswordSerializer
        if self.action in ('list', 'retrieve', 'me'):
            return CustomUserSerializer
        return CustomUserCreateSerializer

    def get_queryset(self):
        user_id = self.request.user.pk
        queryset = User.objects.add_user_annotations(user_id)
        if self.request.query_params.get('is_subscribed'):
            queryset = queryset.filter(is_subscribed=True)
        else:
            queryset = User.objects.all()
        return queryset

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['POST'],
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        user = request.user
        data = request.data
        serializer = self.get_serializer(user, data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(
            {
                'detail': 'Password changed successfully'
            },
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[IsAuthorOrAdminOrReadOnly]
    )
    def subscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(User, pk=pk)
        data = {
            'user': user.pk,
            'author': author.pk
        }
        serializer = SubscribeSerializer(
            data=data,
            context={
                'request': request
            },
        )
        if Subscription.objects.filter(user=user, author=author).exists():
            message = {
                'error': 'You are already subscribed to the author'
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = self.get_serializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(User, pk=pk)
        subscribe = Subscription.objects.filter(user=user, author=author)
        if subscribe.exists():
            subscribe.delete()
            message = {
                'detail': 'You have successfully unsubscribed'
            }
            return Response(message, status=status.HTTP_204_NO_CONTENT)
        message = {
            'error': 'You are already unsubscribed to the author'
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(subscribing__user=user)
        page = self.paginate_queryset(subscriptions)
        serializer = self.get_serializer(page, many=True, )
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
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeSerializer

    def get_queryset(self):
        tags = self.request.query_params.getlist('tags')
        author = self.request.query_params.get('author', None)
        user_id = self.request.user.pk
        if tags:
            queryset = Recipe.objects.filter_tags(tags)
        if author:
            queryset = Recipe.objects.filter(author=author)
        queryset = Recipe.objects.add_user_annotations(user_id)
        if self.request.query_params.get('is_favorited'):
            queryset = queryset.filter(is_favorited=True)
        if self.request.query_params.get('is_in_shopping_cart'):
            queryset = queryset.filter(is_in_shopping_cart=True)
        return queryset


class FavoriteViewSet(viewsets.GenericViewSet):
    """Favorite Recipes."""
    queryset = Recipe.objects.all()
    serializer_class = FavoriteSerializer

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[IsAuthorOrAdminOrReadOnly]
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = self.get_serializer(recipe)
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            message = {
                'error': 'You have already added the recipe to favorites'
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.get_or_create(user=user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def unfavorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        favorite = Favorite.objects.filter(user=user, recipe=recipe)
        if favorite.exists():
            favorite.delete()
            message = {
                'detail': 'You have successfully unfavorited'
            }
            return Response(message, status=status.HTTP_204_NO_CONTENT)
        message = {
            'error': 'You are already removed a recipe from favorites'
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartViewSet(viewsets.GenericViewSet):
    """Shopping cart and list of ingredients to buy."""
    queryset = Recipe.objects.all()
    serializer_class = ShoppingCartSerializer

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[IsAuthorOrAdminOrReadOnly]
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = self.get_serializer(recipe)
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            message = {
                'error': 'You have already added the recipe to shopping cart'
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        shopping_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if shopping_cart.exists():
            shopping_cart.delete()
            message = {
                'detail':
                    'You have successfully removed recipe from shopping cart'
            }
            return Response(message, status=status.HTTP_204_NO_CONTENT)
        message = {
            'error':
                'You have successfully removed a recipe from shopping cart'
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientAmount.objects.filter(
            recipe__shopping_cart__user=user).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')).annotate(
            amount=Sum('amount')
        )
        data = []
        for ingredient in ingredients:
            data.append(
                f'{ingredient["name"]}, '
                f'{ingredient["amount"]} '
                f'{ingredient["measurement_unit"]}'
            )
        content = 'Список покупок:\n\n' + '\n'.join(data)
        filename = 'shopping_cart.txt'
        request = HttpResponse(content, content_type='text/plain')
        request['Content-Disposition'] = f'attachment; filename={filename}'
        return request
