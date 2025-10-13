import datetime
import pytz

from os.path import getmtime as getfilemtime

from QR_Attendance_System.core import *
from FacultyView.models import Student, ClassName, Attendance

from urllib.parse import urlencode

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseNotModified
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.http import parse_http_date, http_date

#=======================

def student_view_registration_form(request, classId : int|None = None, className : str|None = None):
    cls,mod = getClassAndModule(classId,className)
    if cls == None:
        return HttpResponseBadRequest()
    
    return render(request, 
                  'StudentView/view/RegistrationForm.html',
                  {
                       'class' : cls,
                      'module' : mod,
                  })

#=======================
@require_POST
def submit_attendance(request, classId : int|None = None, className : str|None = None):
    classOb = getClass(classId,className)
    if classOb == None:
        raise ValueError("No class specified")
    
    STATE.set_attendance_modified_class(classOb)

    eml = request.POST['student_email'].lower()
    fname = request.POST['student_fname']
    lname = request.POST['student_lname']

    stuOb = Student.objects.get_or_create(s_eml=eml, 
                                          defaults={'s_fname':fname, 
                                                    's_lname':lname
                                                    })[0]
    
    eml = stuOb.s_eml
    fname = stuOb.s_fname
    lname = stuOb.s_lname
    
    D = datetime.datetime.now(pytz.utc)
    return Attendance.objects.get_or_create(dte_date__date=D,
                                            student=stuOb,
                                            className=classOb,
                                            defaults={'dte_date':D})
    
def student_view_submit_attendance_ajax(request, classId : int|None = None, className : str|None = None):
    created = False
    error = False
    validationError = False
    try:
        created = submit_attendance(request, classId, className)[1]
    except ValidationError:
        error = True
        validationError = True
    except:
        error = True
        pass

    return JsonResponse({'created':created, "error":error, "validationError":validationError})

def student_view_submit_attendance(request, classId : int|None = None, className : str|None = None):
    created,attendanceOb = submit_attendance(request, classId, className)

    path = ''
    if created:
        path = reverse('student_view_attendance_submitted',kwargs={'classId':attendanceOb.className.id}) # type: ignore
    else:
        path = reverse('student_view_attendance_already_submitted',kwargs={'classId':attendanceOb.className.id}) # type: ignore

    next = request.POST.get('next', None)
    if next:
        path += '?'
        path += urlencode({'next':next})
    
    return HttpResponseRedirect(path)

#=======================

def student_view_print_qrCode(request,
                              classId : int|None = None,
                              boxSize : int|None = None):
    cls,mod = getClassAndModule(classId, None)
    if cls == None:
        return HttpResponseBadRequest()

    return render(request,
                  'StudentView/view/Print_qrCode.html',
                  {
                       'class' : cls,
                      'module' : mod,
                     'boxSize' : boxSize,
                  })

def student_view_qrCode_image(request, classId : int, boxSize : int = 20, extension : str = ''):
    response = None
    try:
        remotePath, localPath = qrgenerator(request, classId, boxSize, extension)
        mtimestamp = getfilemtime(localPath)
        file_last_modified = datetime.datetime.fromtimestamp(mtimestamp, pytz.utc)

        #Compare our last modified date to that provided by the server
        last_modified = request.META.get('HTTP_IF_MODIFIED_SINCE', None)
        if(last_modified):
            ts = parse_http_date(last_modified)
            dt = datetime.datetime.fromtimestamp(ts,tz=pytz.utc)
            if file_last_modified < dt:
                return HttpResponseNotModified()

        response = HttpResponseRedirect(remotePath)
        response['Last-Modified'] = http_date(mtimestamp)
        response['cache-control'] = 'max-age=604800, immutable, public, stale-while-revalidate=604800, stale-if-error'
    except RequestedContentTypeNotFound as e:
        response = HttpResponseNotFound(str(e))

    except NoAcceptableContentType as e:
        response = HttpResponse(str(e), status=406)
    
    return response

#=======================

def student_view_attendance_submitted(request,
                                      classId : int|None = None, className : str|None = None):
    cls,mod = getClassAndModule(classId,className)
    return render(request,
                  'StudentView/view/AttendanceSubmitted.html',
                  {
                       'class' : cls,
                      'module' : mod,
                  })

#=======================

def student_is_present(student : Student, cls : ClassName, year : int, month : int, day : int):
    return attendance_query(cls=cls, year=year, month=month, day=day, student=student)[0].exists()

@require_POST
def student_view_student_lookup(request):
    stu = None
    eml :str = request.POST['student_email']

    cls = None
    classId : int = int(request.POST.get('classId', -1))
    if(classId > 0):
        cls = getClass(classId = classId,
                       className = None)

    stu = Student.objects.filter(s_eml__iexact=eml.lower()).first()
    
    j = {'student' : {}}
    if(stu):
        isPresent = False
        if(cls):
            D = datetime.datetime.now(pytz.utc)
            year = request.POST.get('year', None) or D.year
            month = request.POST.get('month', None) or D.month
            day = request.POST.get('day', None) or D.day 
            isPresent = student_is_present(stu, cls, year, month, day)

        j['student'] = {
            'found' : True,
              'eml' : stu.s_eml,
            'fname' : stu.s_fname,
            'lname' : stu.s_lname,
            'isPresent' : isPresent,
        }
    else:
        j['student'] = {
            'found': False,
        }

    return JsonResponse(j)
    