from django.urls import path
from . import views

app_name = 'instructors'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('my-students/', views.my_students, name='my_students'),
    path('materials/', views.materials, name='materials'),
    path('videos/', views.videos, name='videos'),
    path('assignments/', views.assignments, name='assignments'),
    path('assignments/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('schedule/', views.schedule, name='schedule'),
    path('messages/', views.messages, name='messages'),
    path('settings/', views.settings, name='settings'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]