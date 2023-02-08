import os
from csv import reader

from django.conf import settings
from django.core.management import BaseCommand
from recipes.models import Ingredient, Tag

DATA_PATH = os.path.join(settings.BASE_DIR, 'data')
INGREDIENTS_DATA = os.path.join(DATA_PATH, 'ingredients.csv')
TAGS_DATA = os.path.join(DATA_PATH, 'tags.csv')


class Command(BaseCommand):
    """Command to import data from .csv to Database"""

    def handle(self, *args, **kwargs):
        with (
            open(INGREDIENTS_DATA, 'r', encoding='UTF-8') as ingredients,
            open(TAGS_DATA, 'r', encoding='UTF-8') as tags,
        ):
            for fields in reader(ingredients):
                if len(fields) == 2:
                    name, measurement_unit = fields
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit,
                    )
            for fields in reader(tags):
                if len(fields) == 3:
                    name, color, slug = fields
                    Tag.objects.get_or_create(
                        name=name,
                        color=color,
                        slug=slug,
                    )
        self.stdout.write('Data has been imported successfully')
