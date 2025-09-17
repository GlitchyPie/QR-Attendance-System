import datetime
import pytz
from django.shortcuts import render
from FacultyView.models import Student, ClassName, Attendance
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.urls import reverse

#=======================
def student_entry_name(request, className):
    classId = ClassName.objects.filter(s_className__iexact=className)[0].id # pyright: ignore[reportAttributeAccessIssue]
    return student_entry(request,classId,className)

def student_entry_id(request, classId):
    className = ClassName.objects.filter(id=classId)[0].s_className
    return student_entry(request,classId,className)

def student_entry(request, classId, className):
    return render(request, 
                  "StudentView/StudentViewstudent_entry.html",
                  {
                      "classId":classId,
                      "className":className,
                  })
#=======================

def submit_attendance_name(request,className):
    classId = ClassName.objects.filter(s_className__iexact=className)[0].id # pyright: ignore[reportAttributeAccessIssue]
    return submit_attendance(request,classId,className)

def submit_attendance_id(request,classId):
    className = ClassName.objects.filter(id=classId)[0].s_className
    return submit_attendance(request,classId,className)

def submit_attendance(request,classId,className):
    if request.method == "GET" :
        return HttpResponseBadRequest() #This should only accept POST requests
    
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
        return HttpResponseRedirect("/submitted")
    else:
        return HttpResponseRedirect("/alreadysubmitted")
    

#=======================

def delete_attendance_id(request, classId):
    if request.method == "GET" :
        return HttpResponseBadRequest() #This should only accept POST requests
    
    d = datetime.datetime.now(pytz.utc)
    eml = request.POST["student_email"].lower()

    attendanceQuery = Attendance.objects.filter(dte_date__date=d, student=eml, s_class=classId)

    if attendanceQuery.exists():
        attendanceQuery[0].delete()

    return HttpResponseRedirect(reverse('faculty_view_class_id',kwargs={"classId":classId}))
    

#=======================

def submitted(request):
    return render(request, "StudentView/Submitted.html")

def already_submitted(request):
    return render(request, "StudentView/AlreadySubmitted.html")
