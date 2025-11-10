from django.core.management.base import BaseCommand
from instructors.models import Instructor
from django.contrib.auth.models import User
import random
import string

class Command(BaseCommand):
    help = 'Create user accounts for instructors that don\'t have them or reset passwords for existing ones'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            help='Default password for created users',
            default='trainer123'
        )
        parser.add_argument(
            '--reset-all',
            action='store_true',
            help='Reset passwords for all trainers',
            default=False
        )

    def handle(self, *args, **options):
        password = options['password']
        reset_all = options['reset_all']
        created_count = 0
        reset_count = 0
        
        if reset_all:
            # Reset passwords for all instructors
            instructors = Instructor.objects.all()
            for instructor in instructors:
                if instructor.user:
                    instructor.user.set_password(password)
                    instructor.user.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Reset password for trainer "{instructor.full_name}" (username: {instructor.user.username})'
                        )
                    )
                    reset_count += 1
                else:
                    # Create user if doesn't exist
                    self.create_user_for_instructor(instructor, password)
                    created_count += 1
        else:
            # Get all instructors without user accounts
            instructors = Instructor.objects.filter(user__isnull=True)
            for instructor in instructors:
                self.create_user_for_instructor(instructor, password)
                created_count += 1
        
        if created_count == 0 and reset_count == 0 and not reset_all:
            self.stdout.write(
                self.style.WARNING('No instructors without user accounts found.')
            )
        else:
            if reset_all:
                self.stdout.write(
                    self.style.SUCCESS(f'Reset passwords for {reset_count} trainers.')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Created {created_count} user accounts.')
                )
    
    def create_user_for_instructor(self, instructor, password):
        # Generate username from first and last name
        username = f"{instructor.first_name.lower()}.{instructor.last_name.lower()}"
        
        # Make sure username is unique
        original_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        
        # Create the user
        user = User.objects.create_user(
            username=username,
            email=instructor.email,
            password=password,
            first_name=instructor.first_name,
            last_name=instructor.last_name
        )
        
        # Associate the user with the instructor
        instructor.user = user
        instructor.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created user "{username}" for instructor "{instructor.full_name}" with password "{password}"'
            )
        )