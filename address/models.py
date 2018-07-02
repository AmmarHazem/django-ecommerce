from django.db import models
from billing.models import BillingProfile

ADDRESS_TYPE = (('billing', 'Billing'), ('shipping', 'Shipping'))

class Address(models.Model):
    bp = models.ForeignKey(BillingProfile)
    address_type = models.CharField(max_length = 120, choices = ADDRESS_TYPE)
    address_line1 = models.CharField(max_length = 120)
    address_line2 = models.CharField(max_length = 120, blank = True)
    city = models.CharField(max_length = 120)
    state = models.CharField(max_length = 120)
    country = models.CharField(max_length = 120, default = 'Egypt')

    def __str__(self):
        return str(self.bp)

    def get_address(self):
        return '{line1} - {line2} - {city} - {state} - {country}'.format(line1 = self.address_line1, line2 = self.address_line2, city = self.city, state = self.state, country = self.country)

