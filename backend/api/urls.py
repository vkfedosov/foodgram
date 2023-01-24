from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                       ShoppingCartViewSet, UserViewSet, TagViewSet)

router = DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('recipes', ShoppingCartViewSet, basename='shopping_cart')
router.register('recipes', FavoriteViewSet, basename='favorite')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
