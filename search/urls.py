from django.conf.urls import url
from .views import *


app_name = 'search'

urlpatterns = [

    url(r'^', ProductSearch.as_view(), name = 'product'),
]