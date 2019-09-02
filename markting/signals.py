from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.conf import settings
from .models import MarktingPrefrence
from .utils import Mailchimp


User = settings.AUTH_USER_MODEL


# @receiver(post_save, sender = User)
# def post_save_user(sender, instance, created, *args, **kwargs):
#     if created:
#         MarktingPrefrence.objects.create(user = instance)


@receiver(post_save, sender = MarktingPrefrence)
def post_save_marktingpref(sender, instance, created, *args, **kwargs):
    if created:
        status, response_data = Mailchimp().subscribe(instance.user.email)
        print(status, response_data)


@receiver(pre_save, sender = MarktingPrefrence)
def marktingpref_update_reciever(sender, instance, *args, **kwargs):
    if instance.subscribed != instance.mailchimp_subscribed:
        if instance.subscribed:
            status, response_data = Mailchimp().subscribe(instance.user.email)
        else:
            status, response_data = Mailchimp().unsubscribe(instance.user.email)

        if response_data['status'] == 'subscribed':
            instance.subscribed = True
            instance.mailchimp_subscribed = True
            instance.mailchimp_msg = response_data
        else:
            instance.subscribed = False
            instance.mailchimp_subscribed = False
            instance.mailchimp_msg = response_data