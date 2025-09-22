import datetime
import pytz
from QR_Attendance_System.core import *
from django.shortcuts import render
from FacultyView.models import Student, ClassName, Attendance
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.urls import reverse
from urllib.parse import urlencode

#=======================

def student_view_name_entry(request, classId : int|None = None, className : str|None = None):
    cls,mod = getClassAndModule(classId,className)
    if cls == None:
        return HttpResponseBadRequest()
    
    return render(request, 
                  'StudentView/StudentViewStudent_entry.html',
                  {
                       'class' : cls,
                      'module' : mod,
                  })

#=======================

def student_view_submit_attendance(request, classId : int|None = None, className : str|None = None):
    if request.method != 'POST' :
        return HttpResponseBadRequest() #This should only accept POST requests
    
    classOb = getClass(classId,className)
    if classOb == None:
        return HttpResponseBadRequest()

    eml = request.POST['student_email'].lower()
    fname = request.POST['student_fname']
    lname = request.POST['student_lname']
    next = request.POST.get('next', None)

    stuOb = Student.objects.get_or_create(s_eml=eml, 
                                          defaults={'s_fname':fname, 
                                                    's_lname':lname
                                                    })[0]

    eml = stuOb.s_eml
    fname = stuOb.s_fname
    lname = stuOb.s_lname
    
    d = datetime.datetime.now(pytz.utc)
    created = Attendance.objects.get_or_create(dte_date__date=d,
                                               student=stuOb,
                                               className=classOb,
                                               defaults={'dte_date':d})[1]
    
    path = ''
    if created:
        path = reverse('student_view_attendance_submitted',kwargs={'classId':classOb.id}) # type: ignore
    else:
        path = reverse('student_view_attendance_already_submitted',kwargs={'classId':classOb.id}) # type: ignore

    if next:
        path += '?'
        path += urlencode({'next':next})
    
    return HttpResponseRedirect(path)

#=======================

def student_view_bigQRcode(request,
                           classId : int|None = None, className : str|None = None, 
                           blockSize : int = 20):
    cls,mod = getClassAndModule(classId,className)
    if cls == None:
        return HttpResponseBadRequest()

    qrSrc = qrgenerator(request, classId, blockSize) # type: ignore
    return render(request,
                  'StudentView/StudentViewQrCode.html',
                  {
                       'class' : cls,
                      'module' : mod,
                       'qrSrc' : qrSrc,
                  })

#=======================

def student_view_attendance_submitted(request,
                                      classId : int|None = None, className : str|None = None):
    cls,mod = getClassAndModule(classId,className)
    return render(request,
                  'StudentView/Submitted.html',
                  {
                       'class' : cls,
                      'module' : mod,
                  })

