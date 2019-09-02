from django.conf.urls import url
from .views import *

app_name = 'contact'

urlpatterns = [

    url(r'^$', Contact.as_view(), name = 'contact')
]