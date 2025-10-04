from django import template
from django.conf import settings
from django.urls import resolve
from QR_Attendance_System.core import getClassAndModule
from TemplateTags.templatetags import export_date_type

register = template.Library()

@register.simple_tag(takes_context=True)
def default_page_title(context,userTitle : str|None = None):
    ttle0 = ''
    ttle1 = ''
    ttle2 = ''
    ttle3 = ''

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
        case 'student_view_registration_form':
            ttle0 = "Student Registration"
        case 'student_view_attendance_submitted':
            ttle0 = "Registration Submitted"
        case 'student_view_attendance_already_submitted':
            ttle0 = "Registration Already Submitted"
        case 'login':
            ttle0 = "Faculty Login"

        case '_':
            ttle0 = ""

    if cls != None:
        ttle1 = cls.__str__()
    elif mod != None:
        ttle1 = mod.__str__()

    ttle2 = userTitle or settings.COPYRIGHT_APP_NAME

    isstd = export_date_type.export_date_type(context)
    match isstd:
        case 1:
            ttle3 = f"{context.get('dte_year')}-{context.get('dte_month')}-{context.get('dte_day')}"
        case 2:
            A = f"{context.get('dte_start_year', "####") or "####"}-{context.get('dte_start_month', "##") or "##"}-{context.get('dte_start_day',"##") or "##"}"
            B = f"{context.get('dte_end_year', "####") or "####"}-{context.get('dte_end_month', "##") or "##"}-{context.get('dte_end_day',"##") or "##"}"
            ttle3 = f"{A} <> {B}"
        case 3:
            ttle3 = f"{context.get('dte_year', "####") or "####"}-{context.get('dte_month', "##") or "##"}-{context.get('dte_day',"##") or "##"}"
        case _:
            pass
    #--

    #=====
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

    if ttle != "":
        if ttle3 != "####-##-##":
            ttle += " [" + ttle3 + "]"
    else:
        ttle += ttle3

    return ttle
    
