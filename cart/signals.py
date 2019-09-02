from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, m2m_changed
from .models import Cart
from orders.models import Order
from billing.models import BillingProfile

@receiver(post_save, sender = Cart)
def save_cart(sender, instance, **kwargs):
    print('A new Cart saved')

@receiver(post_delete, sender = Cart)
def delete_cart(sender, instance, **kwargs):
    print('Cart deleted')

@receiver(m2m_changed, sender = Cart.products.through)
def cart_total(sender, instance, action, **kwargs):
    actions = ('post_add', 'post_remove', 'post_clear')
    if action in actions:
        total = 0
        for p in instance.products.all():
            total += p.price
        instance.total = total
        qs = instance.order_set.filter(cart = instance)
        if not qs.exists():
            order = Order.objects.create(cart = instance)
        else:
            order = qs.last()
        order.update_total()
        instance.save()


