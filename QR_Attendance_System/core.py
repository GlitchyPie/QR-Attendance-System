import datetime
import pytz
import re
import os

import qrcode

from hashlib import md5

import PIL.features as Pil_Features
import PIL.Image as Pil_Image

from qrcode.image.pil import PilImage as qrcode_pilImage
from qrcode.image.svg import SvgPathImage as qrcode_svgPathImage

from django.urls import reverse
from django.conf import settings
from FacultyView.models import Attendance, ClassName, ModuleName, Student
from django.db.models.functions import TruncDate, TruncTime

class NoAcceptableContentType(Exception):
    """Custom exception for my app."""
    pass

class RequestedContentTypeNotFound(Exception):
    """Custom exception for my app."""
    pass

class LocalState:
    last_attendance_modified_class : dict[int,datetime.datetime] = {
            -1 : datetime.datetime.now(pytz.utc)
        }
    
    last_attendance_modified_module : dict[int,datetime.datetime] = {
            -1 : datetime.datetime.now(pytz.utc)
        }
    
    supported_pil_image_formats : dict = {}

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

    def get_attendance_modified(self,cls_or_mod : ClassName | ModuleName | None = None):
        if(isinstance(cls_or_mod,ClassName)):
            return self.get_attendance_modified_class(cls_or_mod)
        elif(isinstance(cls_or_mod,ModuleName)):
            return self.get_attendance_modified_module(cls_or_mod)

        A = self.get_attendance_modified_class()
        B = self.get_attendance_modified_module()
        return max([A , B])

    def get_supported_PIL_Images(self):
        if(self.supported_pil_image_formats):
            return self.supported_pil_image_formats
        
        supported = {}
        # 1. Gather registered extensions (always available formats)
        for ext, fmt in Pil_Image.registered_extensions().items():
            if fmt not in supported:
                supported[fmt] = {'extensions': set(), 'available': True}
            supported[fmt]['extensions'].add(ext)

        # 2. Check optional features (libs required)
        # Map Pillow feature names -> format names
        feature_map = {
            'webp': 'WEBP',
            'webp_anim': 'WEBP',   # animation is optional, base WEBP may still work
            'webp_mux': 'WEBP',    # muxing (advanced WebP features)
            'jpg_2000': 'JPEG2000',
            'avif': 'AVIF',
            'freetype2': 'FREETYPE',
            'raqm': 'RAQM',
            'libjpeg_turbo': 'JPEG',  # turbo-optimized JPEG
        }
        
        for feat, fmt in feature_map.items():
            avail = Pil_Features.check(feat)
            if fmt not in supported:
                supported[fmt] = {'extensions': set(), 'available': avail}
            else:
                # If already in supported (via registered_extensions), refine availability
                supported[fmt]['available'] = supported[fmt]['available'] or avail

        # Normalize extensions to lists
        for fmt in supported:
            supported[fmt]['extensions'] = sorted(supported[fmt]['extensions'])

        #Inject support for svg as it's not directly supported by PIL but
        #Is supported via the qr image factory.
        supported['SVG'] = {
            'extensions':['.svg'],
            'available':True,
        }

        self.supported_pil_image_formats = supported
        return supported 

    def __init__(self) -> None:
        self.supported_pil_image_formats = self.get_supported_PIL_Images()
        pass
#End Class

STATE = LocalState()

