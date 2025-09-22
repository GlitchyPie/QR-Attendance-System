from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def jump_url(context, url : str):
    k = {}
    if context.get('class', None) != None:
        k['classId'] = context['class'].id
    elif context.get('classId', None) != None:
        k['classId'] = context['classId']
    elif context.get('module', None) != None:
        k['moduleId'] = context['module'].id
    elif context.get('moduleId', None) != None:
        k['moduleId'] = context['moduleId']
    
    if context.get('dte_year',None) != None:
        k['year'] = context['dte_year']

    if context.get('dte_month', None) != None:
        k['month'] = context['dte_month']

    if context.get('dte_day', None) != None:
        k['day'] = context['dte_day']

    return reverse(url, kwargs=k)
