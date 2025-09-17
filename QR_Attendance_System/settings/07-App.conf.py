import pytz
from datetime import datetime

INSTITUTION_NAME = "Centre For Alternative Technology"
PORTAL_TITLE = "Attendance Portal"

COPYRIGHT_APP_NAME = "QR Attendance System"

COPYRIGHT_ORG_NAME = "Centre For Alternative Technology"
COPYRIGHT_YEAR = datetime.now(pytz.utc).year

SETTINGS_EXPORT = [
    'INSTITUTION_NAME',
    'PORTAL_TITLE',
    'LANGUAGE_CODE',
    'COPYRIGHT_APP_NAME',
    'COPYRIGHT_ORG_NAME',
    'COPYRIGHT_YEAR',
]