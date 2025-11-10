from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Course, Category, Module, Lesson
from students.models import Enrollment


def course_list(request):
    courses = Course.objects.filter(is_published=True).select_related('category', 'instructor')
    categories = Category.objects.all()
    
    # Filter by category if provided
    category_id = request.GET.get('category')
    if category_id:
        courses = courses.filter(category_id=category_id)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        courses = courses.filter(title__icontains=search_query)
    
    paginator = Paginator(courses, 6)  # Show 6 courses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_id,
        'search_query': search_query,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_published=True)
    modules = course.modules.all().prefetch_related('lessons')
    
    # Check if student is enrolled
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            student__user=request.user, 
            course=course
        ).exists()
    
    context = {
        'course': course,
        'modules': modules,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'courses/course_detail.html', context)


def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, is_published=True)
    course = lesson.module.course
    
    # Check if student is enrolled
    if not request.user.is_authenticated:
        messages.warning(request, 'You need to be logged in to access lessons.')
        return redirect('courses:course_detail', course_id=course.id)
    
    is_enrolled = Enrollment.objects.filter(
        student__user=request.user, 
        course=course
    ).exists()
    
    if not is_enrolled:
        messages.warning(request, 'You need to be enrolled in this course to access lessons.')
        return redirect('courses:course_detail', course_id=course.id)
    
    # Get next and previous lessons
    module = lesson.module
    lessons = Lesson.objects.filter(module=module, is_published=True).order_by('order')
    lesson_ids = list(lessons.values_list('id', flat=True))
    current_index = lesson_ids.index(lesson.id)
    
    prev_lesson = None
    next_lesson = None
    
    if current_index > 0:
        prev_lesson = lessons[current_index - 1]
    if current_index < len(lesson_ids) - 1:
        next_lesson = lessons[current_index + 1]
    
    context = {
        'lesson': lesson,
        'course': course,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
    }
    return render(request, 'courses/lesson_detail.html', context)
