from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from .models import BillingProfile, Card
from django.contrib.auth.models import User, Group
import stripe

stripe.api_key = 'sk_test_hL3k70HLspNvoyq8HqTSpGPC'

@receiver(post_save, sender = User)
def create_billing_profile(sender, instance, created, *args, **kwargs):
    if created:
        profile, created = BillingProfile.objects.get_or_create(user = instance)
        group = Group.objects.get(name = 'View Products')
        group.user_set.add(instance)
        if instance.email:
            profile.email = instance.email
            profile.save()
        print('Billing Profile created')


@receiver(pre_save, sender = BillingProfile)
def pre_save_bp(sender, instance, *args, **kwargs):
    if not instance.customer_id and instance.email:
        print('API request send to stripe')
        customer = stripe.Customer.create(email = instance.email)
        print('\nCreated a customer')
        print('Response', customer, sep = '\n')
        instance.customer_id = customer.id


@receiver(post_save, sender = Card)
def post_save_card(sender, instance, created, *args, **kwargs):
    bp = instance.bp
    cards = Card.objects.filter(bp = bp).exclude(id = instance.id)
    cards.update(default = False)
