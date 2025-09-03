from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Student
import qrcode
import socket
from StudentView.views import present


def qrgenerator(request):
    #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #s.connect(("8.8.8.8", 80))
    #ip = s.getsockname()[0]

    link = f"{request.scheme}://{request.META['HTTP_HOST']}:{request.META['SERVER_PORT']}/add_manually"

    def generate_qr_code(link):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=20,
            border=4,
        )
        qr.add_data(link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save("FacultyView/static/FacultyView/qrcode.png")

    generate_qr_code(link)


def faculty_view(request):
    if request.method == "POST":
        student_roll = request.POST["student_id"]
        student = Student.objects.get(s_roll=student_roll)
        if student in present:
            present.remove(student)
        return HttpResponseRedirect("/")

    else:
        qrgenerator(request)
        return render(
            request,
            "FacultyView/FacultyViewIndex.html",
            {
                "students": present,
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

def add_manually_year(request, year):
    students = Student.objects.filter(s_year=year)
    return render_student_list(request, students)
