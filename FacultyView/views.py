import datetime
import pytz
import csv
import os
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.urls import reverse
from .models import Student, ClassName, Attendance
import qrcode

def qrgenerator(request,classId = -1):
    link = reverse('student_entry_id',kwargs={'classId':classId})
    link = f"{request.scheme}://{request.META['HTTP_HOST']}{link}"
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
        pth = f"{settings.MEDIA_ROOT}/qrs"
        try:
            os.makedirs(pth)
        except FileExistsError:
            pass
        
        img.save(f"{pth}/qrcode_{classId}.png")

    generate_qr_code(link,classId)

#=======================

def faculty_view_class_name(request,className):
    classId = ClassName.objects.filter(s_className__iexact=className)[0].id
    return render_faculty_view_class(request, classId, className)

def faculty_view_class_id(request,classId):
    className = ClassName.objects.filter(id=classId)[0].s_className
    return render_faculty_view_class(request,classId,className)

def render_faculty_view_class(request,classId,className):
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

def faculty_view_ajax_present_id(request,classId):
    className = ClassName.objects.filter(id=classId)[0].s_className
    return render_faculty_view_ajax_present_now(request,classId,className)

def faculty_view_ajax_present_name(request,className):
    classId = ClassName.objects.filter(s_className__iexact=className)[0].id
    return render_faculty_view_ajax_present_now(request, classId, className)

def faculty_view_ajax_present_dte_id(request, classId, year, month, day):
    className = ClassName.objects.filter(id=classId)[0].s_className
    return render_faculty_view_ajax_present(request, classId, className, year, month, day)

def faculty_view_ajax_present_dte_name(request, className, year, month, day):
    classId = ClassName.objects.filter(s_className__iexact=className)[0].id
    return render_faculty_view_ajax_present(request, classId, className, year, month, day)

#==========

def render_faculty_view_ajax_present_now(request, classId, className):
    return render_faculty_view_ajax_present_dte(request, classId, className, datetime.datetime.now(pytz.utc))

def render_faculty_view_ajax_present_dte(request, classId, className,dte):
    return render_faculty_view_ajax_present(request, classId, className, dte.year, dte.month, dte.day)

def render_faculty_view_ajax_present(request, classId, className, year, month, day):
    present = []
    if(classId == None):
        present = Attendance.objects.filter(dte_date__year=year, dte_date__month=month,dte_date__day=day)
    else:
        present = Attendance.objects.filter(dte_date__year=year, dte_date__month=month,dte_date__day=day, s_class=classId)

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

def faculty_view_attendance_export_form(request):
    return render_faculty_view_attendance_export_form_now(request, None, None)

def faculty_view_attendance_export_form_id(request, classId):
    className = ClassName.objects.filter(id=classId)[0].s_className
    return render_faculty_view_attendance_export_form_now(request, classId, className)

def faculty_view_attendance_export_form_name(request, className):
    classId = ClassName.objects.filter(s_className__iexact=className)[0].id
    return render_faculty_view_attendance_export_form_now(request, classId, className)

def render_faculty_view_attendance_export_form_now(request, classId, className):
    D = datetime.datetime.now(pytz.utc)
    return render_faculty_view_attendance_export_dte(request, classId, className, 'view', D.year, D.month, D.day)

#==========

def faculty_view_attendance_export_dte_id(request, classId, action, year, month, day):
    className = ClassName.objects.filter(id=classId)[0].s_className
    return render_faculty_view_attendance_export_dte(request, classId, className, action, year, month, day)

def faculty_view_attendance_export_dte_name(request, className, action, year, month, day):
    classId = ClassName.objects.filter(s_className__iexact=className)[0].id
    return render_faculty_view_attendance_export_dte(request, classId, className, action, year, month, day)

def faculty_view_attendance_export_dte_allClasses(request, action, year, month, day):
    return render_faculty_view_attendance_export_dte(request, -1, None, action, year, month, day)

#==========

def render_faculty_view_attendance_export_dte(request, classId, className, action, year, month, day):
    presentQuery = []

    if classId != None:
        presentQuery = Attendance.objects.all()

        if classId >= 0:
            presentQuery = presentQuery.filter(s_class=classId)

        if year != None:
            presentQuery = presentQuery.filter(dte_date__year=year)

        if month != None:
            presentQuery = presentQuery.filter(dte_date__month=month)

        if day != None:
            presentQuery = presentQuery.filter(dte_date__day=day)
    #End if

    match action:
        case 'export':
            return faculty_view_attendance_export_export(request, presentQuery)
        case 'view':
            return render_faculty_view_attendance_export_form(request, classId, className, presentQuery, year, month, day)
        case _:
            return HttpResponseBadRequest()

def render_faculty_view_attendance_export_form(request, classId, className, present, year, month, day):
    classes = ClassName.objects.all();
    return render(
        request,
        "FacultyView/FacultyViewExportForm.html",
        {
            "classes":classes,
            "classId":classId,
            "className":className,
            "present":present,
            "dte_year":year,
            "dte_month":month,
            "dte_day":day,
        },
    )

def faculty_view_attendance_export_export(request, present_query):
    response = HttpResponse (content_type='text/csv')
    csvWriter = csv.writer(response)

    csvWriter.writerow([
        'Student Email',
        'First Name',
        'Last Name',
        'Class',
        'Date / Time',
    ])
    for entry in present_query:
        csvWriter.writerow([
            entry.student.s_eml,
            entry.student.s_fname,
            entry.student.s_lname,
            entry.s_class.s_className,
            entry.dte_date,
        ])

    return response

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