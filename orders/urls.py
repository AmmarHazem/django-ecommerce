from django.conf.urls import url
from .views import *

app_name = 'orders'

urlpatterns = [
    url(r'^$', OrdersList.as_view(), name = 'list'),
    url(r'^endpoint/verify/ownership/$', VerifyOwnership.as_view(), name = 'ownership'),
    url(r'^(?P<order_id>[0-9A-Za-z]+)/$', OrderDetail.as_view(), name = 'detail'),
]