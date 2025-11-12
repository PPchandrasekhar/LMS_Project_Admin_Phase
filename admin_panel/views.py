from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from courses.models import Course, Category, Material, Video
from students.models import Student, Enrollment, AssignmentSubmission, Attendance, TrainerAttendance
from students.forms import AttendanceForm, BulkAttendanceForm, TrainerAttendanceForm
from instructors.models import Instructor
from .forms import CourseForm, StudentForm, InstructorForm, CategoryForm, MaterialForm, VideoForm, EnrollmentForm


def is_admin(user):
    return user.is_staff


@login_required
@user_passes_test(is_admin)
def dashboard(request):
    # Get statistics for the dashboard
    total_courses = Course.objects.count()
    total_students = Student.objects.count()
    total_instructors = Instructor.objects.count()
    total_materials = Material.objects.count()
    total_videos = Video.objects.count()
    
    # Get recent data
    recent_courses = Course.objects.select_related('category', 'instructor').order_by('-created_at')[:5]
    recent_students = Student.objects.order_by('-created_at')[:5]
    recent_enrollments = Enrollment.objects.select_related('student', 'course').order_by('-enrollment_date')[:5]
    
    # Get category distribution for pie chart
    categories = Category.objects.prefetch_related('courses').all()
    category_data = []
    category_labels = []
    category_colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#8b4513', '#9370db', '#20b2aa']
    
    for i, category in enumerate(categories):
        course_count = category.courses.count()
        if course_count > 0:
            category_labels.append(category.name)
            category_data.append(course_count)
    
    # Ensure we have enough colors
    while len(category_colors) < len(category_labels):
        category_colors.extend(['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b'])
    
    # Create category legend HTML
    category_legend_html = ''
    for i, label in enumerate(category_labels):
        color = category_colors[i] if i < len(category_colors) else '#4e73df'
        category_legend_html += f'<span class="mr-2"><i class="bi bi-circle-fill" style="color: {color};"></i> {label}</span>'
    
    # Get enrollment data for area chart (last 12 months)
    import datetime
    from django.db.models import Count
    
    # Create a list of the last 12 months
    today = datetime.date.today()
    months = []
    enrollment_data = []
    
    for i in range(11, -1, -1):
        date = today - datetime.timedelta(days=30*i)
        month_name = date.strftime('%b')
        months.append(month_name)
        
        # Count enrollments for this month
        start_date = date.replace(day=1)
        if date.month == 12:
            end_date = date.replace(year=date.year+1, month=1, day=1)
        else:
            end_date = date.replace(month=date.month+1, day=1)
            
        count = Enrollment.objects.filter(
            enrollment_date__gte=start_date,
            enrollment_date__lt=end_date
        ).count()
        enrollment_data.append(count)
    
    context = {
        'total_courses': total_courses,
        'total_students': total_students,
        'total_instructors': total_instructors,
        'total_materials': total_materials,
        'total_videos': total_videos,
        'recent_courses': recent_courses,
        'recent_students': recent_students,
        'recent_enrollments': recent_enrollments,
        'category_labels': category_labels,
        'category_data': category_data,
        'category_colors': category_colors[:len(category_labels)],
        'category_legend_html': category_legend_html,
        'months': months,
        'enrollment_data': enrollment_data,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def trainer_list(request):
    trainers = Instructor.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        trainers = trainers.filter(
            Q(instructor_id__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filter by status
    status = request.GET.get('status')
    if status == 'active':
        trainers = trainers.filter(is_active=True)
    elif status == 'inactive':
        trainers = trainers.filter(is_active=False)
    
    paginator = Paginator(trainers, 10)  # Show 10 trainers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'current_status': status,
    }
    return render(request, 'admin_panel/trainer_list.html', context)


@login_required
@user_passes_test(is_admin)
def material_list(request):
    materials = Material.objects.select_related('course', 'module', 'uploaded_by').all()
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        materials = materials.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by material type
    material_type = request.GET.get('type')
    if material_type:
        materials = materials.filter(material_type=material_type)
    
    paginator = Paginator(materials, 12)  # Show 12 materials per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'current_type': material_type,
    }
    return render(request, 'admin_panel/material_list.html', context)


@login_required
@user_passes_test(is_admin)
def add_material(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = request.user
            material.save()
            messages.success(request, 'Material added successfully.')
            return redirect('admin_panel:material_list')
    else:
        form = MaterialForm()
    
    context = {
        'form_title': 'Add New Material',
        'submit_button': 'Add Material',
        'form': form,
    }
    return render(request, 'admin_panel/material_form.html', context)


@login_required
@user_passes_test(is_admin)
def edit_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material updated successfully.')
            return redirect('admin_panel:material_list')
    else:
        form = MaterialForm(instance=material)
    
    context = {
        'form_title': 'Edit Material',
        'submit_button': 'Update Material',
        'form': form,
        'material': material,
    }
    return render(request, 'admin_panel/material_form.html', context)


@login_required
@user_passes_test(is_admin)
def delete_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    
    if request.method == 'POST':
        material.file.delete()  # Delete the file from storage
        material.delete()
        messages.success(request, 'Material deleted successfully.')
        return redirect('admin_panel:material_list')
    
    context = {
        'material': material,
    }
    return render(request, 'admin_panel/material_confirm_delete.html', context)


@login_required
@user_passes_test(is_admin)
def video_list(request):
    videos = Video.objects.select_related('course', 'module', 'uploaded_by').all()
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        videos = videos.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by course
    course_id = request.GET.get('course')
    if course_id:
        videos = videos.filter(course_id=course_id)
    
    paginator = Paginator(videos, 10)  # Show 10 videos per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all courses for filter dropdown
    courses = Course.objects.all()
    
    context = {
        'page_obj': page_obj,
        'courses': courses,
        'search_query': search_query,
        'current_course': course_id,
    }
    return render(request, 'admin_panel/video_list.html', context)


@login_required
@user_passes_test(is_admin)
def add_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.uploaded_by = request.user
            video.save()
            messages.success(request, 'Video added successfully.')
            return redirect('admin_panel:video_list')
    else:
        form = VideoForm()
    
    context = {
        'form_title': 'Add New Video',
        'submit_button': 'Add Video',
        'form': form,
    }
    return render(request, 'admin_panel/video_form.html', context)


@login_required
@user_passes_test(is_admin)
def edit_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            form.save()
            messages.success(request, 'Video updated successfully.')
            return redirect('admin_panel:video_list')
    else:
        form = VideoForm(instance=video)
    
    context = {
        'form_title': 'Edit Video',
        'submit_button': 'Update Video',
        'form': form,
        'video': video,
    }
    return render(request, 'admin_panel/video_form.html', context)


@login_required
@user_passes_test(is_admin)
def delete_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    
    if request.method == 'POST':
        if video.video_file:
            video.video_file.delete()  # Delete the file from storage
        video.delete()
        messages.success(request, 'Video deleted successfully.')
        return redirect('admin_panel:video_list')
    
    context = {
        'video': video,
    }
    return render(request, 'admin_panel/video_confirm_delete.html', context)


@login_required
@user_passes_test(is_admin)
def analytics(request):
    # Get statistics for analytics
    total_courses = Course.objects.count()
    total_students = Student.objects.count()
    total_instructors = Instructor.objects.count()
    total_materials = Material.objects.count()
    total_videos = Video.objects.count()
    total_enrollments = Enrollment.objects.count()
    
    # Calculate revenue (assuming $100 per course enrollment)
    total_revenue = total_enrollments * 100
    
    # Get recent data
    recent_courses = Course.objects.select_related('category', 'instructor').order_by('-created_at')[:5]
    recent_students = Student.objects.order_by('-created_at')[:5]
    recent_enrollments = Enrollment.objects.select_related('student', 'course').order_by('-enrollment_date')[:5]
    
    # Get top performing courses by enrollment
    from django.db.models import Count
    top_courses = Course.objects.annotate(
        enrollment_count=Count('enrollments')
    ).filter(enrollment_count__gt=0).order_by('-enrollment_count')[:5]
    
    # Add completion rate to each course
    for course in top_courses:
        if course.enrollment_count > 0:
            completed_count = course.enrollments.filter(completion_status='completed').count()
            course.completion_rate = round((completed_count / course.enrollment_count) * 100) if course.enrollment_count > 0 else 0
        else:
            course.completion_rate = 0
    
    # Get category distribution for pie chart
    categories = Category.objects.prefetch_related('courses').all()
    category_data = []
    category_labels = []
    category_colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#8b4513', '#9370db', '#20b2aa']
    
    for i, category in enumerate(categories):
        course_count = category.courses.count()
        if course_count > 0:
            category_labels.append(category.name)
            category_data.append(course_count)
    
    # Ensure we have enough colors
    while len(category_colors) < len(category_labels):
        category_colors.extend(['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b'])
    
    # Get enrollment data for area chart (last 12 months)
    import datetime
    from django.db.models import Count
    
    # Create a list of the last 12 months
    today = datetime.date.today()
    months = []
    enrollment_data = []
    
    for i in range(11, -1, -1):
        date = today - datetime.timedelta(days=30*i)
        month_name = date.strftime('%b')
        months.append(month_name)
        
        # Count enrollments for this month
        start_date = date.replace(day=1)
        if date.month == 12:
            end_date = date.replace(year=date.year+1, month=1, day=1)
        else:
            end_date = date.replace(month=date.month+1, day=1)
            
        count = Enrollment.objects.filter(
            enrollment_date__gte=start_date,
            enrollment_date__lt=end_date
        ).count()
        enrollment_data.append(count)
    
    # Calculate completion rate
    completed_enrollments = Enrollment.objects.filter(completion_status='completed').count()
    if total_enrollments > 0:
        completion_rate = round((completed_enrollments / total_enrollments) * 100)
    else:
        completion_rate = 0
    
    # Get pending assignments
    pending_assignments = AssignmentSubmission.objects.filter(is_graded=False).count()
    
    # Create category legend HTML
    category_legend_html = ''
    for i, label in enumerate(category_labels):
        color = category_colors[i] if i < len(category_colors) else '#4e73df'
        category_legend_html += f'<span class="mr-2"><i class="bi bi-circle-fill" style="color: {color};"></i> {label}</span>'
    
    context = {
        'total_courses': total_courses,
        'total_students': total_students,
        'total_instructors': total_instructors,
        'total_revenue': total_revenue,
        'total_enrollments': total_enrollments,
        'completion_rate': completion_rate,
        'pending_assignments': pending_assignments,
        'recent_courses': recent_courses,
        'recent_students': recent_students,
        'recent_enrollments': recent_enrollments,
        'top_courses': top_courses,
        'category_labels': category_labels,
        'category_data': category_data,
        'category_colors': category_colors[:len(category_labels)],
        'category_legend_html': category_legend_html,
        'months': months,
        'enrollment_data': enrollment_data,
    }
    return render(request, 'admin_panel/analytics.html', context)


@login_required
@user_passes_test(is_admin)
def settings(request):
    # For now, we'll show a placeholder page
    context = {
        'settings': {},
    }
    return render(request, 'admin_panel/settings.html', context)


@login_required
@user_passes_test(is_admin)
def contact(request):
    # For now, we'll show a placeholder page
    context = {
        'contact_info': {},
    }
    return render(request, 'admin_panel/contact.html', context)


@login_required
@user_passes_test(is_admin)
def about(request):
    # For now, we'll show a placeholder page
    context = {
        'about_info': {},
    }
    return render(request, 'admin_panel/about.html', context)


@login_required
@user_passes_test(is_admin)
def course_list(request):
    courses = Course.objects.select_related('category', 'instructor').all()
    categories = Category.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        courses = courses.filter(category_id=category_id)
    
    paginator = Paginator(courses, 10)  # Show 10 courses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'current_category': category_id,
    }
    return render(request, 'admin_panel/course_list.html', context)


@login_required
@user_passes_test(is_admin)
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course added successfully.')
            return redirect('admin_panel:course_list')
    else:
        form = CourseForm()
    
    context = {
        'form_title': 'Add New Course',
        'submit_button': 'Add Course',
        'form': form,
    }
    return render(request, 'admin_panel/course_form.html', context)


@login_required
@user_passes_test(is_admin)
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully.')
            return redirect('admin_panel:course_list')
    else:
        form = CourseForm(instance=course)
    
    context = {
        'form_title': 'Edit Course',
        'submit_button': 'Update Course',
        'form': form,
        'course': course,
    }
    return render(request, 'admin_panel/course_form.html', context)


@login_required
@user_passes_test(is_admin)
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully.')
        return redirect('admin_panel:course_list')
    
    context = {
        'course': course,
    }
    return render(request, 'admin_panel/course_confirm_delete.html', context)


@login_required
@user_passes_test(is_admin)
def student_list(request):
    students = Student.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        students = students.filter(
            Q(student_id__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filter by status
    status = request.GET.get('status')
    if status == 'active':
        students = students.filter(is_active=True)
    elif status == 'inactive':
        students = students.filter(is_active=False)
    
    paginator = Paginator(students, 10)  # Show 10 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'current_status': status,
    }
    return render(request, 'admin_panel/student_list.html', context)


@login_required
@user_passes_test(is_admin)
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            # Get the generated password if it was auto-generated
            password = form.cleaned_data.get('password')
            if not password:
                # If no password was provided, it was auto-generated
                # In a real application, you would send this to the student via email
                # For now, we'll just show a message
                messages.success(request, f'Student added successfully. Default password is "student123".')
            else:
                messages.success(request, 'Student added successfully.')
            return redirect('admin_panel:student_list')
    else:
        form = StudentForm()
    
    context = {
        'form_title': 'Add New Student',
        'submit_button': 'Add Student',
        'form': form,
    }
    return render(request, 'admin_panel/student_form.html', context)


@login_required
@user_passes_test(is_admin)
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully.')
            return redirect('admin_panel:student_list')
    else:
        form = StudentForm(instance=student)
    
    context = {
        'form_title': 'Edit Student',
        'submit_button': 'Update Student',
        'form': form,
        'student': student,
    }
    return render(request, 'admin_panel/student_form.html', context)


@login_required
@user_passes_test(is_admin)
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        if student.user:  # Only delete associated user if it exists
            student.user.delete()
        student.delete()
        messages.success(request, 'Student deleted successfully.')
        return redirect('admin_panel:student_list')
    
    context = {
        'student': student,
    }
    return render(request, 'admin_panel/student_confirm_delete.html', context)


@login_required
@user_passes_test(is_admin)
def instructor_list(request):
    instructors = Instructor.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        instructors = instructors.filter(
            Q(instructor_id__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filter by status
    status = request.GET.get('status')
    if status == 'active':
        instructors = instructors.filter(is_active=True)
    elif status == 'inactive':
        instructors = instructors.filter(is_active=False)
    
    paginator = Paginator(instructors, 10)  # Show 10 instructors per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'current_status': status,
    }
    return render(request, 'admin_panel/instructor_list.html', context)


@login_required
@user_passes_test(is_admin)
def add_instructor(request):
    if request.method == 'POST':
        form = InstructorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Instructor added successfully.')
            return redirect('admin_panel:trainer_list')
    else:
        form = InstructorForm()
    
    context = {
        'form_title': 'Add New Instructor',
        'submit_button': 'Add Instructor',
        'form': form,
    }
    return render(request, 'admin_panel/instructor_form.html', context)


@login_required
@user_passes_test(is_admin)
def edit_instructor(request, instructor_id):
    instructor = get_object_or_404(Instructor, id=instructor_id)
    
    if request.method == 'POST':
        form = InstructorForm(request.POST, request.FILES, instance=instructor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Instructor updated successfully.')
            return redirect('admin_panel:trainer_list')
    else:
        form = InstructorForm(instance=instructor)
    
    context = {
        'form_title': 'Edit Instructor',
        'submit_button': 'Update Instructor',
        'form': form,
        'instructor': instructor,
    }
    return render(request, 'admin_panel/instructor_form.html', context)


@login_required
@user_passes_test(is_admin)
def delete_instructor(request, instructor_id):
    instructor = get_object_or_404(Instructor, id=instructor_id)
    
    if request.method == 'POST':
        if instructor.user:  # Only delete associated user if it exists
            instructor.user.delete()
        instructor.delete()
        messages.success(request, 'Instructor deleted successfully.')
        return redirect('admin_panel:trainer_list')
    
    context = {
        'instructor': instructor,
    }
    return render(request, 'admin_panel/instructor_confirm_delete.html', context)


@login_required
@user_passes_test(is_admin)
def category_list(request):
    categories = Category.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        categories = categories.filter(name__icontains=search_query)
    
    paginator = Paginator(categories, 10)  # Show 10 categories per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'admin_panel/category_list.html', context)


@login_required
@user_passes_test(is_admin)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('admin_panel:category_list')
    else:
        form = CategoryForm()
    
    context = {
        'form_title': 'Add New Category',
        'submit_button': 'Add Category',
        'form': form,
    }
    return render(request, 'admin_panel/category_form.html', context)


@login_required
@user_passes_test(is_admin)
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('admin_panel:category_list')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form_title': 'Edit Category',
        'submit_button': 'Update Category',
        'form': form,
        'category': category,
    }
    return render(request, 'admin_panel/category_form.html', context)


@login_required
@user_passes_test(is_admin)
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('admin_panel:category_list')
    
    context = {
        'category': category,
    }
    return render(request, 'admin_panel/category_confirm_delete.html', context)


@login_required
@user_passes_test(is_admin)
def enrollment_list(request):
    enrollments = Enrollment.objects.select_related('student', 'course').all()
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        enrollments = enrollments.filter(
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query) |
            Q(course__title__icontains=search_query)
        )
    
    # Filter by course
    course_id = request.GET.get('course')
    if course_id:
        enrollments = enrollments.filter(course_id=course_id)
    
    # Filter by student
    student_id = request.GET.get('student')
    if student_id:
        enrollments = enrollments.filter(student_id=student_id)
    
    paginator = Paginator(enrollments, 10)  # Show 10 enrollments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all courses and students for filter dropdowns
    courses = Course.objects.all()
    students = Student.objects.all()
    
    context = {
        'page_obj': page_obj,
        'courses': courses,
        'students': students,
        'search_query': search_query,
        'current_course': course_id,
        'current_student': student_id,
    }
    return render(request, 'admin_panel/enrollment_list.html', context)


@login_required
@user_passes_test(is_admin)
def add_enrollment(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            # Check if enrollment already exists
            student = form.cleaned_data['student']
            course = form.cleaned_data['course']
            
            if Enrollment.objects.filter(student=student, course=course).exists():
                messages.error(request, 'This student is already enrolled in this course.')
            else:
                enrollment = form.save(commit=False)
                enrollment.completion_status = 'enrolled'
                enrollment.progress = 0
                enrollment.save()
                messages.success(request, 'Enrollment added successfully.')
                return redirect('admin_panel:enrollment_list')
    else:
        form = EnrollmentForm()
    
    context = {
        'form_title': 'Add New Enrollment',
        'submit_button': 'Add Enrollment',
        'form': form,
    }
    return render(request, 'admin_panel/enrollment_form.html', context)


@login_required
@user_passes_test(is_admin)
def delete_enrollment(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    if request.method == 'POST':
        enrollment.delete()
        messages.success(request, 'Enrollment deleted successfully.')
        return redirect('admin_panel:enrollment_list')
    
    context = {
        'enrollment': enrollment,
    }
    return render(request, 'admin_panel/enrollment_confirm_delete.html', context)


@login_required
@user_passes_test(is_admin)
def daily_attendance(request):
    """Daily attendance report page for admin"""
    # Get the selected date or default to today
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        try:
            selected_date = timezone.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
    
    # Get attendance records for the selected date
    student_attendances = Attendance.objects.filter(session_date=selected_date).select_related('student', 'course')
    trainer_attendances = TrainerAttendance.objects.filter(session_date=selected_date).select_related('trainer', 'course')
    
    # Get summary statistics
    total_students = Student.objects.count()
    total_trainers = Instructor.objects.count()
    students_present = student_attendances.filter(status='present').count()
    trainers_present = trainer_attendances.filter(status='present').count()
    
    context = {
        'selected_date': selected_date,
        'student_attendances': student_attendances,
        'trainer_attendances': trainer_attendances,
        'total_students': total_students,
        'total_trainers': total_trainers,
        'students_present': students_present,
        'trainers_present': trainers_present,
    }
    return render(request, 'admin_panel/daily_attendance.html', context)


@login_required
@user_passes_test(is_admin)
def submit_daily_attendance(request):
    """Submit daily attendance for students and trainers"""
    if request.method == 'POST':
        today = timezone.now().date()
        recorded_by = request.user
        
        # Process student attendance
        student_ids = request.POST.getlist('student_ids')
        student_statuses = request.POST.getlist('student_status')
        student_courses = request.POST.getlist('student_course')
        student_notes = request.POST.get('student_notes', '')
        
        for i, student_id in enumerate(student_ids):
            if i < len(student_statuses) and i < len(student_courses):
                try:
                    student = Student.objects.get(id=student_id)
                    course = Course.objects.get(id=student_courses[i])
                    status = student_statuses[i]
                    
                    # Create or update attendance record
                    Attendance.objects.update_or_create(
                        student=student,
                        course=course,
                        session_date=today,
                        defaults={
                            'status': status,
                            'notes': student_notes,
                            'recorded_by': recorded_by
                        }
                    )
                except (Student.DoesNotExist, Course.DoesNotExist):
                    pass
        
        # Process trainer attendance
        trainer_ids = request.POST.getlist('trainer_ids')
        trainer_statuses = request.POST.getlist('trainer_status')
        trainer_courses = request.POST.getlist('trainer_course')
        trainer_notes = request.POST.get('trainer_notes', '')
        
        for i, trainer_id in enumerate(trainer_ids):
            if i < len(trainer_statuses) and i < len(trainer_courses):
                try:
                    trainer = Instructor.objects.get(id=trainer_id)
                    course = Course.objects.get(id=trainer_courses[i])
                    status = trainer_statuses[i]
                    
                    # Create or update trainer attendance record
                    TrainerAttendance.objects.update_or_create(
                        trainer=trainer,
                        course=course,
                        session_date=today,
                        defaults={
                            'status': status,
                            'notes': trainer_notes,
                            'recorded_by': recorded_by
                        }
                    )
                except (Instructor.DoesNotExist, Course.DoesNotExist):
                    pass
        
        messages.success(request, 'Daily attendance records submitted successfully.')
        return redirect('admin_panel:daily_attendance')
    
    return redirect('admin_panel:daily_attendance')


from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from instructors.models import Instructor
from students.models import Student


def custom_login(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        
        if user_type == 'admin':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('admin_panel:dashboard')
            else:
                messages.error(request, 'Invalid admin credentials or insufficient permissions.')
                
        elif user_type == 'trainer':
            trainer_id = request.POST.get('trainer_id')
            trainer_name = request.POST.get('trainer_name')
            password = request.POST.get('password')
            
            try:
                # Find instructor by ID and name
                instructor = Instructor.objects.get(instructor_id=trainer_id)
                if instructor.full_name.lower() == trainer_name.lower():
                    # Check if the instructor has an associated user
                    if instructor.user:
                        user = authenticate(request, username=instructor.user.username, password=password)
                        if user is not None:
                            login(request, user)
                            return redirect('instructors:dashboard')
                        else:
                            messages.error(request, 'Invalid password for trainer.')
                    else:
                        messages.error(request, 'Trainer account not properly configured.')
                else:
                    messages.error(request, 'Trainer name does not match.')
            except Instructor.DoesNotExist:
                messages.error(request, 'Trainer not found.')
                
        elif user_type == 'student':
            student_id = request.POST.get('student_id')
            student_name = request.POST.get('student_name')
            password = request.POST.get('password')
            
            try:
                # Find student by ID and name
                student = Student.objects.get(student_id=student_id)
                if student.full_name.lower() == student_name.lower():
                    # Check if the student has an associated user
                    if student.user:
                        user = authenticate(request, username=student.user.username, password=password)
                        if user is not None:
                            login(request, user)
                            return redirect('students:dashboard')
                        else:
                            messages.error(request, 'Invalid password for student.')
                    else:
                        messages.error(request, 'Student account not properly configured.')
                else:
                    messages.error(request, 'Student name does not match.')
            except Student.DoesNotExist:
                messages.error(request, 'Student not found.')
        
        return render(request, 'login.html')
    
    return render(request, 'login.html')


def custom_logout(request):
    logout(request)
    return redirect('login')
