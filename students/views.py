from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Student, Enrollment
from courses.models import Course

@login_required
def dashboard(request):
    # Get the student associated with the logged-in user
    try:
        student = request.user.student
    except Student.DoesNotExist:
        student = None
    
    context = {
        'student': student,
    }
    return render(request, 'students/dashboard.html', context)


@login_required
def my_courses(request):
    # Get the student associated with the logged-in user
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:dashboard')
    
    # Get enrollments for this student
    enrollments = Enrollment.objects.filter(student=student).select_related('course__category', 'course__instructor')
    
    paginator = Paginator(enrollments, 6)  # Show 6 enrollments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'student': student,
        'page_obj': page_obj,
    }
    return render(request, 'students/my_courses.html', context)


@login_required
def enroll_course(request, course_id):
    # Get the student associated with the logged-in user
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:dashboard')
    
    # Get the course
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=student, course=course).exists():
        messages.info(request, 'You are already enrolled in this course.')
        return redirect('courses:course_detail', course_id=course.id)
    
    # Create enrollment
    Enrollment.objects.create(
        student=student,
        course=course,
        completion_status='enrolled',
        progress=0
    )
    
    messages.success(request, f'You have been successfully enrolled in "{course.title}".')
    return redirect('courses:course_detail', course_id=course.id)