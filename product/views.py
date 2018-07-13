from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, View
from django.http import Http404, HttpResponse
from django.conf import settings

from mimetypes import guess_type
from wsgiref.util import FileWrapper
import os

from .models import Product, ProductFile
from orders.models import ProductPurchase
from cart.models import Cart
from analytics.mixins import ObjectViewMixin

# Download the media file
class ProductDownload(View):
    def get(self, request, slug, pk):
        user = request.user
        file_ = ProductFile.objects.filter(pk = pk, product__slug = slug)
        if not file_.count() == 1:
            return Http404('File not found')
        file_ = file_.first()

        can_download = True
        free = True
        if file_.user_required and not user.is_authenticated():
            can_download = False
        if not file_.free:
            products = ProductPurchase.objects.products_by_request(request)
            if not file_.product in products:
                free = False
        if not can_download or not free:
            if not can_download:
                messages.error(request, 'You have to sign up to download this product.')
                return redirect('login')
            messages.error(request, 'You have to purchase this product to download it.')
            return redirect(file_.get_default_url())

        file_root = settings.PROTECTED_ROOT
        file_path = file_.file.path
        path = os.path.join(file_root, file_path)
        with open(file_path, 'rb') as f:
            # FileWrapper converts a file like object to an iterator
            wrapper = FileWrapper(f)
            mimetype = 'application/force-download'
            # guss the mime type of the file
            gussed_type = guess_type(file_path)[0]
            if gussed_type:
                mimetype = gussed_type
            response = HttpResponse(wrapper, content_type = mimetype)
            response['Content-Disposition'] = 'attachment;filename=%s' % (file_.name)
            response['X-SendFile'] = str(file_.name)
            return response
        return HttpResponse(file_.get_download_url())

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
