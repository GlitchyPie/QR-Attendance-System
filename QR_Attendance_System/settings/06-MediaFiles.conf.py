# Media files
# https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-MEDIA_ROOT

if DEBUG:
    MEDIA_ROOT = f"{BASE_DIR}/media"
else:
    MEDIA_ROOT = ""
    MEDIA_URL = ""