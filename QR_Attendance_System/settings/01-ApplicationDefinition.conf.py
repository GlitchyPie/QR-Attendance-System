# Application definition
# type: ignore

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'FacultyView',
    'StudentView',
    'TemplateTags',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'QR_Attendance_System.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_settings_export.settings_export',
            ],
        },
    },
]

WSGI_APPLICATION = 'QR_Attendance_System.wsgi.application'

LOGOUT_URL = '/faculty/logout/'
LOGIN_URL = '/faculty/login/'
LOGIN_REDIRECT_URL = '/'   # where to go after successful login
LOGOUT_REDIRECT_URL = '/'  # where to go after logout

# Session expires in 60 minutes (3600 seconds)
SESSION_COOKIE_AGE = 3600 

# If True, session cookie is deleted when browser closes
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
