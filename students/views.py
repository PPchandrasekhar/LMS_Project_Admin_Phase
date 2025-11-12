from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from courses.models import Course, Material, Video
from students.models import Student, Enrollment, AssignmentSubmission, Assignment, Attendance
from instructors.models import Instructor, ScheduleEvent

@login_required
def dashboard(request):
    # Get the student associated with the logged-in user
    try:
        student = request.user.student
    except Student.DoesNotExist:
        student = None
    
    if student:
        # Get key metrics
        total_enrollments = Enrollment.objects.filter(student=student).count()
        completed_courses = Enrollment.objects.filter(student=student, completion_status='completed').count()
        
        # Get pending assignments
        pending_assignments = Assignment.objects.filter(
            course__enrollments__student=student,
            submissions__isnull=True
        ).count()
        
        # Calculate average grade
        submissions = AssignmentSubmission.objects.filter(student=student, is_graded=True)
        if submissions.exists():
            total_points = sum([sub.grade for sub in submissions if sub.grade])
            max_points = sum([sub.assignment.max_points for sub in submissions if sub.assignment.max_points])
            if max_points > 0:
                average_grade = (total_points / max_points) * 100
            else:
                average_grade = 0
        else:
            average_grade = 0
        
        # Get recent enrollments
        recent_enrollments = Enrollment.objects.filter(student=student).select_related('course__instructor').order_by('-enrollment_date')[:5]
        
        context = {
            'student': student,
            'total_enrollments': total_enrollments,
            'completed_courses': completed_courses,
            'pending_assignments': pending_assignments,
            'average_grade': round(average_grade, 1),
            'recent_enrollments': recent_enrollments,
        }
    else:
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


@login_required
def assignments(request):
    # Get the student associated with the logged-in user
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:dashboard')
    
    # Get assignments for courses the student is enrolled in
    assignments = Assignment.objects.filter(
        course__enrollments__student=student
    ).select_related('course').order_by('due_date')
    
    # Add submission status to each assignment
    for assignment in assignments:
        try:
            submission = AssignmentSubmission.objects.get(
                assignment=assignment,
                student=student
            )
            assignment.submission_status = 'submitted'
            assignment.submission = submission
        except AssignmentSubmission.DoesNotExist:
            assignment.submission_status = 'not_submitted'
            assignment.submission = None
    
    context = {
        'student': student,
        'assignments': assignments,
    }
    return render(request, 'students/assignments.html', context)


@login_required
def assignment_detail(request, assignment_id):
    # Get the student associated with the logged-in user
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:dashboard')
    
    # Get the assignment (must be for a course the student is enrolled in)
    assignment = get_object_or_404(
        Assignment, 
        id=assignment_id,
        course__enrollments__student=student
    )
    
    # Get submission if it exists
    try:
        submission = AssignmentSubmission.objects.get(
            assignment=assignment,
            student=student
        )
    except AssignmentSubmission.DoesNotExist:
        submission = None
    
    context = {
        'student': student,
        'assignment': assignment,
        'submission': submission,
    }
    return render(request, 'students/assignment_detail.html', context)


@login_required
def submit_assignment(request, assignment_id):
    # Get the student associated with the logged-in user
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:dashboard')
    
    # Get the assignment (must be for a course the student is enrolled in)
    assignment = get_object_or_404(
        Assignment, 
        id=assignment_id,
        course__enrollments__student=student
    )
    
    # Check if already submitted
    try:
        submission = AssignmentSubmission.objects.get(
            assignment=assignment,
            student=student
        )
        # If already submitted and graded, don't allow resubmission
        if submission.is_graded:
            messages.error(request, 'This assignment has already been graded and cannot be resubmitted.')
            return redirect('students:assignment_detail', assignment_id=assignment.id)
    except AssignmentSubmission.DoesNotExist:
        submission = AssignmentSubmission(
            assignment=assignment,
            student=student
        )
    
    if request.method == 'POST':
        # Handle form submission
        submission_text = request.POST.get('submission_text', '')
        submission_file = request.FILES.get('submission_file')
        
        if not submission_text and not submission_file:
            messages.error(request, 'Please provide either text or a file for your submission.')
        else:
            submission.submission_text = submission_text
            submission.submission_file = submission_file
            submission.save()
            messages.success(request, 'Assignment submitted successfully.')
            return redirect('students:assignment_detail', assignment_id=assignment.id)
    else:
        # Display form
        pass
    
    context = {
        'student': student,
        'assignment': assignment,
        'submission': submission,
    }
    return render(request, 'students/assignment_submit.html', context)


@login_required
def materials(request):
    # Get the student associated with the logged-in user
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:dashboard')
    
    # Get materials for courses the student is enrolled in
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    course_ids = [enrollment.course.id for enrollment in enrollments]
    materials = Material.objects.filter(course_id__in=course_ids).select_related('course').order_by('-created_at')
    
    paginator = Paginator(materials, 10)  # Show 10 materials per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'student': student,
        'page_obj': page_obj,
    }
    return render(request, 'students/materials.html', context)


