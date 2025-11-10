from django.urls import path
from . import views

app_name = 'instructors'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('courses/', views.my_courses, name='my_courses'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/lessons/', views.lesson_list, name='lesson_list'),
    path('courses/<int:course_id>/lessons/add/', views.add_lesson, name='add_lesson'),
    path('lessons/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('lessons/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),
    path('assignments/', views.assignments, name='assignments'),
    path('assignments/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/<int:assignment_id>/submissions/', views.submission_list, name='submission_list'),
    path('profile/', views.profile, name='profile'),
]