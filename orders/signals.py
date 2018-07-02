from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from .models import Order
from ECommerce.utils import unique_order_id
from billing.models import BillingProfile

# receiver function to generate random order id
@receiver(post_save, sender = Order)
def post_save_order(sender, instance, created, **kwargs):
    if created:
        print('order created')
        instance.order_id = unique_order_id(instance)
        print('order id saved')
        instance.status = 'created'
        instance.update_total()
        print('total updated')

@receiver(pre_save, sender = Order)
def pre_save_order(sender, instance, **kwargs):
    qs = Order.objects.filter(cart = instance.cart).exclude(billing_profile = instance.billing_profile)
    if qs.exists():
        qs.update(active = False)
