from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import AddressForm
from billing.models import BillingProfile
from .models import Address
from orders.models import Order

class CheckoutAddress(View):
    def get(self, request):
        return redirect('cart:checkout')

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            bp, created = BillingProfile.objects.new_or_get(request)
            address = form.save(commit = False)
            address.bp = bp
            address_type = request.POST.get('address_type', 'shipping')
            address.address_type = address_type
            address.save()
            request.session[address_type + '_id'] = address.id
            return redirect('cart:checkout')
        return redirect('cart:home')


class PrevAddress(View):
    def get(self, request):
        return redirect('cart:home')

    def post(self, request):
        if request.user.is_authenticated():
            bp, created = BillingProfile.objects.new_or_get(request)
            address_type = request.POST.get('address_type', 'shipping')
            shipping_address = request.POST.get('shipping_address')
            next = request.POST.get('next', 'cart:checkout')
            if shipping_address:
                qs = Address.objects.filter(bp = bp, id = shipping_address)
                if qs.exists():
                    bp, created = BillingProfile.objects.new_or_get(request)
                    address = qs.last()
                    address.bp = bp
                    address_type = request.POST.get('address_type', 'shipping')
                    address.address_type = address_type
                    address.save()
                    order_id = request.POST.get('order_id')
                    order = Order.objects.get(id = order_id)
                    if address_type == 'shipping':
                        order.shipping_address = address
                        order.save()
                    else:
                        order.billing_address = address
                        order.save()
                    return redirect(next)
        return redirect('cart:home')
