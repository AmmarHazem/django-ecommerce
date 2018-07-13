from django.conf.urls import url
from .views import *

app_name = 'product'

urlpatterns = [
    url(r'^(?P<slug>[-\w]+)/$', ProductDetail.as_view(), name = 'detail'),
    url(r'^(?P<slug>[-\w]+)/(?P<pk>\d+)/$', ProductDownload.as_view(), name = 'download'),
    url(r'^$', ProductList.as_view(), name = 'list'),
]