from django.conf.urls import url
from .views import *

app_name = 'cart'

urlpatterns = [

    url(r'^$', Cart_Home.as_view(), name = 'home'),
    # url(r'^add/$', Add_Product.as_view(), name = 'add'),
    # url(r'^remove/$', Remove_Product.as_view(), name = 'remove'),
    url(r'^update/$', UpdateCart.as_view(), name = 'update'),
    url(r'^add-all/$', AddAll.as_view(), name = 'add-all'),
    url(r'^api/$', CartRefresh.as_view(), name = 'api'),
    url(r'^checkout/$', Checkout.as_view(), name = 'checkout'),
    url(r'^checkout/success$', CheckoutSuccess.as_view(), name = 'success'),
]