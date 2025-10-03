from urllib.parse import urlparse
from django import template

register = template.Library()

@register.filter
def referer_path(request):
    ref = request.META.get('HTTP_REFERER', None)
    return urlparse(ref).path if ref else ''