PREFERRED_QR_IMAGE_FORMATS = [
        {'e':'.svg', 'f':'SVG','m':'image/svg+xml', 'c':qrcode_svgPathImage, 'd':['1']},
        {'e':'.png', 'f':'PNG','m':'image/png', 'c':qrcode_pilImage, 'd':['1']},
        {'e':'.webp', 'f':'WEBP','m':'image/webp', 'c':qrcode_pilImage, 'd':['1']},
        {'e':'.gif', 'f':'GIF','m':'image/gif', 'c':qrcode_pilImage, 'd':['1']},
        {'e':'.bmp', 'f':'BMP','m':'image/bmp', 'c':qrcode_pilImage, 'd':['1']},
        {'e':'.jpg', 'f':'JPEG','m':'image/jpeg', 'c':qrcode_pilImage, 'd':['1']},
        {'e':'.tiff', 'f':'TIFF','m':'image/tiff', 'c':qrcode_pilImage, 'd':['1']},
        {'e':'.avif', 'f':'AVIF', 'm':'image/avif', 'c':qrcode_pilImage, 'd':['1']},
        {'e':'.jp2', 'f':'JPEG2000', 'm':'image/jp2', 'c':qrcode_pilImage, 'd':['RGB', 'RGBA', 'L', 'CMYK']}
    ]
PREFERRED_QR_FORMAT_NAMES = [f['f'] for f in PREFERRED_QR_IMAGE_FORMATS]
PREFERRED_QR_IMAGE_MIMES = [m['m'] for m in PREFERRED_QR_IMAGE_FORMATS]



def qrgenerator(request, classId : int, boxSize : int, extension : str|None):
    def generate_qr_code(link : str, boxSize : int, image_factory):
        qr = qrcode.QRCode(
            version=None, #https://pypi.org/project/qrcode/
            error_correction=qrcode.ERROR_CORRECT_H,
            box_size=boxSize,
            border=4,
            image_factory=image_factory
        )
        qr.add_data(link)
        qr.make(fit=True)
        return qr.make_image(fill_color='black', back_color='white')
    #End def:

    def safe_filename(name):
        # Remove path separators and invalid characters
        name = os.path.basename(name)
        return re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", name)
    #End def:

    #The link to embed in the QR code
    link = reverse('student_view_registration_form',kwargs={'classId':classId})
    link = f"{request.scheme}://{request.get_host()}{link}"

    #A hash of the link to ensure if anything changes with the link a new QR code is generated
    LINK_HASH = md5(link.encode(), usedforsecurity=False).hexdigest()

    local_file_dir = settings.MEDIA_ROOT
    FILE_DIR = f"qrs/{classId}/"

    #Create local directories if they don't exist
    PATH_PARTS = FILE_DIR.split('/')    
    for part in PATH_PARTS:
        local_file_dir = os.path.join(local_file_dir,part)

    try:
        os.makedirs(local_file_dir)
    except FileExistsError:
        pass
    
    REQUIRED_EXTENSION = f".{(extension or '').lower()}"
    REQUIRED_MIME = request.GET.get('mime','').lower()

    negotiated_format = None

    if(REQUIRED_EXTENSION != '.'):
        required_format_name = ''
        for k in STATE.supported_pil_image_formats:
            e = STATE.supported_pil_image_formats[k]['extensions']
            if REQUIRED_EXTENSION in e:
                required_format_name = k
                break

        if(not required_format_name in PREFERRED_QR_FORMAT_NAMES):
            raise RequestedContentTypeNotFound('No supported format for requested extension.')
    
        negotiated_format = PREFERRED_QR_IMAGE_FORMATS[PREFERRED_QR_FORMAT_NAMES.index(required_format_name)]

    elif(REQUIRED_MIME != ''):
        if(not REQUIRED_MIME in PREFERRED_QR_IMAGE_MIMES):
            raise RequestedContentTypeNotFound('No supported format for requested content-type.')
    
        negotiated_format = PREFERRED_QR_IMAGE_FORMATS[PREFERRED_QR_IMAGE_MIMES.index(REQUIRED_MIME)]
    
    else:
        negotiated_mime = request.get_preferred_type(PREFERRED_QR_IMAGE_MIMES)
        if(not negotiated_mime in PREFERRED_QR_IMAGE_MIMES):
            raise NoAcceptableContentType("Unable to negotiate an acceptable content type.")
        
        negotiated_format = PREFERRED_QR_IMAGE_FORMATS[PREFERRED_QR_IMAGE_MIMES.index(negotiated_mime)]

    SUPPORTED_FORMAT_ENTRY = STATE.supported_pil_image_formats[negotiated_format['f']]
    if not SUPPORTED_FORMAT_ENTRY['available']:
        raise  NoAcceptableContentType(f"A format was selected [{negotiated_format['f']}], but it's not supported.")


    FILENAME = f"qrcode_{boxSize}_{LINK_HASH}{negotiated_format['e']}"
    local_file_path = os.path.join(local_file_dir, FILENAME)

    if os.path.isfile(local_file_path) == False:
        IMG = generate_qr_code(link, boxSize, negotiated_format['c'])
        match(negotiated_format['f']):
            case 'SVG':
                IMG.save(local_file_path) # type: ignore
            case _:
                options = {
                    'quality' : 95,
                   'lossless' : True,
                     'effort' : 9
                }
                if IMG.mode not in negotiated_format['d']: # type: ignore
                    IMG = IMG.convert(negotiated_format['d'][0]) # type: ignore
                IMG.save(local_file_path,format=negotiated_format['f'], **options) # type: ignore

    return (f"{settings.MEDIA_URL}{FILE_DIR}{FILENAME}", local_file_path)

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

