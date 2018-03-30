from django.db.models.signals import post_save, pre_save
from communication.models import UserQuestion, QuestionConfig, QuestionComment
from django.dispatch import receiver


@receiver(pre_save, sender=UserQuestion)
def comment_add(sender, instance, **kwargs):
    if instance.is_closed and not instance.end_message:
        content = QuestionConfig.get_solo().message
        message = QuestionComment.objects.filter(content=content).first()
        if not message:
            message = QuestionComment.objects.create(content=content, is_admin=True)
        instance.end_message = message
        instance.end_message.save()
    elif instance.end_message:
        instance.end_message = None

    if instance.is_read == 'force read':
        instance.is_read = 'read'
    elif instance.comments.last() and instance.comments.last().is_admin or instance.end_message:
        instance.is_read = '!read'


#@receiver(pre_save, sender=UserQuestion)
#def set_is_read_field(sender, **kwargs):
#    instance = kwargs['instance']
#    if instance.comments.last() and instance.comments.last().is_admin:
#        instance.is_read = False
#        instance.save()
#    elif instance.comments.last() and not instance.comments.last().is_admin:
#        instance.is_read = True

