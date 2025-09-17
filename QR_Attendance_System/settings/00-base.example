# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-%&4dfwaayogd!r)=ot3hi1ybepd=s9d%$gkcomne)rq-a&fnmq"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip = s.getsockname()[0]

ALLOWED_HOSTS = ["127.0.0.1", f"{ip}", "localhost"]