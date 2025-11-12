from django import forms
from .models import Attendance, TrainerAttendance
from courses.models import Course
from instructors.models import Instructor


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'course', 'session_date', 'status', 'notes']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'session_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        
        if course:
            # Filter students to only those enrolled in this course
            self.fields['student'].queryset = course.enrollments.filter(
                completion_status__in=['enrolled', 'in_progress']
            ).select_related('student').values_list('student', flat=True)
            self.fields['course'].initial = course
            self.fields['course'].widget = forms.HiddenInput()


class BulkAttendanceForm(forms.Form):
    session_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        
        if course:
            # Add a field for each student enrolled in the course
            enrollments = course.enrollments.filter(
                completion_status__in=['enrolled', 'in_progress']
            ).select_related('student')
            
            for enrollment in enrollments:
                self.fields[f'status_{enrollment.student.id}'] = forms.ChoiceField(
                    choices=[('present', 'Present'), ('absent', 'Absent'), ('late', 'Late'), ('excused', 'Excused')],
                    widget=forms.Select(attrs={'class': 'form-control'}),
                    initial='present'
                )


class TrainerAttendanceForm(forms.ModelForm):
    class Meta:
        model = TrainerAttendance
        fields = ['trainer', 'course', 'session_date', 'status', 'notes']
        widgets = {
            'trainer': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'session_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter courses to only those with active instructors
        self.fields['course'].queryset = Course.objects.filter(
            instructor__is_active=True
        )