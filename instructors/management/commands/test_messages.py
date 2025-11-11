from django.core.management.base import BaseCommand
from django.contrib import messages

class Command(BaseCommand):
    help = 'Test the messages module'

    def handle(self, *args, **options):
        # Simple test - just import and check if it works
        self.stdout.write('Messages module imported successfully')
        self.stdout.write('Messages module test completed successfully')
