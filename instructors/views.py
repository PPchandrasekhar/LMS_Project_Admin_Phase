from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from courses.models import Course, Module, Lesson
from students.models import Assignment, AssignmentSubmission
from .models import Instructor


@login_required
def dashboard(request):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        instructor = None
    
    # Get courses taught by this instructor
    if instructor:
        courses = Course.objects.filter(instructor=instructor)
    else:
        courses = []
    
    context = {
        'instructor': instructor,
        'courses': courses,
    }
    return render(request, 'instructors/dashboard.html', context)


@login_required
def my_courses(request):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # Get courses taught by this instructor
    courses = Course.objects.filter(instructor=instructor)
    
    paginator = Paginator(courses, 6)  # Show 6 courses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'instructor': instructor,
        'page_obj': page_obj,
    }
    return render(request, 'instructors/my_courses.html', context)


@login_required
def course_detail(request, course_id):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # Get the course (must be taught by this instructor)
    course = get_object_or_404(Course, id=course_id, instructor=instructor)
    modules = Module.objects.filter(course=course).prefetch_related('lessons')
    
    context = {
        'instructor': instructor,
        'course': course,
        'modules': modules,
    }
    return render(request, 'instructors/course_detail.html', context)


@login_required
def lesson_list(request, course_id):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # Get the course (must be taught by this instructor)
    course = get_object_or_404(Course, id=course_id, instructor=instructor)
    modules = Module.objects.filter(course=course).prefetch_related('lessons')
    
    context = {
        'instructor': instructor,
        'course': course,
        'modules': modules,
    }
    return render(request, 'instructors/lesson_list.html', context)


@login_required
def add_lesson(request, course_id):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # Get the course (must be taught by this instructor)
    course = get_object_or_404(Course, id=course_id, instructor=instructor)
    
    if request.method == 'POST':
        # Handle form submission
        pass
    else:
        # Display empty form
        pass
    
    context = {
        'instructor': instructor,
        'course': course,
    }
    return render(request, 'instructors/lesson_form.html', context)


@login_required
def edit_lesson(request, lesson_id):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # Get the lesson (must be in a course taught by this instructor)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course__instructor=instructor)
    
    if request.method == 'POST':
        # Handle form submission
        pass
    else:
        # Display form with existing data
        pass
    
    context = {
        'instructor': instructor,
        'lesson': lesson,
    }
    return render(request, 'instructors/lesson_form.html', context)


@login_required
def delete_lesson(request, lesson_id):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # Get the lesson (must be in a course taught by this instructor)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course__instructor=instructor)
    
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Lesson deleted successfully.')
        return redirect('instructors:lesson_list', course_id=lesson.module.course.id)
    
    context = {
        'instructor': instructor,
        'lesson': lesson,
    }
    return render(request, 'instructors/lesson_confirm_delete.html', context)


@login_required
def assignments(request):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # Get assignments for courses taught by this instructor
    assignments = Assignment.objects.filter(course__instructor=instructor).select_related('course')
    
    context = {
        'instructor': instructor,
        'assignments': assignments,
    }
    return render(request, 'instructors/assignments.html', context)


@login_required
def assignment_detail(request, assignment_id):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # Get the assignment (must be for a course taught by this instructor)
    assignment = get_object_or_404(Assignment, id=assignment_id, course__instructor=instructor)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment).select_related('student')
    
    context = {
        'instructor': instructor,
        'assignment': assignment,
        'submissions': submissions,
    }
    return render(request, 'instructors/assignment_detail.html', context)


@login_required
def submission_list(request, assignment_id):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # Get the assignment (must be for a course taught by this instructor)
    assignment = get_object_or_404(Assignment, id=assignment_id, course__instructor=instructor)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment).select_related('student')
    
    paginator = Paginator(submissions, 10)  # Show 10 submissions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'instructor': instructor,
        'assignment': assignment,
        'page_obj': page_obj,
    }
    return render(request, 'instructors/submission_list.html', context)


@login_required
def profile(request):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        instructor = None
    
    context = {
        'instructor': instructor,
    }
    return render(request, 'instructors/profile.html', context)
