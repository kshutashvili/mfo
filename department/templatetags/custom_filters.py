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


@register.filter
def get_icon_class_social_net(social_net):
    try:
        if 'facebook' in social_net.link:
            return 'facebook'
        elif 'telegram' in social_net.link:
            return 'telegram'
        else:
            return ''
    except:
        return ''


@register.filter
def get_icon_class_phone_number(phone):
    kyivstar = ['67', '68', '96', '97', '98']
    vodafone = ['5', '66', '95', '99']
    lifecell = ['63', '93', '73']
    try:
        tmp = phone.number.split('0')
        if tmp[1][:2] in lifecell:
            return 'lifecell'
        elif tmp[1][:2] in vodafone:
            return 'vodafone'
        elif tmp[1][:2] in kyivstar:
            return 'kyivstar'
        else:
            return ''
    except:
        return ''

