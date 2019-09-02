from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView, View
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Avg
import datetime
import random

from orders.models import Order

class SalesAjax(View):
    def get(self, request):
        data = {}
        if request.is_ajax() and request.user.is_staff:
            if request.GET.get('type') == 'week':
                qs = Order.objects.all()
                days = 14
                start_date = timezone.now().today() - datetime.timedelta(days = days - 1)
                last_week_orders = qs.by_range(start_date)
                datetime_list = []
                labels = []
                sales_items = []
                for x in range(days):
                    new_time = start_date + datetime.timedelta(days = x)
                    datetime_list.append(new_time)
                    labels.append(new_time.strftime('%a'))
                    sales_items.append(last_week_orders.by_range(start_date = start_date, end_date = new_time).count())
                data['labels'] = labels
                data['values'] = sales_items
        return JsonResponse(data)



class Sales(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/sales.html'

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            return render(self.request, '400.html')
        return super(Sales, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(Sales, self).get_context_data(*args, *kwargs)
        one_day = timezone.now() - datetime.timedelta(days = 1)
        last_two_weeks = timezone.now() - datetime.timedelta(days = 30)
        qs = Order.objects.all()
        last_day_orders = qs.by_range(start_date = one_day)
        last_two_weeks_orders = qs.by_range(start_date = last_two_weeks)
        context['qs'] = qs.by_date()
        context['recent_orders'] = qs
        context['recent_orders_total'] = context['recent_orders'].totals_data()
        context['recent_orders_cart_data'] = context['recent_orders'].cart_data()
        context['last_day_orders'] = last_day_orders
        context['last_two_weeks_orders'] = last_two_weeks_orders
        return context
