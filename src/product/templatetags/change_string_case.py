from atexit import register
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

# @register.filter(is_safe=True)
# def cut(value, arg):
#     """Removes all values of arg from the given string"""
#     return value.replace(value, arg)


@register.filter(is_safe=True)
# @stringfilter
def cut(value, arg):
    """Removes all values of arg from the given string"""
    if arg:
        print("Arg :",arg)
        return True
    else:
        return False


@register.filter(is_safe=True)
def add_xx(value):
    return '%sxx' % value    

# register.filter('cut', cut)