from django import template

register = template.Library()

@register.filter
def get_attr_safe(obj, atr : str, default = None):
    if obj:
        return getattr(obj, atr, default)
    else:
        return default