import datetime
from typing import Any
import pytz
import csv
import json
import hashlib
from enum import Enum
from QR_Attendance_System.core import *
from django.shortcuts import render
from django.utils.http import parse_http_date, http_date
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotFound
from django.http import HttpResponseNotModified
from django.urls import reverse
from django.core.serializers.json import DjangoJSONEncoder
from .models import Student, ClassName, Attendance, ModuleName

#=======================

def faculty_view_delete_attendance(request):
    if request.method != 'POST' :
        return HttpResponseBadRequest() #This should only accept POST requests
    
    r = request.POST['attendance_record']

    attendanceOb = Attendance.objects.filter(id=r).first()

    cls = None
    if attendanceOb:
        cls = attendanceOb.className
        attendanceOb.delete()
        return HttpResponseRedirect(reverse('faculty_view',kwargs={'classId':cls.id})) # pyright: ignore[reportAttributeAccessIssue]
    else:
        return HttpResponseNotFound()
        
#=======================

def faculty_view(request,
                 classId : int|None = None, className : str|None = None,
                 moduleId : int|None =None, moduleName : str|None =None):
    
    cls,mod = getClassAndModule(classId, className,
                                moduleId, moduleName)
    
    if cls != None:
        return render_faculty_view_class(request,cls)
    elif mod != None:
        return render_faculty_view_class_index(request, mod)
    else:
        return render_faculty_view_module_index(request)

def render_faculty_view_module_index(request):
    modules = ModuleName.objects.all()
    return render(
        request,
        'FacultyView/view/Index.html',
        {
            'modules' : modules
        },
    )

def render_faculty_view_class_index(request, module : ModuleName|None):
    if module == None:
        return HttpResponseBadRequest()

    classes = ClassName.objects.filter(moduleName=module.id) # type: ignore
    return render(
        request,
        'FacultyView/view/Index.html',
        {
            'classes' : classes,
            'module' : module,
        },
    )

def render_faculty_view_class(request, cls : ClassName|None):
    if cls == None:
        return HttpResponseBadRequest()
    
    qrSrc = qrgenerator(request,cls.id) # pyright: ignore[reportAttributeAccessIssue]

    present,cls,mod = attendance_query(cls = cls, 
                                       dte=datetime.datetime.now(pytz.utc))

    return render(
        request,
        'FacultyView/view/Class.html',
        {
              'present' : present,
                'class' : cls,
               'module' : mod,
                'qrSrc' : qrSrc,
        },
    )

#=======================
def faculty_view_attendance_view_today(request,
                                       classId : int|None = None, className : str|None = None,
                                       moduleId : int|None = None, moduleName : str|None = None,
                                       action : str|None = 'view',):
    
    D = datetime.datetime.now(pytz.utc)
    y = D.year
    m = D.month
    d = D.day
    return faculty_view_attendance_view(request,
                                        classId, className,
                                        moduleId, moduleName,
                                        action,
                                        y, m, d)

