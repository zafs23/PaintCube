import time

# import connection module to test if the database connection is available
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for Database to start ...')
        db_conn = None
        while not db_conn:  # false value until database is available
            try:
                db_conn = connections['default']  # if connection is error and
                # django will raise an error
            except OperationalError:
                self.stdout.write('Database is unavailable, waiting 1 second.')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database is available!'))
