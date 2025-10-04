import datetime
import pytz
import csv
import json
import hashlib
import xlsxwriter

from QR_Attendance_System.core import *
from .DRF_Serializers import AttendanceSerializer
from .models import Student, ClassName, Attendance, ModuleName

from typing import Any
from io import BytesIO
from itertools import groupby

from django.shortcuts import render
from django.utils.http import parse_http_date, http_date
from django.http import HttpResponse, FileResponse, HttpResponseRedirect
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.http import HttpResponseNotModified, JsonResponse
from django.urls import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_POST
from django.conf import settings


#=======================

@require_POST
@permission_required('FacultyView.delete_attendance', raise_exception=True)
def faculty_view_delete_attendance(request):
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

@login_required
def faculty_view(request,
                 classId : int|None = None, className : str|None = None,
                 moduleId : int|None =None, moduleName : str|None =None):
    
    request.session.set_expiry(settings.SESSION_COOKIE_AGE)

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
@login_required
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

@login_required
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


    #Query our attendance register...
    query,cls,mod = attendance_query(classId=classId, className=className,
                                            moduleId=moduleId, moduleName=moduleName,
                                            year=year, month=month, day=day,
                                            year_start=year_start,month_start=month_start,day_start=day_start,
                                            year_end=year_end,month_end=month_end,day_end=day_end)
    
    #Most recently modified
    state_last_attendance_modified = STATE.get_attendance_modified()

    #If we have a class or a module specified we can use the more specific update time
    if(cls):
        state_last_attendance_modified = STATE.get_attendance_modified_class(cls)
    elif(mod):
        state_last_attendance_modified = STATE.get_attendance_modified_module(mod)

    #Compare our last modified date to that provided by the server
    last_modified = request.META.get('HTTP_IF_MODIFIED_SINCE', None)
    if(last_modified):
        ts = parse_http_date(last_modified)
        dt = datetime.datetime.fromtimestamp(ts,tz=pytz.utc)
        if state_last_attendance_modified < dt:
            return HttpResponseNotModified()

    #Generate a json representation of the query and generate a hash
    vals = list(query.values())
    str_json = json.dumps(vals, cls=DjangoJSONEncoder).encode()
    etag = hashlib.md5(str_json, usedforsecurity=False).hexdigest()
    
    #Compare that hash to the etag provided by the server
    if_none_match = request.META.get("HTTP_IF_NONE_MATCH")
    if if_none_match == etag:
        return HttpResponseNotModified()


    #Should we generate a view with date and clas headers
    #Usually true for the attendance view, false for the class view
    with_date_headers = (str(request.GET.get('with_date_headers', 'true')).lower() == "true")
    with_class_headers = (str(request.GET.get('with_class_headers', 'true')).lower() == "true")

    context : dict[str, Any]= {
               'present' : query,
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
        case 'view': #view the attendance list next to the export form
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)

            #Force the with_date_headers to true for this view...
            context['with_date_headers'] = True
            context['with_class_headers'] = True
            response = render_attendance_template_with_context(request,
                                                                       'FacultyView/view/ExportForm.html',
                                                                       context)
            
            
        case 'view-table': #A plain HTML table view
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)

            response = render_attendance_template_with_context(request,
                                                                       'FacultyView/view/AttendanceTable.html',
                                                                       context)
        
        case 'list-html': #Just the <ul> list - used for AJAX polling
            response = render_attendance_template_with_context(request,
                                                                       'FacultyView/part/AttendanceList.html',
                                                                       context)
            
        case 'export-csv': #Export as a CSV
            response = render_attendance_query_csv(request, query)
        
        case 'export-xlsx': #Export as an Excel workbook
            response = render_attendance_query_xlsx(request, query)

        case 'export-json': #Export as json
            response = render_attendance_query_json(request, query)

        case _:
            response = HttpResponseNotFound()

    response['cache-control'] = 'max-age=2, must-revalidate'
    response['Last-Modified'] = http_date(state_last_attendance_modified.timestamp())
    response['ETag'] = etag
    return response

def render_attendance_template_with_context(request,
                                            templateName : str, 
                                            context : dict[str, Any]):
    context['classes'] = ClassName.objects.all()
    context['modules'] = ModuleName.objects.all()

    return render(request, templateName, context)

def render_attendance_query_csv(request, attendance_query):
    response = HttpResponse (content_type='text/csv')
    csvWriter = csv.writer(response)

    csvWriter.writerow([
        'Student Email',
        'First Name',
        'Last Name',
        'Module',
        'Class',
        'Date / Time (ISO)',
        'Module ID',
        'Class ID',
    ])
    for entry in attendance_query:
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

    fn = request.GET.get('file_name',None) or "Attendance Report.csv"
    response["Content-Disposition"] = f"attachment; filename=\"{fn}\""
    return response

def render_attendance_query_xlsx(request, attendance_query):
    headers = [
        'Student Email',
        'First Name',
        'Last Name',
        'Module',
        'Class',
        'Date / Time (ISO)',
        'Time (Local)',
        'Module ID',
        'Class ID',
    ]

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output,{'use_future_functions':False})

    fmt1 = workbook.add_format()
    fmt1.set_num_format('hh:mm')
    
    for k, grp in groupby(attendance_query, key=lambda d: d.dte_date.date()):
        worksheet = workbook.add_worksheet(k.isoformat())
        worksheet.write_row(0,0,headers)
        r = 1
        for entry in grp:
            entry_posix = entry.dte_date.timestamp()
            excel_serial = (entry_posix / 86400) + 25569
            worksheet.write_row(r,0,[
                entry.student.s_eml, #0
                entry.student.s_fname, #1
                entry.student.s_lname, #2
                entry.className.moduleName.s_moduleName, #3
                entry.className.s_className, #4
                entry.dte_date.isoformat(), #5
                0, #6
                entry.className.moduleName.id, #7
                entry.className.id,#8
            ])
            formula = (
                        "=_xlfn.LET("
                       f"_xlpm.α,{excel_serial},"
                        "_xlpm.φ, WORKDAY.INTL(DATE(YEAR(_xlpm.α),4,1),-1,\"1111110\"),"
                        "_xlpm.ε, WORKDAY.INTL(DATE(YEAR(_xlpm.α),11,1),-1,\"1111110\"),"
                        "_xlpm.α+((_xlpm.α>=_xlpm.φ+1/24)*(_xlpm.α<_xlpm.ε+1/24))/24"
                        ")"
                       )
            worksheet.write_formula(r, 6, formula, fmt1)
            r+=1

    workbook.close()

    output.seek(0)
    fn = request.GET.get('file_name',None) or "Attendance Report.xlsx"
    response = FileResponse(output, as_attachment=True, 
                            filename=fn,
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                            )

    return response

def render_attendance_query_json(request, attendance_query):
    fn = request.GET.get('file_name',None) or "Attendance Report.json"
    serializer = AttendanceSerializer(attendance_query, many=True)
    response = JsonResponse(serializer.data, safe=False)
    response["Content-Disposition"] = f"attachment; filename=\"{fn}\""
    return response
#=======================

@require_POST
@login_required
def faculty_view_create_class(request):
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