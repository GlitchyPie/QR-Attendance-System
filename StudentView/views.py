import datetime
from django.shortcuts import render
from FacultyView.models import Student, ClassName, Attendance
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.urls import reverse

# Create your views here.

present = set()

#=======================
def student_entry_name(request, className):
    classId = ClassName.objects.filter(s_className__iexact=className)[0].id
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
    classId = ClassName.objects.filter(s_className__iexact=className)[0].id
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

    stuQuery = Student.objects.filter(s_eml=eml)
    stuOb = None
    if len(stuQuery) == 0:
        stuOb = Student(s_eml=eml,s_fname=fname,s_lname=lname)
        stuOb.save()
    else:
        stuOb = stuQuery[0]

    eml = stuOb.s_eml
    fname = stuOb.s_fname
    lname = stuOb.s_lname

    attendanceQuery = Attendance.objects.filter(dte_date__date=datetime.date, student=eml, s_class=classId)
    if attendanceQuery.exists() == False:
        attendanceOb = Attendance(dte_date=datetime.datetime.now(),s_class=classId,student=eml)
        attendanceOb.save()

    return HttpResponseRedirect("/submitted")

#=======================

def submitted(request):
    return render(request, "StudentView/Submitted.html")

#def add_manually_post(request):
#    student_roll = request.POST["student-name"]
#    student = Student.objects.get(s_roll=student_roll)
#    present.add(student)
#    return HttpResponseRedirect("/submitted")



