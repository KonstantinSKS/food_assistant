import csv
from django.core.management import BaseCommand

from recipes.models import Ingredient

'''Скрипт для импорта csv-файлов в базу данных'''
'''Запуск скрипта через команду "python manage.py dbloader" в консоле'''


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        with open('data/ingredients.csv', encoding='utf8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                status, created = Ingredient.objects.update_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
                self.stdout.write(
                    "!!!The Ingredient database has been loaded successfully!!!")
