from django import template
from django.conf import settings
from django.urls import resolve
from QR_Attendance_System.core import getClassAndModule

register = template.Library()

@register.simple_tag(takes_context=True)
def default_page_title(context):
    ttle0 = ''
    ttle1 = ''
    ttle2 = ''

    r : str = context['request'].path
    m = resolve(r)

    cls,mod = getClassAndModule(context.get('classId', None), context.get('className', None),
                                context.get('moduleId', None), context.get('moduleName', None),
                                context.get('class', None), context.get('module', None))

    match m.url_name:
        case 'faculty_view_attendance':
            ttle0 = "Attendance History"
        case 'faculty_view':
            ttle0 = "Attendance Register"

            if r.startswith("/module"):
                ttle0 += " - Class index"
            elif r.startswith("/class") == False:
                ttle0 += " - Module Index"
        case 'student_view_enter_student':
            ttle0 = "Student Registration"
        case 'student_view_attendance_submitted':
            ttle0 = "Registration Submitted"
        case 'student_view_attendance_already_submitted':
            ttle0 = "Registration Already Submitted"

        #For completeness, but I don't think these will ever be used.
        case 'faculty_view_create_class':
            ttle0 = "Create class"
        case 'faculty_view_delete_attendance':
            ttle0 = "Delete Attendance Record"
        case 'faculty_view_present_list':
            ttle0 = "AJAX - Present List"
        case '_':
            ttle0 = ""

    if cls != None:
        ttle1 = cls.__str__()
    elif mod != None:
        ttle1 = mod.__str__()

    ttle2 = settings.COPYRIGHT_APP_NAME

    ttle = ttle0
    
    if ttle != "":
        if ttle1 != "":
            ttle += " - " + ttle1
    else:
        ttle += ttle1

    if ttle != "":
        if ttle2 != "":
            ttle += " - " + ttle2
    else:
        ttle += ttle2

    return ttle
    
