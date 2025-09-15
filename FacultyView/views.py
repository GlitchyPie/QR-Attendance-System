import datetime
import pytz
import csv
import io
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.urls import reverse
from .models import Student, ClassName, Attendance
import qrcode

#TODO: This will need to be changed once in production in order to correctly serve the image....
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

    present = Attendance.objects.filter(dte_date__date=datetime.datetime.now(pytz.utc), s_class=classId)
    return render(
        request,
        "FacultyView/FacultyViewClass.html",
        {
            "present": present,
            "className": className,
            "classId": classId,
        },
    )
#=======================

def faculty_view_present_name(request,className):
    classId = ClassName.objects.filter(s_className__iexact=className)[0].id
    return faculty_view_present(request, classId, className)

def faculty_view_present_id(request,classId):
    className = ClassName.objects.filter(id=classId)[0].s_className
    return faculty_view_present(request,classId,className)

def faculty_view_present(request,classId,className):
    qrgenerator(request,classId)

    present = Attendance.objects.filter(dte_date__date=datetime.datetime.now(pytz.utc), s_class=classId)
    return render(
        request,
        "FacultyView/StudentList.html",
        {
            "present": present,
            "className": className,
            "classId": classId,
        },
    )

#=======================

def faculty_view_create_class(request):
    if request.method == "GET" :
        return HttpResponseBadRequest() #This should only accept POST requests
    
    className = request.POST["class_name"]
    classNameEntry = ClassName(s_className=className)
    classNameEntry.save()
    return HttpResponseRedirect(reverse('faculty_view_class_id',kwargs={"classId":classNameEntry.id}))

def faculty_view(request):
    classes = ClassName.objects.all()
    return render(
        request,
        "FacultyView/FacultyViewIndex.html",
        {
            "classes": classes
        },
    )

#=======================

def faculty_view_attendance_export_id(request,classId, year, month, day):
    className = ClassName.objects.filter(id=classId)[0].s_className
    return faculty_view_attendance_export(request, classId, ClassName, year, month, day)

def faculty_view_attendance_export_name(request,className, year, month, day):
    classId = ClassName.objects.filter(s_className__iexact=className)[0].id
    return faculty_view_attendance_export(request, classId, ClassName, year, month, day)

def faculty_view_attendance_export(request, classId, className, year, month, day):
    present = Attendance.objects.filter(dte_date__year=year, dte_date__month=month, dte_date__day=day, s_class=classId)

    sio = io.StringIO()
    csvWriter = csv.writer(sio)
    csvWriter.writerows(present)
    return HttpResponse(sio.getvalue(),content_type="text/plain")