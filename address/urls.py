from django.conf.urls import url
from .views import *

app_name = 'address'

urlpatterns = [

    url(r'^checkout/address$', PrevAddress.as_view(), name = 'address-reuse'),
    url(r'^checkout/$', CheckoutAddress.as_view(), name = 'checkout'),
]