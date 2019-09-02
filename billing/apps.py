from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class BillingConfig(AppConfig):
    name = 'billing'
    def ready(self):
        import billing.signals