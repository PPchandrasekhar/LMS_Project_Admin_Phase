from django.db import models
from django.contrib.auth.models import User

class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    instructor_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='instructor_profiles/', blank=True, null=True)
    hire_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.instructor_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class ScheduleEvent(models.Model):
    EVENT_TYPES = [
        ('lecture', 'Lecture'),
        ('workshop', 'Workshop'),
        ('meeting', 'Meeting'),
        ('exam', 'Exam'),
        ('other', 'Other'),
    ]
    
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='schedule_events')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='schedule_events', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='lecture')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    is_recurring = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.start_time}"

    class Meta:
        ordering = ['start_time']