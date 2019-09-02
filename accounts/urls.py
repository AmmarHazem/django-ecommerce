from django.conf.urls import url
from .views import *
from product.views import UserProductHistoryList

# app_name = 'accounts'

urlpatterns = [
    url(r'^$', AccountHome.as_view(), name = 'home'),
    url(r'^login/$', Login.as_view(), name = 'login'),
    url(r'^signup/$', SignUp.as_view(), name = 'signup'),
    url(r'^edit-credentials/$', UserUpdate.as_view(), name = 'edit-credentials'),
    url(r'^products-history/$', UserProductHistoryList.as_view(), name = 'history'),
    url(r'^email/confirm/(?P<key>[0-9A-Za-z]+)/$', ConfirmEmail.as_view(), name = 'confirm-email'),
    url(r'^guest/$', Guest.as_view(), name = 'guest'),
]