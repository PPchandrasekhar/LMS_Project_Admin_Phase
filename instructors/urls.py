from django.urls import path
from . import views

app_name = 'instructors'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('my-students/', views.my_students, name='my_students'),
    path('materials/', views.materials, name='materials'),
    path('materials/add/', views.add_material, name='add_material'),
    path('videos/', views.videos, name='videos'),
    path('videos/add/', views.add_video, name='add_video'),
    path('assignments/', views.assignments, name='assignments'),
    path('assignments/add/', views.add_assignment, name='add_assignment'),
    path('assignments/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/<int:assignment_id>/edit/', views.edit_assignment, name='edit_assignment'),
    path('assignments/<int:assignment_id>/delete/', views.delete_assignment, name='delete_assignment'),
    path('test-messages/', views.test_messages, name='test_messages'),
    path('schedule/', views.schedule, name='schedule'),
    path('schedule/add/', views.add_schedule_event, name='add_schedule_event'),
    path('schedule/<int:event_id>/edit/', views.edit_schedule_event, name='edit_schedule_event'),
    path('schedule/<int:event_id>/delete/', views.delete_schedule_event, name='delete_schedule_event'),
    path('messages/', views.messages_view, name='messages'),
    path('settings/', views.settings, name='settings'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]