from django.db import models
from product.models import Product
from django.conf import settings

User = settings.AUTH_USER_MODEL

class CartManager(models.Manager):
    def new(self, user = None):
        return self.model.objects.create(user = user)

    def new_or_get(self, request):
        cart_user = request.session.get('user')
        if not cart_user:
            if not request.user.is_authenticated():
                cart = self.model.objects.new()
                request.session['user'] = str(cart.id)
                return cart, True
            qs = self.model.objects.filter(user = request.user)
            if qs.count() == 0:
                cart = self.model.objects.new(user = request.user)
                request.session['user'] = cart.user.email
                return cart, True
            else:
                request.session['user'] = qs.first().user.email
                return qs.first(), False
        else:
            if request.user.is_authenticated():
                qs = self.model.objects.filter(user = request.user)
                if qs.count() == 0:
                    cart = Cart.objects.new(request.user)
                    request.session['user'] = cart.user.email
                    return cart, True
                else:
                    return qs.first(), False
            else:
                qs = self.model.objects.filter(id = cart_user)
                if qs.count() == 0:
                    cart = Cart.objects.new()
                    request.session['user'] = str(cart.id)
                    return cart, True
                else:
                    return qs.first(), False


class Cart(models.Model):
    user = models.ForeignKey(User, null = True, blank = True)
    products = models.ManyToManyField(Product, blank = True)
    total = models.DecimalField(default = 0.00, max_digits = 6, decimal_places = 2)
    timestamp = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    objects = CartManager()

    def __str__(self):
        if self.user:
            return str(self.user.email)
        return str(self.id)

class Guest(models.Model):
    email = models.EmailField()
    active = models.BooleanField(default = True)
    created = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.email

