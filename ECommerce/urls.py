"""ECommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView
from .views import *
from orders.views import Library


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', Home.as_view(), name = 'home'),
    url(r'^cart/', include('cart.urls')),
    # redirects the url accounts/ to account/
    # url(r'^accounts/', RedirectView.as_view(url = '/account')),
    url(r'^account/', include('accounts.urls', namespace = 'accounts')),
    url(r'^account/', include('accounts.passwords.urls', namespace = 'password')),
    url(r'^settings/', include('markting.urls')),
    url(r'^library/$', Library.as_view(), name = 'library'),
    url(r'^orders/', include('orders.urls')),
    url(r'^billing/', include('billing.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^address/', include('address.urls')),
    url(r'^products/', include('product.urls')),
    url(r'^search/', include('search.urls')),
    url(r'^contact/', include('contact.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
