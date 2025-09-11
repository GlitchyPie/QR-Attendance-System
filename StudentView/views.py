from django.shortcuts import render
from FacultyView.models import Student, ClassName
from django.http import HttpResponseRedirect
from django.urls import reverse

# Create your views here.

present = set()

#=======================
def student_entry_name(request,className):
    classId = ClassName.objects.filter(s_className__iexact=className)[0].id
    return student_entry(request,classId,className)

def student_entry_id(request,classId):
    className = ClassName.objects.filter(id=classId)[0].s_className
    return student_entry(request,classId,className)

def student_entry(request,classId, className):
    return render(request, "StudentView/StudentViewstudent_entry.html")
#=======================

def submit_attendance_name(request,className):
    classId = ClassName.objects.filter(s_className__iexact=className)[0].id
    return submit_attendance(request,classId,className)

def submit_attendance_id(request,classId):
    className = ClassName.objects.filter(id=classId)[0].s_className
    return submit_attendance(request,classId,className)

def submit_attendance(request,className):
    #Do stuff here.....
    return HttpResponseRedirect("/submitted")

#=======================

def submitted(request):
    return render(request, "StudentView/Submitted.html")

#def add_manually_post(request):
#    student_roll = request.POST["student-name"]
#    student = Student.objects.get(s_roll=student_roll)
#    present.add(student)
#    return HttpResponseRedirect("/submitted")



