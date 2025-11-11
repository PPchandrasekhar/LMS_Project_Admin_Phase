from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Instructor, ScheduleEvent
from courses.models import Course, Module, Lesson, Material, Video
from students.models import Student, Enrollment, Assignment, AssignmentSubmission
from .forms import AssignmentForm, ScheduleEventForm
from admin_panel.forms import MaterialForm, VideoForm

@login_required
def dashboard(request):
    # Get the instructor associated with the logged-in user
    try:
        instructor = request.user.instructor
    except Instructor.DoesNotExist:
        instructor = None
        messages.error(request, 'Instructor profile not found.')
        return redirect('login')
    
    # Get statistics for the instructor dashboard
    if instructor:
        total_courses = Course.objects.filter(instructor=instructor).count()
        
        # Get total students enrolled in instructor's courses
        total_students = Student.objects.filter(
            enrollments__course__instructor=instructor
        ).distinct().count()
        
        # Get total assignments for instructor's courses
        total_assignments = Assignment.objects.filter(course__instructor=instructor).count()
        
        # Get pending assignment submissions (not yet graded)
        pending_reviews = AssignmentSubmission.objects.filter(
            assignment__course__instructor=instructor,
            is_graded=False
        ).count()
        
        # Get recent activity (recent enrollments in instructor's courses)
        recent_activity = Enrollment.objects.filter(
            course__instructor=instructor
        ).select_related('student', 'course').order_by('-enrollment_date')[:5]
    else:
        total_courses = 0
        total_students = 0
        total_assignments = 0
        pending_reviews = 0
        recent_activity = []
    
    context = {
        'instructor': instructor,
        'total_courses': total_courses,
        'total_students': total_students,
        'total_assignments': total_assignments,
        'pending_reviews': pending_reviews,
        'recent_activity': recent_activity,
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
    
    # Add submission counts to each assignment
    for assignment in assignments:
        # Total submissions
        assignment.total_submissions = assignment.submissions.count()
        # Pending reviews (not graded)
        assignment.pending_reviews = assignment.submissions.filter(is_graded=False).count()
    
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


@login_required
def my_students(request):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # Get students enrolled in instructor's courses
    students = Student.objects.filter(
        enrollments__course__instructor=instructor
    ).distinct().order_by('last_name', 'first_name')
    
    paginator = Paginator(students, 10)  # Show 10 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'instructor': instructor,
        'page_obj': page_obj,
    }
    return render(request, 'instructors/my_students.html', context)


@login_required
def materials(request):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # Get materials for instructor's courses
    materials = Material.objects.filter(
        course__instructor=instructor
    ).select_related('course', 'module').order_by('-created_at')
    
    # Debug information
    print(f"Instructor: {instructor}")
    print(f"Materials count: {materials.count()}")
    for material in materials:
        print(f"Material: {material.title}, Course: {material.course.title}, Instructor: {material.course.instructor}")
    
    paginator = Paginator(materials, 12)  # Show 12 materials per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'instructor': instructor,
        'page_obj': page_obj,
    }
    return render(request, 'instructors/materials.html', context)


@login_required
def videos(request):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # Get videos for instructor's courses
    videos = Video.objects.filter(
        course__instructor=instructor
    ).select_related('course', 'module').order_by('-created_at')
    
    # Debug information
    print(f"Instructor: {instructor}")
    print(f"Videos count: {videos.count()}")
    for video in videos:
        print(f"Video: {video.title}, Course: {video.course.title}, Instructor: {video.course.instructor}")
    
    paginator = Paginator(videos, 12)  # Show 12 videos per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'instructor': instructor,
        'page_obj': page_obj,
    }
    return render(request, 'instructors/videos.html', context)


@login_required
def schedule(request):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # Get schedule events for this instructor
    events = ScheduleEvent.objects.filter(instructor=instructor).select_related('course').order_by('start_time')
    
    context = {
        'instructor': instructor,
        'events': events,
    }
    return render(request, 'instructors/schedule.html', context)


