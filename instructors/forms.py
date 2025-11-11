from django import forms
from .models import ScheduleEvent
from courses.models import Course
from students.models import Assignment
from datetime import datetime

class ScheduleEventForm(forms.ModelForm):
    class Meta:
        model = ScheduleEvent
        fields = ['course', 'title', 'description', 'event_type', 'start_time', 'end_time', 'location']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'end_time': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, instructor=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter courses to only those taught by this instructor
        if instructor:
            self.fields['course'].queryset = Course.objects.filter(instructor=instructor)
        
        # Set default times
        if not self.instance.pk:
            # For new events, set some default times
            pass


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['course', 'title', 'description', 'due_date', 'max_points']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'due_date': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'max_points': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def __init__(self, instructor=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter courses to only those taught by this instructor
        if instructor:
            self.fields['course'].queryset = Course.objects.filter(instructor=instructor)
        
        # Set default due date to 7 days from now
        if not self.instance.pk and 'due_date' in self.fields:
            # Set initial value for new assignments
            if not self.initial.get('due_date'):
                from datetime import datetime, timedelta
                default_due = datetime.now() + timedelta(days=7)
                self.fields['due_date'].initial = default_due.strftime('%Y-%m-%dT%H:%M')