from django.shortcuts import render, redirect
from django.views.generic import ListView, View
from django.conf import settings
from .models import Cart
from accounts.models import Guest
from orders.models import Order
from product.models import Product
from accounts.forms import GuestForm
from accounts.forms import LoginForm
from billing.models import BillingProfile
from address.forms import AddressForm
from address.models import Address
from django.http import JsonResponse

STRIPE_PUB_KEY = getattr(settings, 'PUB_KEY', 'pk_test_VXDkskRFeTYvKtSLl5dNMmkf')

class Cart_Home(ListView):

    model = Cart
    template_name = 'cart/cart.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super(Cart_Home, self).get_context_data(**kwargs)
        cart, created = Cart.objects.new_or_get(self.request)
        #shipping = cart.order_set.all().first().shipping_total
        qs = cart.order_set.all()
        if not qs.exists():
            order = Order.objects.create(cart = cart)
            shipping = order.shipping_total
        else:
            shipping = qs.first().shipping_total
        context['products'] = cart.products.all()
        context['total'] = cart.order_set.all().first().total
        context['shipping'] = shipping
        return context


class CartRefresh(View):
    def get(self, request):
        cart, created = Cart.objects.new_or_get(request)
        products = [{'name' : p.name, 'price' : p.price, 'url' : p.get_absolute_url(), 'slug' : p.slug} for p in cart.products.all()]
        return JsonResponse({'products' : products, 'total' : cart.total})


class UpdateCart(View):
    def get(self, request):
        return redirect('cart:home')

    def post(self, request):
        form = request.POST
        slug = form.get('slug')
        next = form.get('next')
        if not slug:
            return render(request, 'error.html')
        p = Product.objects.get(slug = slug)
        cart, created = Cart.objects.new_or_get(request)
        if p in cart.products.all():
            cart.products.remove(p)
            added = False
        else:
            cart.products.add(p)
            added = True
        request.session['n'] = cart.products.count()
        if request.is_ajax():
            return JsonResponse({'added' : added, 'n' : cart.products.count()})
        if next == '0':
            return redirect(p.get_absolute_url())
        return redirect('cart:home')


class Checkout(View):

    def set_billing_data(self, order):
        billing_id = self.request.session.get('billing_id')
        shipping_id = self.request.session.get('shipping_id')
        if billing_id:
            order.billing_address = Address.objects.get(id = billing_id)
            del self.request.session['billing_id']
        if shipping_id:
            order.shipping_address = Address.objects.get(id = shipping_id)
            del self.request.session['shipping_id']
        if billing_id or shipping_id:
            order.save()


    # get all the addresses associated whith the user's billing profile
    def get_addr(self, bp = None):
        address_qs = Address.objects.filter(bp = bp)
        return address_qs

    def get(self, request):
        user_email = request.session.get('user_email')
        cart, created = Cart.objects.new_or_get(request)
        if created:
            return redirect('cart:home')
        login_form = LoginForm(request)
        guest_form = GuestForm()
        shipping_form = AddressForm()
        shipping_address_required = not cart.is_digital

        if not request.user.is_authenticated() and not user_email:
            bp, created = BillingProfile.objects.new_or_get(request)
            # addresses = self.get_addr(bp)
            order, created = Order.objects.new_or_get(bp, cart)
            self.set_billing_data(order)
            return render(request, 'checkout.html', {'login_form' : login_form, 'guest_form' : guest_form, 'publish_key' : STRIPE_PUB_KEY})

        elif user_email and not request.user.is_authenticated():
            bp, created = BillingProfile.objects.new_or_get(request)
            has_card = bp.has_card
            addresses = self.get_addr(bp)
            order, created = Order.objects.new_or_get(bp, cart)
            self.set_billing_data(order)
            return render(request, 'checkout.html', {'order' : order, 'billing_profile' : bp, 'shipping_form' : shipping_form, 'addresses' : addresses, 'has_card' : has_card, 'publish_key' : STRIPE_PUB_KEY, 'shipping_address_required' : shipping_address_required})

        elif request.user.is_authenticated():
            bp, created = BillingProfile.objects.new_or_get(request)
            has_card = bp.has_card
            addresses = self.get_addr(bp)
            order, created = Order.objects.new_or_get(bp, cart)
            self.set_billing_data(order)
            return render(request, 'checkout.html', {'order' : order, 'billing_profile' : bp, 'shipping_form' : shipping_form, 'addresses' : addresses, 'has_card' : has_card, 'publish_key' : STRIPE_PUB_KEY, 'shipping_address_required' : shipping_address_required})

    def post(self, request):
        bp, created = BillingProfile.objects.new_or_get(request)
        cart, created = Cart.objects.new_or_get(request)
        order, created = Order.objects.new_or_get(bp, cart)
        is_done = order.check_done
        if is_done:
            did_charge = bp.create_charge(order)
            if did_charge:
                order.mark_paid()
                if not request.user.is_authenticated():
                    request.session.flush()
                if not bp.user:
                    bp.set_cards_inactive()
                for p in cart.products.all():
                    cart.products.remove(p)
                return render(request, 'success.html')
            else:
                print('did_charge: {}'.format(did_charge))


class CheckoutSuccess(View):
    def get(self, request):
        cart, created = Cart.objects.new_or_get(request)
        for p in cart.products.all():
            cart.products.remove(p)
        request.session['n'] = 0
        return render(request, 'success.html')


class AddAll(View):
    def post(self, request):
        cart, created = Cart.objects.new_or_get(request)
        p = Product.objects.all()
        request.session['n'] = p.count()
        for product in p:
            if product not in cart.products.all():
                cart.products.add(product)
        return JsonResponse({'next' : '/cart/', 'n' : p.count()})

    def get(self, request):
        return redirect('product:list')