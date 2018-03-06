from content.models import MenuFooterBlock
from communication.models import SocialNet, PhoneNumber

def menu_processor(requset):
    menu_footer = MenuFooterBlock.objects.order_by('order')
    phones = PhoneNumber.objects.all()
    social_nets = SocialNet.objects.all()
    return {'menu_footer': menu_footer,
            'social_nets':social_nets,
            'phones':phones}

