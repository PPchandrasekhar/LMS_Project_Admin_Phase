from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Course(models.Model):
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    instructor = models.ForeignKey('instructors.Instructor', on_delete=models.CASCADE, related_name='courses')
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta:
        ordering = ['order']


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField()
    duration = models.DurationField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.module.title} - {self.title}"

    class Meta:
        ordering = ['order']


class Material(models.Model):
    MATERIAL_TYPES = [
        ('pdf', 'PDF Document'),
        ('doc', 'Word Document'),
        ('ppt', 'PowerPoint Presentation'),
        ('xls', 'Excel Spreadsheet'),
        ('txt', 'Text File'),
        ('zip', 'Zip Archive'),
        ('other', 'Other File'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='course_materials/')
    material_type = models.CharField(max_length=10, choices=MATERIAL_TYPES, default='pdf')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='materials', null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    download_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def file_extension(self):
        if self.file:
            return self.file.name.split('.')[-1].upper()
        return 'N/A'

    @property
    def file_size(self):
        if self.file:
            size = self.file.size
            if size < 1024:
                return f"{size} bytes"
            elif size < 1024 * 1024:
                return f"{size // 1024} KB"
            else:
                return f"{size // (1024 * 1024)} MB"
        return 'N/A'


class Video(models.Model):
    VIDEO_TYPES = [
        ('mp4', 'MP4 Video'),
        ('avi', 'AVI Video'),
        ('mov', 'MOV Video'),
        ('wmv', 'WMV Video'),
        ('flv', 'FLV Video'),
        ('webm', 'WebM Video'),
        ('other', 'Other Video'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to='course_videos/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    video_type = models.CharField(max_length=10, choices=VIDEO_TYPES, default='mp4')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='videos', null=True, blank=True)
    duration = models.DurationField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='video_thumbnails/', blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    view_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def file_extension(self):
        if self.video_file:
            return self.video_file.name.split('.')[-1].upper()
        return 'N/A'

    @property
    def file_size(self):
        if self.video_file:
            size = self.video_file.size
            if size < 1024:
                return f"{size} bytes"
            elif size < 1024 * 1024:
                return f"{size // 1024} KB"
            else:
                return f"{size // (1024 * 1024)} MB"
        return 'N/A'

    def get_video_source(self):
        """Return either the uploaded file URL or the external URL"""
        if self.video_file:
            return self.video_file.url
        elif self.video_url:
            return self.video_url
        return None
