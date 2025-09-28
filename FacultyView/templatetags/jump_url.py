from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def jump_url(context, url : str, **kwargs):
    k = kwargs or {}
    if context.get('class', None) != None:
        k['classId'] = context['class'].id
    elif context.get('classId', None) != None:
        k['classId'] = context['classId']
    elif context.get('module', None) != None:
        k['moduleId'] = context['module'].id
    elif context.get('moduleId', None) != None:
        k['moduleId'] = context['moduleId']
    
    #---
    if context.get('dte_year',None) != None:
        k['year'] = context['dte_year']

    if context.get('dte_month', None) != None:
        k['month'] = context['dte_month']

    if context.get('dte_day', None) != None:
        k['day'] = context['dte_day']
    
    #---
    if context.get('dte_start_year',None) != None:
        k['year_start'] = context['dte_start_year']

    if context.get('dte_start_month',None) != None:
        k['month_start'] = context['dte_start_month']

    if context.get('dte_start_day',None) != None:
        k['day_start'] = context['dte_start_day']

    #---
    if context.get('dte_end_year',None) != None:
        k['year_end'] = context['dte_end_year']

    if context.get('dte_end_month',None) != None:
        k['month_end'] = context['dte_end_month']

    if context.get('dte_end_day',None) != None:
        k['day_end'] = context['dte_end_day']

    return reverse(url, kwargs=k)
