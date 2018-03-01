from django import template

register = template.Library()


@register.filter
def get_city(department):
    try:
        return department.address.split(',')[-2].strip()
    except:
        return None

