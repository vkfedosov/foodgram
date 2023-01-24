import django_filters

from recipes.models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    """Filter for Recipes."""
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name="tags__slug",
        to_field_name="slug",
    )
    is_favorited = django_filters.NumberFilter(method='get_is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', )

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value == 1:
            return queryset.filter(favorite__user=user)
        return Recipe.objects.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value == 1:
            return queryset.filter(shopping_cart__user=user)
        return Recipe.objects.all()
