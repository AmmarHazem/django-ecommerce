from django.db import models
from django.db.models import Sum, Avg, Count
from django.urls import reverse
from django.utils import timezone
import datetime
from cart.models import Cart
from django.contrib.auth import get_user_model
from decimal import Decimal
from billing.models import BillingProfile
from address.models import Address
from product.models import Product

User = get_user_model()


class OrderQuerySet(models.query.QuerySet):

    def by_range(self, start_date, end_date = None):
        if end_date is None:
            return self.filter(updated__gte = start_date)
        return self.filter(updated__gte = start_date).filter(updated__lte = end_date)

    def by_date(self):
        now = timezone.now() - datetime.timedelta(days = 30)
        return self.filter(updated__month__gte = now.month)

    def totals_data(self):
        return self.aggregate(Sum('total'), Avg('total'))

    def cart_data(self):
        return self.aggregate(Sum('cart__products__price'), Avg('cart__products__price'), products = Count('cart__products'))

    def not_refunded(self):
        return self.exclude(status = 'refunded')

    def by_status(self, status = 'shipped'):
        return self.filter(status = status)

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
    updated = models.DateTimeField(auto_now = True)
    created = models.DateTimeField(auto_now_add = True)

    objects = OrderManager()

    class Meta:
        ordering = ('-updated', '-created')

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

    def update_total(self):
        cart_total = self.cart.total
        if cart_total == 0:
            self.total = 0
        else:
            self.total = Decimal(cart_total) + Decimal(self.shipping_total)
        self.save()

    def check_done(self):
        shipping_address_required = self.cart.is_digital
        shipping_done = False
        if shipping_address_required and self.shipping_address:
            shipping_done = True
        elif shipping_address_required and not self.shipping_address:
            shipping_done = False
        else:
            shipping_done = True
        billing_profile = self.billing_profile
        billing_address = self.billing_address
        total = self.total
        if billing_profile and billing_address and shipping_done and total:
            return True
        return False

    def update_purchases(self):
        for p in self.cart.products.all():
            obj, created = ProductPurchase.objects.get_or_create(order_id = self.order_id, product = p, billing_profile = self.billing_profile)
        return ProductPurchase.objects.filter(order_id = self.order_id).count()

    def mark_paid(self):
        if self.check_done():
            self.status = 'paid'
            self.update_purchases()
            self.save()
        return self.status


class ProductPurchaseQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(refunded = False)

    def digital(self):
        return self.filter(product__is_digital = True)

    def by_request(self, request):
        bp, created = BillingProfile.objects.new_or_get(request)
        return self.filter(billing_profile = bp)


class ProductPurchaseManager(models.Manager):
    def get_queryset(self):
        return ProductPurchaseQuerySet(self.model, using = self._db)

    def all(self):
        return self.get_queryset().filter(refunded = False)

    def library(self):
        return self.get_queryset().active().digital()

    def by_request(self, request):
        return self.get_queryset().by_request(request)

    def products_by_id(self, request):
        qs = self.by_request(request).digital()
        ids = [p.product.id for p in qs]
        return ids

    def products_by_request(self, request):
        ids = self.products_by_id(request)
        products = Product.objects.filter(id__in = ids)
        return products


class ProductPurchase(models.Model):
    order_id = models.CharField(max_length = 120, blank = True)
    billing_profile = models.ForeignKey(BillingProfile, blank = True, null = True, on_delete = models.SET_NULL)
    product = models.ForeignKey(Product, blank = True, null = True, on_delete = models.SET_NULL)
    refunded = models.BooleanField(default = False)
    updated = models.DateTimeField(auto_now= True)
    created = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.product.name

    objects = ProductPurchaseManager()
