import datetime
import pytz
import qrcode
import os
from django.urls import reverse
from django.conf import settings
from FacultyView.models import Attendance, ClassName, ModuleName, Student

class LocalState:
    last_attendance_modified_class : dict[int,datetime.datetime] = {
            -1 : datetime.datetime.now(pytz.utc)
        }
    
    last_attendance_modified_module : dict[int,datetime.datetime] = {
            -1 : datetime.datetime.now(pytz.utc)
        }
    
    def get_attendance_modified_class(self, cls : ClassName | None = None):
        id = -1
        if(cls):
            id = cls.id # type: ignore
        return self.last_attendance_modified_class.get(id, self.last_attendance_modified_class[-1])
    
    def set_attendance_modified_class(self, cls : ClassName, dte : datetime.datetime | None = None):
        dte = dte or datetime.datetime.now(pytz.utc)
        self.last_attendance_modified_class[-1] = dte
        self.last_attendance_modified_class[cls.id] = dte # type: ignore
        self.last_attendance_modified_class[cls.id] = dte # type: ignore
        self.set_attendance_modified_module(cls.moduleName)

    def get_attendance_modified_module(self, mod : ModuleName | None = None):
        id = -1
        if(mod):
            id = mod.id # type: ignore
        return self.last_attendance_modified_module.get(id, self.last_attendance_modified_module[-1])
    
    def set_attendance_modified_module(self, mod : ModuleName, dte : datetime.datetime | None = None):
        dte = dte or datetime.datetime.now(pytz.utc)
        self.last_attendance_modified_module[-1] = dte
        self.last_attendance_modified_module[mod.id] = dte # type: ignore
        self.last_attendance_modified_module[mod.id] = dte # type: ignore

    def get_attendance_modified(self):
        A = self.get_attendance_modified_class()
        B = self.get_attendance_modified_module()
        return max([A , B])
#End Class

STATE = LocalState()

def qrgenerator(request, classId : int = -1, boxSize : int=20):
    link = reverse('student_view_enter_student',kwargs={'classId':classId})
    link = f"{request.scheme}://{request.META['HTTP_HOST']}{link}"
    def generate_qr_code(link,classId,boxSize):
        pth = os.path.join(settings.MEDIA_ROOT,'qrs')
        try:
            os.makedirs(pth)
        except FileExistsError:
            pass
        pth = os.path.join(pth,f"qrcode_{classId}_{boxSize}.png")
        if os.path.isfile(pth) == False:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.ERROR_CORRECT_H,
                box_size=boxSize,
                border=4,
            )
            qr.add_data(link)
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')
            img.save(pth) # pyright: ignore[reportArgumentType]
        #End if
    #End def:

    generate_qr_code(link,classId,boxSize)
    return f"{settings.MEDIA_URL}qrs/qrcode_{classId}_{boxSize}.png"

def getClass(classId : int|None, className : str|None):
    if((classId == None) and (className == None)):
        return None
    elif(classId != None):
        return ClassName.objects.filter(id=classId)[0]
    else:
        return ClassName.objects.filter(s_className__iexact=className)[0]

def getModule(moduleId : int|None, moduleName : str|None):
    if((moduleId == None) and (moduleName == None)):
        return None
    elif(moduleId != None):
        return ModuleName.objects.filter(id=moduleId)[0]
    else:
        return ModuleName.objects.filter(s_moduleName__iexact=moduleName)[0]
    
def getClassAndModule(classId : int|None = None, className : str|None = None,
                      moduleId : int|None = None, moduleName : str|None = None,
                      cls : ClassName|None = None, mod : ModuleName|None = None):
    
    clsOb = cls
    modOb = mod
    
    if clsOb: #If we have a class object the class and module can be determined exactly
        modOb = clsOb.moduleName
    elif classId: #If we have a class ID, this also allows us to determine the class and module exactly
        clsOb = ClassName.objects.filter(id=classId)[0]
        modOb = clsOb.moduleName
    elif className: #For a class name we will either return the first class we can,
        #or, if given a module as well, we will do our best to match the class and module

        c = ClassName.objects.filter(s_className__iexact = className)
        if modOb:
            c = c.filter(moduleName = modOb)
        elif moduleId:
            c = c.filter(moduleName = moduleId)
        elif moduleName:
            c = c.filter(moduleName__s_moduleName__iexact = moduleName)
    
        clsOb = c[0]
        modOb = clsOb.moduleName

    elif moduleId: #We can not determine a class if only given module information
        modOb = ModuleName.objects.filter(id = moduleId)[0]
    elif moduleName:
        modOb = ModuleName.objects.filter(s_moduleName__iexact = moduleId)[0]

    return (clsOb, modOb)

def attendance_query(cls : ClassName|None = None,
                     mod : ModuleName|None = None, 
                     classId : int|None = None, className : str|None = None, 
                     moduleId : int|None = None, moduleName : str|None = None, 
                     dte : datetime.datetime|None = None,
                     year : int|None = None,
                     month : int|None = None,
                     day : int|None = None,
                     dte_start : datetime.datetime|None = None, dte_end : datetime.datetime|None = None,
                     year_start : int|None = None,
                     month_start : int|None = None,
                     day_start : int|None = None,
                     year_end : int|None = None,
                     month_end : int|None = None,
                     day_end : int|None = None,
                     student : Student | None = None,):

    if((cls == None) and (mod == None)):
        cls,mod = getClassAndModule(classId, className, moduleId, moduleName)
    elif(cls):
        mod = mod or cls.moduleName

    present = Attendance.objects.all()
    if(cls):
        present = present.filter(className = cls) # pyright: ignore[reportAttributeAccessIssue]
    elif(mod):
        present = present.filter(className__moduleName = mod) # pyright: ignore[reportAttributeAccessIssue]

    if dte:
        year = dte.year
        month = dte.month
        day = dte.day

    if dte_start:
        year_start = dte_start.year
        month_start = dte_start.month
        day_end = dte_start.day
    
    if dte_end:
        year_end = dte_end.year
        month_end = dte_end.month
        day_end = dte_end.day
    
    if((year_start or month_start or day_start) or (year_end or month_end or day_end)):
        if(year_start):
            present = present.filter(dte_date__year__gte=year_start)
        
        if(month_start):
            present = present.filter(dte_date__month__gte=month_start)

        if(day_start):
            present = present.filter(dte_date__day__gte=day_start)
        
        if(year_end):
            present = present.filter(dte_date__year__lte=year_end)
        
        if(month_end):
            present = present.filter(dte_date__month__lte=month_end)

        if(day_end):
            present = present.filter(dte_date__day__lte=day_end)

    else:
        if(year):
            present = present.filter(dte_date__year=year)

        if(month):
            present = present.filter(dte_date__month=month)

        if(day):
            present = present.filter(dte_date__day=day)

    #--------

    if(student):
        present = present.filter(student=student)

    return (present, cls, mod)
    