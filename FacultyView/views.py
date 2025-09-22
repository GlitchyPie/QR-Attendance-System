import datetime
import pytz
import csv
from QR_Attendance_System.core import *
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.urls import reverse
from .models import Student, ClassName, Attendance, ModuleName

def attendance_query(cls : ClassName|None = None,
                     mod : ModuleName|None = None, 
                     classId : int|None = None, className : str|None = None, 
                     moduleId : int|None = None, moduleName : str|None = None, 
                     dte : datetime.datetime|None = None,
                     year : int|None = None,
                     month : int|None = None,
                     day : int|None = None):
    
    if((cls == None) and (mod == None)):
        cls,mod = getClassAndModule(classId, className, moduleId, moduleName)
    elif(cls):
        mod = mod or cls.moduleName

    D = dte or datetime.datetime.now(pytz.utc)
    year = year or D.year
    month = month or D.month
    day = day or D.day

    present = None
    if(cls):
        present = Attendance.objects.filter(className = cls.id) # pyright: ignore[reportAttributeAccessIssue]
    elif(mod):
        present = Attendance.objects.filter(className__moduleName = mod.id) # pyright: ignore[reportAttributeAccessIssue]
    else:
        present = Attendance.objects.all()

    present = present.filter(dte_date__year=year, dte_date__month=month,dte_date__day=day)

    return (present, cls, mod)
    
#=======================

def faculty_view_delete_attendance(request,
                                   classId : int|None = None,
                                   className : str|None = None):
    if request.method != 'POST' :
        return HttpResponseBadRequest() #This should only accept POST requests
    
    cls = getClass(classId,className)
    if cls == None:
        return HttpResponseBadRequest()
    
    #0 1 2 3 4 5 6 7 8 9
    #r e c o r d _ 1 2 3
    r = request.POST['attendance_record'][7:]

    attendanceQuery = Attendance.objects.filter(id=r)

    if attendanceQuery.exists():
        attendanceQuery[0].delete()

    return HttpResponseRedirect(reverse('faculty_view',kwargs={'classId':cls.id})) # pyright: ignore[reportAttributeAccessIssue]
    
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

    present,cls,mod = attendance_query(cls = cls)

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

def faculty_view_present_list(request, 
                              classId : int|None = None, className : str|None = None,
                              moduleId : int|None = None, moduleName : str|None = None,
                              year : int|None= None,
                              month : int|None = None,
                              day : int|None = None):
    
    present,cls,mod = attendance_query(classId=classId,
                                       className=className,
                                       moduleId=moduleId,
                                       moduleName=moduleName,
                                       year=year,
                                       month=month,
                                       day=day)
    
    return render(
        request,
        'FacultyView/StudentList.html',
        {
               'present' : present,
                 'class' : cls,
                'module' : mod,
              'dte_year' : year,
             'dte_month' : month,
               'dte_day' : day,
        },
    )

#=======================

def faculty_view_attendance_export(request,
                                   classId : int|None = None, className : str|None = None,
                                   moduleId : int|None = None, moduleName : str|None = None,
                                   action : str|None = 'view',
                                   year : int|None = None,
                                   month : int|None = None,
                                   day : int|None = None):
    
    D = datetime.datetime.now(pytz.utc)
    year = year or D.year
    month = month or D.month
    day = day or D.day    

    presentQuery,cls,mod = attendance_query(classId=classId, className=className,
                                            moduleId=moduleId, moduleName=moduleName,
                                            year=year, month=month, day=day)

    match action:
        case 'export':
            return render_faculty_view_attendance_export_CSV(request, presentQuery)
        case 'view':
            return render_faculty_view_attendance_export_form(request, cls, mod, presentQuery, year, month, day)
        case _:
            return HttpResponseBadRequest()

def render_faculty_view_attendance_export_form(request,
                                               cls : ClassName|None,
                                               mod : ModuleName|None,
                                               present,
                                               year : int|None,
                                               month : int|None,
                                               day : int|None):
    classes = ClassName.objects.all()
    modules = ModuleName.objects.all()
    return render(
        request,
        'FacultyView/FacultyViewExportForm.html',
        {
               'classes' : classes,
               'modules' : modules,
                 'class' : cls,
                'module' : mod,
               'present' : present,
              'dte_year' : year,
             'dte_month' : month,
               'dte_day' : day,
        },
    )

def render_faculty_view_attendance_export_CSV(request, present_query):
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

    return HttpResponseRedirect(reverse('faculty_view_class',kwargs={'classId':classOb.id})) # pyright: ignore[reportAttributeAccessIssue]

#=======================