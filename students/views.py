from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from courses.models import Course
from .models import Student, Enrollment


@login_required
def dashboard(request):
    # Get the student profile
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None
    
    # Get enrolled courses
    if student:
        enrollments = Enrollment.objects.filter(student=student).select_related('course')
    else:
        enrollments = []
    
    context = {
        'student': student,
        'enrollments': enrollments,
    }
    return render(request, 'students/dashboard.html', context)


@login_required
def my_courses(request):
    # Get the student profile
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:dashboard')
    
    # Get enrolled courses
    enrollments = Enrollment.objects.filter(
        student=student
    ).select_related('course', 'course__category', 'course__instructor')
    
    paginator = Paginator(enrollments, 6)  # Show 6 courses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'student': student,
        'page_obj': page_obj,
    }
    return render(request, 'students/my_courses.html', context)


@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    # Get the student profile
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('courses:course_detail', course_id=course_id)
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=student, course=course).exists():
        messages.info(request, 'You are already enrolled in this course.')
    else:
        # Create enrollment
        Enrollment.objects.create(student=student, course=course)
        messages.success(request, f'Successfully enrolled in {course.title}!')
    
    return redirect('courses:course_detail', course_id=course_id)


@login_required
def profile(request):
    # Get the student profile
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None
    
    context = {
        'student': student,
    }
    return render(request, 'students/profile.html', context)


@login_required
def assignments(request):
    # Get the student profile
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:dashboard')
    
    # Get assignments
    submissions = student.submissions.select_related('assignment', 'assignment__course')
    
    context = {
        'student': student,
        'submissions': submissions,
    }
    return render(request, 'students/assignments.html', context)
