from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def export_date_type(context):
    y = context.get('dte_year', None)
    m = context.get('dte_month', None)
    d = context.get('dte_day', None)

    ys = context.get('dte_start_year', None)
    ms = context.get('dte_start_month', None)
    ds = context.get('dte_start_day', None)

    ye = context.get('dte_end_year', None)
    me = context.get('dte_end_month', None)
    de = context.get('dte_end_day', None)

    if(y and m and d):
        return 1
    elif (ys or ms or ds or ye or me or de):
        return 2
    else:
        return 3