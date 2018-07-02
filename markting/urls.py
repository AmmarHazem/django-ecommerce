from django.conf.urls import url
from .views import MarktingPrefrenceUpdateView, MailchimpWebhook

app_name = 'markting'

urlpatterns = [
    url(r'^emails/$', MarktingPrefrenceUpdateView.as_view(), name = 'prefrence'),
    url(r'^webhook/$', MailchimpWebhook.as_view(), name = 'mailchimp-webhook'),
]