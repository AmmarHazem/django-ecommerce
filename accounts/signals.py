from django.dispatch import Signal, receiver
from django.db.models.signals import post_save
from .models import Guest
from billing.models import BillingProfile

user_logged_in = Signal(providing_args=['instance', 'request'])


@receiver(post_save, sender = Guest)
def save_cart(sender, instance, created, **kwargs):
    BillingProfile.objects.create(email = instance.email)