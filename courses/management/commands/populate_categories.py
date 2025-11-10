from django.core.management.base import BaseCommand
from courses.models import Category

class Command(BaseCommand):
    help = 'Populate the database with sample categories'

    def handle(self, *args, **options):
        categories = [
            {
                'name': 'Web Development',
                'description': 'Courses related to web development technologies including HTML, CSS, JavaScript, and frameworks'
            },
            {
                'name': 'Data Science',
                'description': 'Courses related to data analysis, machine learning, and artificial intelligence'
            },
            {
                'name': 'Business',
                'description': 'Courses related to business management, entrepreneurship, and leadership'
            },
            {
                'name': 'Design',
                'description': 'Courses related to graphic design, UI/UX, and creative arts'
            },
            {
                'name': 'Marketing',
                'description': 'Courses related to digital marketing, SEO, and social media strategies'
            },
            {
                'name': 'Programming',
                'description': 'Courses related to programming languages and software development'
            }
        ]

        created_count = 0
        for category_data in categories:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults={'description': category_data['description']}
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated {created_count} categories'
            )
        )