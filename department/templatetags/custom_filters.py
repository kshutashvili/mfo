from django import template

register = template.Library()


@register.filter
def get_city(department):
    try:
        return department.address.split(',')[-2].strip()
    except:
        return None


@register.filter
def replace_comma_with_space(string):
    try:
        return str(string).replace(',',' ')
    except:
        return None


@register.filter
def get_few_words(string, number):
    try:
        result = ' '.join(str(string).split(' ')[:int(number)])
        result = ''.join([result, '...'])
        return result
    except:
        return None


@register.filter
def get_int_divide_plus_one(number, divider):
    try:
        return 1 + int(number)//int(divider)
    except:
        return None


@register.filter
def generate_paginate_iter(q_list, divider):
    try:
        pag = get_int_divide_plus_one(len(q_list), divider)
        result = [x for x in range(1, pag + 1)]
        return result
    except:
        return None

