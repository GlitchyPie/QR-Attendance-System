import datetime
import pytz
import json
from io import StringIO
from QR_Attendance_System.core import *
from django.shortcuts import render
from FacultyView.models import Student, ClassName, Attendance
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseBadRequest
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
    
    D = datetime.datetime.now(pytz.utc)
    created = Attendance.objects.get_or_create(dte_date__date=D,
                                               student=stuOb,
                                               className=classOb,
                                               defaults={'dte_date':D})[1]
    
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

#=======================

def student_is_present(student : Student, cls : ClassName, year : int, month : int, day : int):
    return Attendance.objects.filter(dte_date__year = year,
                                     dte_date__month = month,
                                     dte_date__day = day,
                                     className = cls,
                                     student = student).exists()

def student_view_student_lookup(request):
    if request.method != 'POST' :
        return HttpResponseBadRequest() #This should only accept POST requests
    
    stu = None
    eml :str = request.POST['student_email']

    cls = None
    classId : int = int(request.POST.get('classId', -1))
    if(classId > 0):
        cls = getClass(classId = classId,
                       className = None)

    q = Student.objects.filter(s_eml__iexact=eml.lower())
    if len(q) > 0:
        stu = q[0]
    
    j = {'student' : {}}
    if(stu):
        isPresent = False
        if(cls):
            D = datetime.datetime.now(pytz.utc)
            year = request.POST.get('year', None) or D.year
            month = request.POST.get('month', None) or D.month
            day = request.POST.get('day', None) or D.day 
            isPresent = student_is_present(stu,cls,year,month,day) 

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
    