def endOfYear(y : int):
    return endOfMonth(y,12)

def endOfMonth(y : int, m : int):
    if m >= 12:
        m = 1
        y = y + 1
        d = datetime.datetime(y,m,1,tzinfo=pytz.utc) - datetime.timedelta(days=1)
    else:
        d = datetime.datetime(y, m + 1, 1,tzinfo=pytz.utc) - datetime.timedelta(days=1)
    return d.replace(hour=23, minute=59, second=59, microsecond=999999)

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

    #-----------------------------------------

    if not dte:
        if year:
            if month:
                if day:
                    dte = datetime.datetime(year, month, day, 0, 0, 0, 0, pytz.utc)
                else:
                    dte_start = datetime.datetime(year, month, 1, 0 ,0, 0, 0, pytz.utc)
                    dte_end = endOfMonth(year, month)
            else:
                dte_start = datetime.datetime(year, 1, 1, 0 ,0, 0, 0, pytz.utc)
                dte_end = endOfYear(year)
    #-----------------------------------------

    if not dte_start:
        if year_start:
            if month_start:
                if day_start:
                    dte_start = datetime.datetime(year_start, month_start, day_start, 0, 0, 0, 0, pytz.utc)
                else:
                    dte_start = datetime.datetime(year_start, month_start, 1, 0, 0, 0, 0, pytz.utc)
            else:
                dte_start = datetime.datetime(year_start, 1, 1, 0, 0, 0, 0, pytz.utc)
    #-----------------------------------------

    if not dte_end:
        if year_end:
            if month_end:
                if day_end:
                    dte_end = datetime.datetime(year_end,month_end,day_end,23,59,50,999999, pytz.utc)
                else:
                    dte_end = endOfMonth(year_end,month_end)
            else:
                dte_end = endOfYear(year_end)
    #-----------------------------------------
    
    if((dte_start and dte_end) and (dte_start.date() == dte_end.date())):
        dte = dte_start
        dte_start = None
        dte_end = None


    if(dte_start or dte_end):
        if dte_start:
            present = present.filter(dte_date__date__gte=dte_start)

        if dte_end:
            present = present.filter(dte_date__date__lte=dte_end)

    elif(dte):
        present = present.filter(dte_date__date=dte)

    #--------

    if(student):
        present = present.filter(student=student)

    present = present.annotate(
            dte_date_date=TruncDate('dte_date'),
            dte_date_time=TruncTime('dte_date')
        ).order_by('dte_date_date', 'className__moduleName__s_moduleName', 'className__s_className', 'dte_date_time')

    return (present, cls, mod)
    