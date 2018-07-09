from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import Http404
from django.views.generic import ListView, DetailView
from .models import Order


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
