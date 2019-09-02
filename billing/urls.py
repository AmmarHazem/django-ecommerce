from django.conf.urls import url
from .views import *

app_name = 'billing'

urlpatterns = [
    url(r'^payment/', payment, name = 'payment'),
    url(r'^create/', payment_create, name = 'create'),
    url(r'^add-payment-method/', add_billing_method, name = 'add-method'),
]