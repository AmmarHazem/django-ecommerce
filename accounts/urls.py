from django.conf.urls import url
from .views import *

app_name = 'accounts'

urlpatterns = [
    url(r'^login/$', Login.as_view(), name = 'login'),
    url(r'^signup/$', SignUp.as_view(), name = 'signup'),
]