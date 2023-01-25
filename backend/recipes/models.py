from django.db import models
from django.db.models import Exists, OuterRef

from users.models import User


class Ingredient(models.Model):
    """Ingredient model."""
    name = models.CharField(
        blank=False,
        max_length=50,
        verbose_name='Name',
    )
    measurement_unit = models.CharField(
        blank=False,
        max_length=50,
        verbose_name='Measurement Unit',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Tag model."""
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Tag name',
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Color (HEX code)',
        help_text='example, #49B64E',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='URL',
        help_text='Unique URL for the Tag',
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class RecipeQuerySet(models.QuerySet):
    """Recipe QuerySet."""

    def filter_tags(self, tags):
        if tags:
            return self.filter(tags__slug__in=tags).distinct()
        return self

    def add_user_annotations(self, user_id):
        return self.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    recipe__pk=OuterRef('pk'),
                    user_id=user_id,
                )
            ),
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    recipe__pk=OuterRef('pk'),
                    user_id=user_id,
                )
            ),
        )


class Recipe(models.Model):
    """Recipe model."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Author',
    )
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Title',
    )
    image = models.ImageField(
        blank=True,
        upload_to='recipes/',
        verbose_name='Image',
    )
    text = models.TextField(
        verbose_name='Text',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        related_name='recipes',
        verbose_name='Ingredients',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Tags',
    )
    cooking_time = models.IntegerField(
        verbose_name='Cooking Time',
        help_text='in minutes',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Publications Date',
    )

    objects = RecipeQuerySet.as_manager()

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """Favorite model."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Recipe',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='User added to favorites',
    )

    class Meta:
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'


class ShoppingCart(models.Model):
    """Shopping Cart model."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Recipe',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='User added to shopping cart',
    )

    class Meta:
        verbose_name = 'Shopping Cart'
        verbose_name_plural = 'Shopping Carts'


class IngredientAmount(models.Model):
    """Ingredient amount model."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_amount',
        verbose_name='Ingredient',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_amount',
        verbose_name='Recipe',
    )
    amount = models.IntegerField(
        verbose_name='Amount',
    )

    class Meta:
        verbose_name = 'Ingredient amount'
        verbose_name_plural = 'Ingredients amount'

    def __str__(self):
        return f'{self.ingredient}: {self.amount}'
