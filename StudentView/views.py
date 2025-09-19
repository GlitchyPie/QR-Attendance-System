import datetime
import pytz
from QR_Attendance_System.core import *
from django.shortcuts import render
from FacultyView.models import Student, ClassName, Attendance
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.urls import reverse

#=======================

def student_view_name_entry(request, classId = None, className = None):
    cls = getClass(classId,className)
    if cls == None:
        return HttpResponseBadRequest()

    className = cls.s_className
    classId = cls.id  # pyright: ignore[reportAttributeAccessIssue]

    return render(request, 
                  "StudentView/StudentViewStudent_entry.html",
                  {
                      "classId":classId,
                      "className":className,
                      "class":cls,
                  })

#=======================

def student_view_submit_attendance(request,classId = None, className = None):
    if request.method != "POST" :
        return HttpResponseBadRequest() #This should only accept POST requests
    
    cls = getClass(classId,className)
    if cls == None:
        return HttpResponseBadRequest()

    className = cls.s_className
    classId = cls.id  # pyright: ignore[reportAttributeAccessIssue]

    eml = request.POST["student_email"].lower()
    fname = request.POST["student_fname"]
    lname = request.POST["student_lname"]

    classOb = ClassName.objects.filter(id=classId)[0]

    stuOb = Student.objects.get_or_create(s_eml=eml, s_fname=fname, s_lname=lname)[0]

    d = datetime.datetime.now(pytz.utc)
    eml = stuOb.s_eml
    fname = stuOb.s_fname
    lname = stuOb.s_lname
    
    attendanceQuery = Attendance.objects.filter(dte_date__date=d, student=eml, className=classId)
    if attendanceQuery.exists() == False:
        attendanceOb = Attendance(dte_date=d,className=classOb,student=stuOb)
        attendanceOb.save()
        return HttpResponseRedirect(reverse('student_view_attendance_submitted',kwargs={"classId":classId}))
    else:
        return HttpResponseRedirect(reverse('student_view_attendance_already_submitted',kwargs={"classId":classId}))

#=======================

def student_view_bigQRcode(request, classId = None, className = None, blockSize = 20):
    cls = getClass(classId,className)
    if cls == None:
        return HttpResponseBadRequest()

    className = cls.s_className
    classId = cls.id  # pyright: ignore[reportAttributeAccessIssue]

    qrSrc = qrgenerator(request, classId, blockSize)
    return render(request,
                  "StudentView/StudentViewQrCode.html",
                  {
                      "classId":classId,
                      "className":className,
                      "class":cls,
                      "qrSrc":qrSrc,
                  })

#=======================

def student_view_attendance_submitted(request, classId=None, className=None):
    cls = getClass(classId,className)
    if cls == None:
        className = None
        classId = None
    else:
        className = cls.s_className
        classId = cls.id  # pyright: ignore[reportAttributeAccessIssue]

    return render(request,
                  "StudentView/Submitted.html",
                  {
                      "classId":classId,
                      "className":className,
                      "class":cls,
                  })

def student_view_attendance_already_submitted(request, classId=None, className=None):
    cls = getClass(classId,className)
    if cls == None:
        className = None
        classId = None
    else:
        className = cls.s_className
        classId = cls.id  # pyright: ignore[reportAttributeAccessIssue]

    return render(request,
                  "StudentView/AlreadySubmitted.html",
                  {
                      "classId":classId,
                      "className":className,
                      "class":cls,
                  })
