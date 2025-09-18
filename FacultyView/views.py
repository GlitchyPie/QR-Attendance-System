import datetime
import pytz
import csv
import os
import qrcode
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.urls import reverse
from .models import Student, ClassName, Attendance

def qrgenerator(request,classId = -1,boxSize=20):
    link = reverse('student_view_name_entry_by_class_id',kwargs={'classId':classId})
    link = f"{request.scheme}://{request.META['HTTP_HOST']}{link}"
    def generate_qr_code(link,classId,boxSize):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_H,
            box_size=boxSize,
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
        
        img.save(f"{pth}/qrcode_{classId}_{boxSize}.png") # pyright: ignore[reportArgumentType]

    generate_qr_code(link,classId,boxSize)
    return f"{settings.MEDIA_URL}qrs/qrcode_{classId}_{boxSize}.png"

#=======================

def faculty_view_delete_attendance(request, classId = None, className = None):
    if request.method == "GET" :
        return HttpResponseBadRequest() #This should only accept POST requests
    
    if((classId == None) and (className == None)):
        return HttpResponseBadRequest()
    elif(classId == None):
        classId = ClassName.objects.filter(s_className__iexact=className)[0].id # pyright: ignore[reportAttributeAccessIssue]
    else:
        className = ClassName.objects.filter(id=classId)[0].s_className

    d = datetime.datetime.now(pytz.utc)
    eml = request.POST["student_email"].lower()

    attendanceQuery = Attendance.objects.filter(dte_date__date=d, student=eml, s_class=classId)

    if attendanceQuery.exists():
        attendanceQuery[0].delete()

    return HttpResponseRedirect(reverse('faculty_view_by_class_id_today',kwargs={"classId":classId}))
    
#=======================

def faculty_view_class(request, classId = None, className = None):
    if((classId == None) and (className == None)):
        return HttpResponseBadRequest()
    elif(classId == None):
        classId = ClassName.objects.filter(s_className__iexact=className)[0].id # pyright: ignore[reportAttributeAccessIssue]
    else:
        className = ClassName.objects.filter(id=classId)[0].s_className

    qrSrc = qrgenerator(request,classId)

    present = Attendance.objects.filter(dte_date__date=datetime.datetime.now(pytz.utc), s_class=classId)
    return render(
        request,
        "FacultyView/FacultyViewClass.html",
        {
            "present": present,
            "className": className,
            "classId": classId,
            "qrSrc": qrSrc,
        },
    )

#=======================

def faculty_view_present_list(request, classId = None, className = None, year = None, month = None, day = None):
    if((classId == None) and (className == None)):
        classId = None
        className = "All"
    elif(classId == None):
        classId = ClassName.objects.filter(s_className__iexact=className)[0].id # pyright: ignore[reportAttributeAccessIssue]
    else:
        className = ClassName.objects.filter(id=classId)[0].s_className

    D = datetime.datetime.now(pytz.utc)
    year = year or D.year
    month = month or D.month
    day = day or D.day

    if(classId):
        present = Attendance.objects.filter(dte_date__year=year, dte_date__month=month,dte_date__day=day, s_class=classId)
    else:
        present = Attendance.objects.filter(dte_date__year=year, dte_date__month=month, dte_date__day=day)

    return render(
        request,
        "FacultyView/StudentList.html",
        {
            "present": present,
            "className": className,
            "classId": classId,
            "dte_year": year,
            "dte_month": month,
            "dte_day": day,
        },
    )

#=======================

def faculty_view_attendance_export(request, classId = None, className = None, action = 'view', year = None, month = None, day = None):
    if((classId == None) and (className == None)):
        className = "All"
    elif(classId == None):
        classId = ClassName.objects.filter(s_className__iexact=className)[0].id # pyright: ignore[reportAttributeAccessIssue]
    else:
        className = ClassName.objects.filter(id=classId)[0].s_className

    D = datetime.datetime.now(pytz.utc)
    year = year or D.year
    month = month or D.month
    day = day or D.day

    presentQuery = Attendance.objects.all()

    if classId:
        presentQuery = presentQuery.filter(s_class=classId)

    presentQuery = presentQuery.filter(dte_date__year=year)

    presentQuery = presentQuery.filter(dte_date__month=month)

    presentQuery = presentQuery.filter(dte_date__day=day)

    match action:
        case 'export':
            return render_faculty_view_attendance_export_CSV(request, presentQuery)
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

def render_faculty_view_attendance_export_CSV(request, present_query):
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
    return HttpResponseRedirect(reverse('faculty_view_by_class_id_today',kwargs={"classId":classNameEntry.id})) # pyright: ignore[reportAttributeAccessIssue]

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