from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using the key"""
    return dictionary.get(key)

@register.filter
def get_status(attendance):
    """Get the status from an attendance object"""
    return attendance.status

@register.filter
def get_attendance_status(attendances, student_id):
    """Get the attendance status for a specific student"""
    if not attendances:
        return ''
    
    for attendance in attendances:
        if attendance.student.id == student_id:
            return attendance.status
    
    return ''