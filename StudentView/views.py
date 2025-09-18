import datetime
import pytz
from django.shortcuts import render
from FacultyView.models import Student, ClassName, Attendance
from FacultyView.views import qrgenerator
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.urls import reverse

#=======================

def student_view_name_entry(request, classId = None, className = None):
    if((classId == None) and (className == None)):
        return HttpResponseBadRequest()
    elif(classId == None):
        classId = ClassName.objects.filter(s_className__iexact=className)[0].id # pyright: ignore[reportAttributeAccessIssue]
    else:
        className = ClassName.objects.filter(id=classId)[0].s_className

    return render(request, 
                  "StudentView/StudentViewStudent_entry.html",
                  {
                      "classId":classId,
                      "className":className,
                  })
#=======================

def student_view_submit_attendance(request,classId = None, className = None):
    if request.method == "GET" :
        return HttpResponseBadRequest() #This should only accept POST requests
    
    if((classId == None) and (className == None)):
        return HttpResponseBadRequest()
    elif(classId == None):
        classId = ClassName.objects.filter(s_className__iexact=className)[0].id # pyright: ignore[reportAttributeAccessIssue]
    else:
        className = ClassName.objects.filter(id=classId)[0].s_className


    eml = request.POST["student_email"].lower()
    fname = request.POST["student_fname"]
    lname = request.POST["student_lname"]

    classOb = ClassName.objects.filter(id=classId)[0]

    stuQuery = Student.objects.filter(s_eml=eml)
    stuOb = None
    if len(stuQuery) == 0:
        stuOb = Student(s_eml=eml,s_fname=fname,s_lname=lname)
        stuOb.save()
    else:
        stuOb = stuQuery[0]

    d = datetime.datetime.now(pytz.utc)
    eml = stuOb.s_eml
    fname = stuOb.s_fname
    lname = stuOb.s_lname
    
    attendanceQuery = Attendance.objects.filter(dte_date__date=d, student=eml, s_class=classId)
    if attendanceQuery.exists() == False:
        attendanceOb = Attendance(dte_date=d,s_class=classOb,student=stuOb)
        attendanceOb.save()
        return HttpResponseRedirect(reverse('student_view_attendance_submitted_with_classId',kwargs={"classId":classId}))
    else:
        return HttpResponseRedirect(reverse('student_view_attendance_already_submitted_with_classId',kwargs={"classId":classId}))

#=======================

def student_view_bigQRcode(request, classId = None, className = None, blockSize = 20):
    if((classId == None) and (className == None)):
        return HttpResponseBadRequest()
    elif(classId == None):
        classId = ClassName.objects.filter(s_className__iexact=className)[0].id # pyright: ignore[reportAttributeAccessIssue]
    else:
        className = ClassName.objects.filter(id=classId)[0].s_className

    qrSrc = qrgenerator(request, classId, blockSize)
    return render(request,
                  "StudentView/StudentViewQrCode.html",
                  {
                      "classId":classId,
                      "className":className,
                      "qrSrc":qrSrc,
                  })

#=======================

def student_view_attendance_submitted(request, classId=None, className=None):
    if((classId == None) and (className == None)):
        pass
    elif(classId == None):
        classId = ClassName.objects.filter(s_className__iexact=className)[0].id # pyright: ignore[reportAttributeAccessIssue]
    else:
        className = ClassName.objects.filter(id=classId)[0].s_className

    return render(request,
                  "StudentView/Submitted.html",
                  {
                      "classId":classId,
                      "className":className,
                  })

def student_view_attendance_already_submitted(request, classId=None, className=None):
    if((classId == None) and (className == None)):
        pass
    elif(classId == None):
        classId = ClassName.objects.filter(s_className__iexact=className)[0].id # pyright: ignore[reportAttributeAccessIssue]
    else:
        className = ClassName.objects.filter(id=classId)[0].s_className

    return render(request,
                  "StudentView/AlreadySubmitted.html",
                  {
                      "classId":classId,
                      "className":className,
                  })
