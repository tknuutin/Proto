'''
Created on 29.6.2012

@author: Tarmo
'''

from django import template
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from itertools import chain

register = template.Library()


def active_navlink(request, pattern):
    import re
    if re.search(pattern, request.path):
        return 'navlink_current'
    return 'navlink'

def format_for_design(value, user_id):
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        raise template.TemplateSyntaxError("User ID given does not exist.")
    return [x for x in value if x.is_editable(user)]

register.filter("format_for_design", format_for_design)
register.simple_tag(active_navlink)


