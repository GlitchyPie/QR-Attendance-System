import qrcode
import os
from django.urls import reverse
from django.conf import settings
from FacultyView.models import ClassName, ModuleName

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