def faculty_view_attendance_view(request,
                                 classId : int|None = None, className : str|None = None,
                                 moduleId : int|None = None, moduleName : str|None = None,
                                 action : str|None = 'view',
                                 year : int|None = None,
                                 month : int|None = None,
                                 day : int|None = None,
                                 year_start : int|None = None,
                                 month_start : int|None = None,
                                 day_start : int|None = None,
                                 year_end : int|None = None,
                                 month_end : int|None = None,
                                 day_end : int|None = None):

    presentQuery,cls,mod = attendance_query(classId=classId, className=className,
                                            moduleId=moduleId, moduleName=moduleName,
                                            year=year, month=month, day=day,
                                            year_start=year_start,month_start=month_start,day_start=day_start,
                                            year_end=year_end,month_end=month_end,day_end=day_end)
    
    state_last_attendance_modified = STATE.get_attendance_modified()
    if(cls):
        state_last_attendance_modified = STATE.get_attendance_modified_class(cls)
    elif(mod):
        state_last_attendance_modified = STATE.get_attendance_modified_module(mod)

    last_modified = request.META.get('HTTP_IF_MODIFIED_SINCE', None)
    if(last_modified):
        ts = parse_http_date(last_modified)
        dt = datetime.datetime.fromtimestamp(ts,tz=pytz.utc)
        if state_last_attendance_modified < dt:
            return HttpResponseNotModified()

    vals = list(presentQuery.values())
    j = json.dumps(vals, cls=DjangoJSONEncoder).encode()
    etag = hashlib.md5(j, usedforsecurity=False).hexdigest()
    
    if_none_match = request.META.get("HTTP_IF_NONE_MATCH")
    if if_none_match == etag:
        return HttpResponseNotModified()

    one_date_only = (year and month and day)

    with_date_headers = (str(request.GET.get('with_date_headers', 'true')).lower() == "true")
    with_class_headers = (str(request.GET.get('with_class_headers', 'true')).lower() == "true")

    context : dict[str, Any]= {
               'present' : presentQuery,
                 'class' : cls,
                'module' : mod,

              'dte_year' : year,
             'dte_month' : month,
               'dte_day' : day,

        'dte_start_year' : year_start,
       'dte_start_month' : month_start,
         'dte_start_day' : day_start,

          'dte_end_year' : year_end,
         'dte_end_month' : month_end,
           'dte_end_day' : day_end,

     'with_date_headers' : with_date_headers,
    'with_class_headers' : with_class_headers,
    }

    response = None
    match action:
        case 'view':
            #Force the with_date_headers to true for this view...
            context['with_date_headers'] = True
            context['with_class_headers'] = True
            response = render_faculty_view_attendance_related_template(request,
                                                                       'FacultyView/view/ExportForm.html',
                                                                       context)
        case 'view-table':
            response = render_faculty_view_attendance_related_template(request,
                                                                       'FacultyView/views/AttendanceTable.html',
                                                                       context)
        
        case 'list-html':
            response = render_faculty_view_attendance_related_template(request,
                                                                       'FacultyView/part/AttendanceList.html',
                                                                       context)
        case 'export-csv':
            response = render_faculty_view_attendance_view_CSV(request, presentQuery)
        
        case 'export-json':
            response = HttpResponseNotFound()
        
        case _:
            response = HttpResponseBadRequest()

    response['Last-Modified'] = http_date(state_last_attendance_modified.timestamp())
    response['ETag'] = etag
    return response

def render_faculty_view_attendance_related_template(request,
                                                    templateName : str, 
                                                    context : dict[str, Any]):

    context['classes'] = ClassName.objects.all()
    context['modules'] = ModuleName.objects.all()

    return render(request, templateName, context)

def render_faculty_view_attendance_view_CSV(request, present_query):
    response = HttpResponse (content_type='text/csv')
    csvWriter = csv.writer(response)

    csvWriter.writerow([
        'Student Email',
        'First Name',
        'Last Name',
        'Module',
        'Class',
        'Date / Time',
        'Module ID',
        'Class ID',
    ])
    for entry in present_query:
        csvWriter.writerow([
            entry.student.s_eml,
            entry.student.s_fname,
            entry.student.s_lname,
            entry.className.moduleName.s_moduleName,
            entry.className.s_className,
            entry.dte_date,
            entry.className.moduleName.id,
            entry.className.id,
        ])

    return response

#=======================

def faculty_view_create_class(request):
    if request.method != 'POST' :
        return HttpResponseBadRequest() #This should only accept POST requests
    
    className = request.POST['class_name']
    moduleName = request.POST['module_name']
    moduleId = request.POST.get('module_id',None)
    
    if moduleId == '':
        moduleOb = ModuleName.objects.get_or_create(s_moduleName__iexact=moduleName,
                                                    defaults={'s_moduleName':moduleName})[0]
    else:
        moduleOb = ModuleName.objects.filter(id=moduleId).first()

    classOb = ClassName.objects.get_or_create(s_className__iexact=className, moduleName=moduleOb,
                                              defaults={'s_className':className})[0]

    return HttpResponseRedirect(reverse('faculty_view',kwargs={'classId':classOb.id})) # pyright: ignore[reportAttributeAccessIssue]

#=======================