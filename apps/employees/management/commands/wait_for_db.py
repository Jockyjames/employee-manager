import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Attend que la base de données soit disponible.'

    def handle(self, *args, **options):
        self.stdout.write('En attente de la base de données...')
        db_conn = None
        attempts = 0
        while not db_conn:
            try:
                db_conn = connections['default']
                db_conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS('Base de données disponible ✓'))
            except OperationalError:
                attempts += 1
                self.stdout.write(f'  Tentative {attempts} — nouvelle tentative dans 1s...')
                time.sleep(1)
