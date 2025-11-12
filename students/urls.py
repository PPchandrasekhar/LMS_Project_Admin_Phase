from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('enroll-course/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('assignments/', views.assignments, name='assignments'),
    path('assignments/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('materials/', views.materials, name='materials'),
    path('videos/', views.videos, name='videos'),
    path('videos/<int:video_id>/', views.video_detail, name='video_detail'),
    path('schedule/', views.schedule, name='schedule'),
    path('messages/', views.messages_view, name='messages'),
    path('settings/', views.settings, name='settings'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('daily-attendance/', views.daily_attendance, name='daily_attendance'),
    path('daily-attendance/submit/', views.submit_daily_attendance, name='submit_daily_attendance'),
]