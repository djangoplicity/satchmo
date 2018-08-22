from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = "Load Satchmo country (l10n) data."

    def handle_noargs(self, **options):
        """Load l10n fixtures"""
        call_command('loaddata', 'l10n_data.xml', interactive=True)
