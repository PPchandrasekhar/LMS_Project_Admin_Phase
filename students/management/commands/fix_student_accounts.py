from django.core.management.base import BaseCommand
from students.models import Student
from django.contrib.auth.models import User
import random
import string

class Command(BaseCommand):
    help = 'Create user accounts for students who don\'t have them'

    def handle(self, *args, **options):
        students_without_users = Student.objects.filter(user=None)
        
        self.stdout.write(f"Found {students_without_users.count()} students without user accounts")
        
        for student in students_without_users:
            # Generate username from first and last name
            username = f"{student.first_name.lower()}.{student.last_name.lower()}"
            
            # Make sure username is unique
            original_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            # Generate a default password
            password = "student123"
            
            # Create the user
            user = User.objects.create_user(
                username=username,
                email=student.email,
                password=password,
                first_name=student.first_name,
                last_name=student.last_name
            )
            
            # Associate the user with the student
            student.user = user
            student.save()
            
            self.stdout.write(f"Created user account for {student.full_name} (ID: {student.student_id})")
            self.stdout.write(f"  Username: {username}")
            self.stdout.write(f"  Password: {password}")
            self.stdout.write("")
        
        self.stdout.write(self.style.SUCCESS("All student accounts have been updated!"))