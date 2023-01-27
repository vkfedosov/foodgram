from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User

from .filters import RecipeFilter
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, RecipeShortSerializer,
                          RecipeWriteSerializer, SetPasswordSerializer,
                          ShoppingCartSerializer, SubscriptionSerializer,
                          SubscriptionUserSerializer, TagSerializer)


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """User, subscription and list of subscriptions."""

    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action in ('subscriptions', 'subscribe'):
            return SubscriptionUserSerializer
        if self.action in ('list', 'retrieve', 'me'):
            return CustomUserSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        return CustomUserCreateSerializer

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
        serializer = SubscriptionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = self.get_serializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(User, pk=pk)
        Subscription.objects.filter(user=user, author=author).delete()
        message = {
            'detail': 'You have successfully unsubscribed'
        }
        return Response(message, status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(
            subscribing__user=user
        ).prefetch_related('recipes')
        page = self.paginate_queryset(subscriptions)
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
    filter_backends = [filters.SearchFilter]
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Recipe list."""
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('favorite', 'shopping_cart'):
            return RecipeShortSerializer
        if self.action in ('create', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeSerializer

    def get_queryset(self):
        user_id = self.request.user.pk
        queryset = Recipe.objects.add_user_annotations(user_id).select_related(
            'author'
        ).prefetch_related(
            'ingredients', 'tags'
        )
        return queryset

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[IsAuthorOrAdminOrReadOnly]
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {
            'user': user.pk,
            'recipe': recipe.pk
        }
        serializer = FavoriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def unfavorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        message = {
            'detail': 'You have successfully unfavorited'
        }
        return Response(message, status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[IsAuthorOrAdminOrReadOnly]
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {
            'user': user.pk,
            'recipe': recipe.pk
        }
        serializer = ShoppingCartSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
        message = {
            'detail':
                'You have successfully removed recipe from shopping cart'
        }
        return Response(message, status=status.HTTP_204_NO_CONTENT)

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
