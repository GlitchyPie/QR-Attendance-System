from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Student, ClassName, Attendance
import qrcode
import socket
from StudentView.views import present
import urllib.parse

def qrgenerator(request,className = ""):
    #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #s.connect(("8.8.8.8", 80))
    #ip = s.getsockname()[0]

    link = f"{request.scheme}://{request.META['HTTP_HOST']}:{request.META['SERVER_PORT']}/class/{urllib.parse.quote(className)}/add_manually"

    def generate_qr_code(link,className):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=20,
            border=4,
        )
        qr.add_data(link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(f"FacultyView/static/FacultyView/qrcode_{className}.png")

    generate_qr_code(link,className)

def faculty_view_class(request,className):
    if request.method == "POST":
        student_roll = request.POST["student_id"]
        student = Student.objects.get(s_roll=student_roll)
        if student in present:
            present.remove(student)
        return HttpResponseRedirect("/")
    else:
        qrgenerator(request,className)
        return render(
            request,
            "FacultyView/FacultyViewClass.html",
            {
                "students": present,
                "className": className
            },
        )

def faculty_view(request):
    classes = ClassName.objects.all()
    return render(
        request,
        "FacultyView/FacultyViewIndex.html",
        {
            "classes": classes
        },
    )
        

def render_student_list(request,students):
    return render(
        request,
        "StudentView/StudentViewIndex.html",
        {
            "students": students,
        },
    )

def add_manually(request):
    students = Student.objects.all().order_by("s_roll")
    return render_student_list(request, students)

def add_manually_class(request,className):
    students = Student.objects.all().order_by("s_roll")
    return render_student_list(request, students)

def add_manually_year(request, year):
    students = Student.objects.filter(s_year=year)
    return render_student_list(request, students)

#https://stackoverflow.com/questions/57989320/django-filter-foreignkey-related-model-filtering
def add_manually_filtered(request, branch, section, year):
    students = Student.objects.filter(s_branch__branch__iexact=branch).filter(s_section__section__iexact=section).filter(s_year__year=year)
    return render_student_list(request, students)

def add_manually_filtered_2(request, branch, section):
    students = Student.objects.filter(s_branch__branch__iexact=branch).filter(s_section__section__iexact=section)
    return render_student_list(request, students)

def add_manually_filtered_3(request, branch):
    students = Student.objects.filter(s_branch__branch__iexact=branch)
    return render_student_list(request, students)