@login_required
def add_schedule_event(request):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    if request.method == 'POST':
        form = ScheduleEventForm(instructor, request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.instructor = instructor
            event.save()
            messages.success(request, 'Event created successfully.')
            return redirect('instructors:schedule')
    else:
        form = ScheduleEventForm(instructor=instructor)
    
    context = {
        'instructor': instructor,
        'form': form,
        'form_title': 'Create New Event',
        'submit_button': 'Create Event',
    }
    return render(request, 'instructors/schedule_event_form.html', context)


@login_required
def edit_schedule_event(request, event_id):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # Get the event (must be for this instructor)
    event = get_object_or_404(ScheduleEvent, id=event_id, instructor=instructor)
    
    if request.method == 'POST':
        form = ScheduleEventForm(instructor, request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully.')
            return redirect('instructors:schedule')
    else:
        form = ScheduleEventForm(instructor=instructor, instance=event)
    
    context = {
        'instructor': instructor,
        'form': form,
        'event': event,
        'form_title': 'Edit Event',
        'submit_button': 'Update Event',
    }
    return render(request, 'instructors/schedule_event_form.html', context)


@login_required
def delete_schedule_event(request, event_id):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # Get the event (must be for this instructor)
    event = get_object_or_404(ScheduleEvent, id=event_id, instructor=instructor)
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully.')
        return redirect('instructors:schedule')
    
    context = {
        'instructor': instructor,
        'event': event,
    }
    return render(request, 'instructors/schedule_event_confirm_delete.html', context)


@login_required
def messages_view(request):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # For now, just render a basic messages page
    context = {
        'instructor': instructor,
    }
    return render(request, 'instructors/messages.html', context)


@login_required
def settings(request):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # For now, just render a basic settings page
    context = {
        'instructor': instructor,
    }
    return render(request, 'instructors/settings.html', context)


@login_required
def about(request):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # For now, just render a basic about page
    context = {
        'instructor': instructor,
    }
    return render(request, 'instructors/about.html', context)


@login_required
def contact(request):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # For now, just render a basic contact page
    context = {
        'instructor': instructor,
    }
    return render(request, 'instructors/contact.html', context)


@login_required
def add_assignment(request):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    if request.method == 'POST':
        form = AssignmentForm(instructor, request.POST)
        if form.is_valid():
            assignment = form.save()
            messages.success(request, 'Assignment created successfully.')
            return redirect('instructors:assignments')
    else:
        form = AssignmentForm(instructor=instructor)
    
    context = {
        'instructor': instructor,
        'form': form,
        'form_title': 'Create New Assignment',
        'submit_button': 'Create Assignment',
    }
    return render(request, 'instructors/assignment_form.html', context)


@login_required
def edit_assignment(request, assignment_id):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # Get the assignment (must be for a course taught by this instructor)
    assignment = get_object_or_404(Assignment, id=assignment_id, course__instructor=instructor)
    
    if request.method == 'POST':
        form = AssignmentForm(instructor, request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated successfully.')
            return redirect('instructors:assignment_detail', assignment_id=assignment.id)
    else:
        form = AssignmentForm(instructor=instructor, instance=assignment)
    
    context = {
        'instructor': instructor,
        'form': form,
        'assignment': assignment,
        'form_title': 'Edit Assignment',
        'submit_button': 'Update Assignment',
    }
    return render(request, 'instructors/assignment_form.html', context)


@login_required
def delete_assignment(request, assignment_id):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    # Get the assignment (must be for a course taught by this instructor)
    assignment = get_object_or_404(Assignment, id=assignment_id, course__instructor=instructor)
    
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Assignment deleted successfully.')
        return redirect('instructors:assignments')
    
    context = {
        'instructor': instructor,
        'assignment': assignment,
    }
    return render(request, 'instructors/assignment_confirm_delete.html', context)


@login_required
def add_material(request):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = request.user
            material.save()
            messages.success(request, 'Material added successfully.')
            return redirect('instructors:materials')
    else:
        form = MaterialForm()
        # Filter courses to only those taught by this instructor
        form.fields['course'].queryset = Course.objects.filter(instructor=instructor)
    
    context = {
        'instructor': instructor,
        'form': form,
        'form_title': 'Add New Material',
        'submit_button': 'Add Material',
    }
    return render(request, 'instructors/material_form.html', context)


@login_required
def add_video(request):
    # Get the instructor profile
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructors:dashboard')
    
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.uploaded_by = request.user
            video.save()
            messages.success(request, 'Video added successfully.')
            return redirect('instructors:videos')
    else:
        form = VideoForm()
        # Filter courses to only those taught by this instructor
        form.fields['course'].queryset = Course.objects.filter(instructor=instructor)
    
    context = {
        'instructor': instructor,
        'form': form,
        'form_title': 'Add New Video',
        'submit_button': 'Add Video',
    }
    return render(request, 'instructors/video_form.html', context)


@login_required
def test_messages(request):
    messages.success(request, 'Test message - success')
    messages.error(request, 'Test message - error')
    messages.info(request, 'Test message - info')
    messages.warning(request, 'Test message - warning')
    return redirect('instructors:dashboard')