@login_required
def videos(request):
    # Get the student associated with the logged-in user
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:dashboard')
    
    # Get videos for courses the student is enrolled in
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    course_ids = [enrollment.course.id for enrollment in enrollments]
    videos = Video.objects.filter(course_id__in=course_ids).select_related('course').order_by('-created_at')
    
    paginator = Paginator(videos, 10)  # Show 10 videos per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'student': student,
        'page_obj': page_obj,
    }
    return render(request, 'students/videos.html', context)


@login_required
def video_detail(request, video_id):
    # Get the student associated with the logged-in user
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:dashboard')
    
    # Get the video (must be for a course the student is enrolled in)
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    course_ids = [enrollment.course.id for enrollment in enrollments]
    video = get_object_or_404(Video, id=video_id, course_id__in=course_ids)
    
    context = {
        'student': student,
        'video': video,
    }
    return render(request, 'students/video_detail.html', context)


@login_required
def schedule(request):
    # Get the student associated with the logged-in user
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:dashboard')
    
    # Get schedule events for courses the student is enrolled in
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    course_ids = [enrollment.course.id for enrollment in enrollments]
    events = ScheduleEvent.objects.filter(course_id__in=course_ids).select_related('course', 'instructor').order_by('start_time')
    
    context = {
        'student': student,
        'events': events,
    }
    return render(request, 'students/schedule.html', context)


@login_required
def messages_view(request):
    # Get the student associated with the logged-in user
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:dashboard')
    
    # For now, just render a basic messages page
    context = {
        'student': student,
    }
    return render(request, 'students/messages.html', context)


@login_required
def settings(request):
    # Get the student associated with the logged-in user
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:dashboard')
    
    if request.method == 'POST':
        # Handle form submission for updating student profile
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        date_of_birth = request.POST.get('date_of_birth')
        
        # Update student profile
        student.first_name = first_name
        student.last_name = last_name
        student.email = email
        student.phone = phone
        if date_of_birth:
            student.date_of_birth = date_of_birth
        student.save()
        
        messages.success(request, 'Profile updated successfully.')
        return redirect('students:settings')
    
    context = {
        'student': student,
    }
    return render(request, 'students/settings.html', context)


@login_required
def about(request):
    # Get the student associated with the logged-in user
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:dashboard')
    
    context = {
        'student': student,
    }
    return render(request, 'students/about.html', context)


@login_required
def contact(request):
    # Get the student associated with the logged-in user
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:dashboard')
    
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # In a real application, you would send an email or save to database
        # For now, just show a success message
        messages.success(request, 'Thank you for your message. We will get back to you soon.')
        return redirect('students:contact')
    
    context = {
        'student': student,
    }
    return render(request, 'students/contact.html', context)


@login_required
def daily_attendance(request):
    # Get the student profile
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:dashboard')
    
    # Get today's date
    today = timezone.now().date()
    
    # Get courses the student is enrolled in
    enrollments = Enrollment.objects.filter(
        student=student,
        completion_status__in=['enrolled', 'in_progress']
    ).select_related('course', 'course__instructor')
    
    # Get existing attendance records for today
    existing_attendances = Attendance.objects.filter(
        student=student,
        session_date=today
    ).select_related('course')
    
    # Create a dictionary for easy lookup
    attendance_dict = {att.course_id: att for att in existing_attendances}
    
    context = {
        'student': student,
        'enrollments': enrollments,
        'today': today,
        'attendance_dict': attendance_dict,
    }
    return render(request, 'students/daily_attendance.html', context)


@login_required
def submit_daily_attendance(request):
    # Get the student profile
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('students:dashboard')
    
    if request.method == 'POST':
        today = timezone.now().date()
        recorded_by = request.user
        
        # Process attendance for each course
        enrollment_ids = request.POST.getlist('enrollment_ids')
        notes = request.POST.get('notes', '')
        
        for enrollment_id in enrollment_ids:
            status_key = f'status_{enrollment_id}'
            if status_key in request.POST:
                status = request.POST[status_key]
                
                try:
                    enrollment = Enrollment.objects.get(id=enrollment_id, student=student)
                    
                    # Create or update attendance record
                    Attendance.objects.update_or_create(
                        student=student,
                        course=enrollment.course,
                        session_date=today,
                        defaults={
                            'status': status,
                            'notes': notes,
                            'recorded_by': recorded_by
                        }
                    )
                except Enrollment.DoesNotExist:
                    pass
        
        messages.success(request, 'Your daily attendance has been submitted successfully.')
        return redirect('students:daily_attendance')
    
    return redirect('students:daily_attendance')
