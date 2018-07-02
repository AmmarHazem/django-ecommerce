from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import stripe
from .models import BillingProfile, Card

PUB_KEY = getattr(settings, 'PUB_KEY', 'pk_test_VXDkskRFeTYvKtSLl5dNMmkf')
stripe.api_key = getattr(settings, 'STRIPE_API_KEY', 'sk_test_hL3k70HLspNvoyq8HqTSpGPC')


def payment(request):
    return render(request, 'billing/payment.html', {'publish_key' : PUB_KEY})


def payment_create(request):
    if request.method == 'POST' and request.is_ajax():
        bp, created = BillingProfile.objects.new_or_get(request)
        token = request.POST.get('token')
        if token is not None:
            card = Card.objects.add_new(bp, token)
            print(card)
        return JsonResponse({'message' : 'DONE'})
    return HttpResponse('error', status = 401)


def add_billing_method(request):
    if request.method == 'GET':
        return render(request, 'paymentmethod.html', {'pub_key' : PUB_KEY})
