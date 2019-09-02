from django.shortcuts import render
from django.views.generic import ListView
from product.models import Product



class ProductSearch(ListView):
    model = Product
    template_name = 'products.html'
    context_object_name = 'products'

    def get_queryset(self, *args, **kwargs):
        products = Product.objects.search(self.request.GET.get('q', ''))
        return products
