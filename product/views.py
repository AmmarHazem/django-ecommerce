from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Product
from cart.models import Cart
from analytics.mixins import ObjectViewMixin

class ProductList(ListView):
    model = Product
    template_name = 'products.html'
    context_object_name = 'products'


class UserProductHistoryList(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products.html'
    context_object_name = 'products'

    def get_queryset(self, *args, **kwargs):
        request = self.request
        products_viewed = request.user.objectviewed_set.by_model(Product)
        products_viewed_ids = [p.object_id for p in products_viewed]
        return Product.objects.filter(pk__in = products_viewed_ids)


class ProductDetail(ObjectViewMixin, DetailView):

    model = Product
    context_object_name = 'product'
    template_name = 'product.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetail, self).get_context_data(*args, **kwargs)
        cart, created = Cart.objects.new_or_get(self.request)
        context['in_cart'] = (self.object in cart.products.all())
        return context
