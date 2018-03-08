from content.models import MenuFooterBlock
from communication.models import SocialNet, PhoneNumber, HotLinePhone

def menu_processor(requset):
    menu_footer = MenuFooterBlock.objects.order_by('order')
    phones = PhoneNumber.objects.all()
    social_nets = SocialNet.objects.all()
    hot_line_phone = HotLinePhone.get_solo()
    return {'menu_footer': menu_footer,
            'social_nets':social_nets,
            'phones':phones,
            'hot_line_phone':hot_line_phone}

