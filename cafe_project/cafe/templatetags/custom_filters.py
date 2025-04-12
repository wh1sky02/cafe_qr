
from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='sum')
def sum_filter(queryset, field_name):
    if not queryset:
        return 0
    return sum(getattr(item, field_name) for item in queryset)
