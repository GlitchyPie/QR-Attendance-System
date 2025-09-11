from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Student, ClassName, Attendance
import qrcode
import socket
from StudentView.views import present
import urllib.parse

def qrgenerator(request,classId = -1):
    link = f"{request.scheme}://{request.META['HTTP_HOST']}/class/{classId}/student_entry"
    def generate_qr_code(link,classId):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=20,
            border=4,
        )
        qr.add_data(link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(f"FacultyView/static/FacultyView/qrcode_{classId}.png")

    generate_qr_code(link,classId)

#=======================

def faculty_view_class_name(request,className):
    classId = ClassName.objects.filter(s_className__iexact=className)[0].id
    return faculty_view_class(request, classId, className)

def faculty_view_class_id(request,classId):
    className = ClassName.objects.filter(id=classId)[0].s_className
    return faculty_view_class(request,classId,className)

def faculty_view_class(request,classId,className):
    qrgenerator(request,classId)
    present = []
    return render(
        request,
        "FacultyView/FacultyViewClass.html",
        {
            "students": present,
            "className": className,
            "classId": classId,
        },
    )

#=======================

def faculty_view(request):
    classes = ClassName.objects.all()
    return render(
        request,
        "FacultyView/FacultyViewIndex.html",
        {
            "classes": classes
        },
    )
        

#def render_student_list(request,students):
#    return render(
#        request,
#        "StudentView/StudentViewIndex.html",
#        {
#            "students": students,
#        },
#    )

#def add_manually(request):
#    students = Student.objects.all().order_by("s_roll")
#    return render_student_list(request, students)

#def add_manually_class(request,className):
#    students = Student.objects.all().order_by("s_roll")
#    return render_student_list(request, students)

#def add_manually_year(request, year):
#    students = Student.objects.filter(s_year=year)
#    return render_student_list(request, students)

#https://stackoverflow.com/questions/57989320/django-filter-foreignkey-related-model-filtering
#def add_manually_filtered(request, branch, section, year):
#    students = Student.objects.filter(s_branch__branch__iexact=branch).filter(s_section__section__iexact=section).filter(s_year__year=year)
#    return render_student_list(request, students)

#def add_manually_filtered_2(request, branch, section):
#    students = Student.objects.filter(s_branch__branch__iexact=branch).filter(s_section__section__iexact=section)
#    return render_student_list(request, students)

#def add_manually_filtered_3(request, branch):
#    students = Student.objects.filter(s_branch__branch__iexact=branch)
#    return render_student_list(request, students)