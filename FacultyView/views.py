import datetime
from typing import Any
import pytz
import csv
import json
import hashlib
from enum import Enum
from QR_Attendance_System.core import *
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotFound
from django.http import HttpResponseNotModified
from django.urls import reverse
from django.core.serializers.json import DjangoJSONEncoder
from .models import Student, ClassName, Attendance, ModuleName

def attendance_query(cls : ClassName|None = None,
                     mod : ModuleName|None = None, 
                     classId : int|None = None, className : str|None = None, 
                     moduleId : int|None = None, moduleName : str|None = None, 
                     dte : datetime.datetime|None = None,
                     year : int|None = None,
                     month : int|None = None,
                     day : int|None = None,
                     dte_start : datetime.datetime|None = None, dte_end : datetime.datetime|None = None,
                     year_start : int|None = None,
                     month_start : int|None = None,
                     day_start : int|None = None,
                     year_end : int|None = None,
                     month_end : int|None = None,
                     day_end : int|None = None,):

    if((cls == None) and (mod == None)):
        cls,mod = getClassAndModule(classId, className, moduleId, moduleName)
    elif(cls):
        mod = mod or cls.moduleName

    present = Attendance.objects.all()
    if(cls):
        present = present.filter(className = cls) # pyright: ignore[reportAttributeAccessIssue]
    elif(mod):
        present = present.filter(className__moduleName = mod) # pyright: ignore[reportAttributeAccessIssue]

    if dte:
        year = dte.year
        month = dte.month
        day = dte.day

    if dte_start:
        year_start = dte_start.year
        month_start = dte_start.month
        day_end = dte_start.day
    
    if dte_end:
        year_end = dte_end.year
        month_end = dte_end.month
        day_end = dte_end.day
    
    if((year_start or month_start or day_start) or (year_end or month_end or day_end)):
        if(year_start):
            present = present.filter(dte_date__year__gte=year_start)
        
        if(month_start):
            present = present.filter(dte_date__month__gte=month_start)

        if(day_start):
            present = present.filter(dte_date__day__gte=day_start)
        
        if(year_end):
            present = present.filter(dte_date__year__lte=year_end)
        
        if(month_end):
            present = present.filter(dte_date__month__lte=month_end)

        if(day_end):
            present = present.filter(dte_date__day__lte=day_end)

    else:
        if(year):
            present = present.filter(dte_date__year=year)

        if(month):
            present = present.filter(dte_date__month=month)

        if(day):
            present = present.filter(dte_date__day=day)

    #--------

    return (present, cls, mod)
    
#=======================

def faculty_view_delete_attendance(request):
    if request.method != 'POST' :
        return HttpResponseBadRequest() #This should only accept POST requests
    
    r = request.POST['attendance_record']

    attendanceQuery = Attendance.objects.filter(id=r)

    cls = None
    if attendanceQuery.exists():
        attendanceOb = attendanceQuery[0]
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
        'FacultyView/FacultyViewIndex.html',
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
        'FacultyView/FacultyViewIndex.html',
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
        'FacultyView/FacultyViewClass.html',
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
    
    vals = list(presentQuery.values())
    j = json.dumps(vals, cls=DjangoJSONEncoder).encode()
    etag = hashlib.md5(j, usedforsecurity=False).hexdigest()
    
    if_none_match = request.META.get("HTTP_IF_NONE_MATCH")
    if if_none_match == etag:
        return HttpResponseNotModified()

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
    }

    response = None
    match action:
        case 'view':
            response = render_faculty_view_attendance_related_template(request,
                                                                       'FacultyView/FacultyViewExportForm.html',
                                                                       context)
        case 'view-table':
            response = HttpResponseNotFound()
        
        case 'list-html':
            response = render_faculty_view_attendance_related_template(request,
                                                                       'FacultyView/AttendanceList.html',
                                                                       context)
        case 'export-csv':
            response = render_faculty_view_attendance_view_CSV(request, presentQuery)
        
        case 'export-json':
            response = HttpResponseNotFound()
        
        case _:
            response = HttpResponseBadRequest()

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
    
    moduleOb = ModuleName.objects.get_or_create(s_moduleName__iexact=moduleName,
                                                defaults={'s_moduleName':moduleName})[0]
    classOb = ClassName.objects.get_or_create(s_className__iexact=className, moduleName=moduleOb,
                                              defaults={'s_className':className})[0]

    return HttpResponseRedirect(reverse('faculty_view',kwargs={'classId':classOb.id})) # pyright: ignore[reportAttributeAccessIssue]

#=======================