from django import template

register = template.Library()

@register.filter
def intersection(list1, list2):
    return set(list1).intersection(list2)