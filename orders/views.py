from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.views.generic import ListView, DetailView, View
from .models import Order, ProductPurchase


class OrdersList(LoginRequiredMixin, ListView):

    template_name = 'orders/order_list.html'

    def get_queryset(self):
        return Order.objects.by_request(self.request).not_created()


class OrderDetail(LoginRequiredMixin, DetailView):

    template_name = 'orders/order_detail.html'

    def get_object(self):
        orders = Order.objects.by_request(self.request).filter(order_id = self.kwargs.get('order_id'))
        if orders.count() == 1:
            return orders.first()
        return Http404


class Library(LoginRequiredMixin, ListView):
    template_name = 'orders/library.html'
    def get_queryset(self):
        products = ProductPurchase.objects.products_by_request(self.request)
        return products


class VerifyOwnership(LoginRequiredMixin, View):
    def get(self, request):
        if request.is_ajax():
            product_id = int(request.GET.get('id'))
            ownership_ids = ProductPurchase.objects.products_by_id(request)
            if product_id in ownership_ids:
                return JsonResponse({'owner' : True})
            return JsonResponse({'owner' : False})
        raise Http404('Not allowed')
