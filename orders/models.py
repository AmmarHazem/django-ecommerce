from django.db import models
from django.urls import reverse
from cart.models import Cart
from decimal import Decimal
from billing.models import BillingProfile
from address.models import Address


class OrderQuerySet(models.query.QuerySet):
    def by_request(self, request):
        bp, created = BillingProfile.objects.new_or_get(request)
        return self.filter(billing_profile = bp)

    def not_created(self):
        return self.exclude(status = 'created')


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using = self._db)

    def by_request(self, request):
        return self.get_queryset().by_request(request)

    def new_or_get(self, bp, cart):
        created = False
        order_qs = self.model.objects.filter(billing_profile = bp)
        if not order_qs.exists():
            order_qs = self.model.objects.filter(cart = cart, active = True, status = 'created')
        if not order_qs.exists():
            order = self.model.objects.create(billing_profile = bp, cart = cart)
            created = True
        else:
            order = order_qs.last()
            order_qs.exclude(order_id = order.order_id).update(active = False)
            created = False
        order.billing_profile = bp
        order.save()
        return order, created


class Order(models.Model):
    order_id = models.CharField(max_length = 120, blank = True)
    billing_profile = models.OneToOneField(BillingProfile, blank = True, null = True)
    shipping_address = models.ForeignKey(Address, null = True, blank = True, related_name = 'shipping_address')
    billing_address = models.ForeignKey(Address, null = True, blank = True, related_name = 'billing_address')
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE, null = True, blank = True)
    STATUS_CHOICES = (('created', 'Created'), ('paid', 'Paid'), ('shipped', 'Shipped'), ('refunded', 'Refunded'))
    status = models.CharField(max_length = 20, choices = STATUS_CHOICES)
    shipping_total = models.DecimalField(default = 5.99, max_digits = 6, decimal_places = 2)
    total = models.DecimalField(default = 0.00, max_digits = 6, decimal_places = 2)
    active = models.BooleanField(default = True)
    created = models.DateTimeField(auto_now_add = True)

    objects = OrderManager()

    class Meta:
        ordering = ('-created', 'order_id')

    def __str__(self):
        return self.order_id

    def get_absolute_url(self):
        return reverse('orders:detail', kwargs = {'order_id' : self.order_id})

    def get_shipping_status(self):
        if self.status == 'refunded':
            return 'Refunded'
        elif self.status == 'shipped':
            return 'Shipped'
        return 'Shipping Soon'
    
    class Meta:
        ordering = ('id',)

    def update_total(self):
        cart_total = self.cart.total
        if cart_total == 0:
            self.total = 0
        else:
            self.total = Decimal(cart_total) + Decimal(self.shipping_total)
        self.save()

    def check_done(self):
        bp = self.billing_profile
        ba = self.billing_address
        sa = self.shipping_address
        total = self.total
        if bp and ba and sa and total:
            return True
        return False

    def mark_paid(self):
        if self.check_done():
            self.status = 'paid'
            self.save()
        return self.status
