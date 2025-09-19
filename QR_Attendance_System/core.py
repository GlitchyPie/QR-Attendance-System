import qrcode
import os
from django.urls import reverse
from django.conf import settings
from FacultyView.models import ClassName, ModuleName

def qrgenerator(request,classId = -1,boxSize=20):
    link = reverse('student_view_enter_student',kwargs={'classId':classId})
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

def getClass(classId, className):
    if((classId == None) and (className == None)):
        return None
    elif(classId != None):
        return ClassName.objects.filter(id=classId)[0]
    else:
        return ClassName.objects.filter(s_className__iexact=className)[0]

def getModule(moduleId, moduleName):
    if((moduleId == None) and (moduleName == None)):
        return None
    elif(moduleId != None):
        return ModuleName.objects.filter(id=moduleId)[0]
    else:
        return ModuleName.objects.filter(s_moduleName__iexact=moduleName)[0]
    
def getClassAndModule(classId = None, className = None, moduleId = None, moduleName = None):
    cls = None
    mod = None
    
    if(classId): #For a given class ID we can accuratly get the class and its module
        cls = ClassName.objects.filter(id=classId)[0]
        mod = cls.moduleName
    
    elif(className): # For a given class name...
        q = ClassName.objects.all()
        if(moduleId): # If we are given module details, use them to limit the search to classes in that module.
            q = q.filter(moduleName=moduleId)
        elif(moduleName):
            q = q.filter(moduleName__s_moduleName__iexact=moduleName)

        q = q.filter(s_className__iexact=className)
        cls = q[0]
        mod = mod or cls.moduleName

    elif(moduleId): #If we are only given module info, then only return the module.
        mod = ModuleName.objects.filter(id=moduleId)[0]
    elif(moduleName):
        mod = ModuleName.objects.filter(s_moduleName=moduleName)[0]
    
    return (cls,mod)
