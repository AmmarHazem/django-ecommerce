from django.db import models
from django.conf import settings
import stripe

User = settings.AUTH_USER_MODEL

PUB_KEY = 'pk_test_VXDkskRFeTYvKtSLl5dNMmkf'
stripe.api_key = 'sk_test_hL3k70HLspNvoyq8HqTSpGPC'

class BillingProfileManager(models.Manager):
    def new_or_get(self, request):
        user = request.user
        user_email = request.session.get('user_email')
        if user.is_authenticated():
            bp, created = self.model.objects.get_or_create(user = user, email = user.email)
        elif user_email:
            qs = BillingProfile.objects.exclude(active = False).filter(email = user_email)
            created = False
            if not qs.exists():
                bp = BillingProfile.objects.create(email = user_email)
                created = True
            else:
                bp = qs.latest('created')
                qs.exclude(id = bp.id).update(active = False)
        else:
            bp = BillingProfile.objects.create()
            created = True
        if created:
            try:
                bp.email = user.email or user_email or None
                bp.save()
            except AttributeError:
                bp.save()
        return bp, created


class BillingProfile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, null = True, blank = True)
    email = models.EmailField(blank = True)
    active = models.BooleanField(default = True)
    customer_id = models.CharField(max_length = 120, blank = True)
    updated = models.DateTimeField(auto_now = True)
    created = models.DateTimeField(auto_now_add = True)

    objects = BillingProfileManager()

    def __str__(self):
        if self.user:
            return self.user.email
        return str(self.id)

    def create_charge(self, order, card = None):
        return Charge.objects.do_charge(self, order, card)

    def get_cards(self):
        qs = self.card_set.filter(bp = self)
        return qs
    
    @property
    def has_card(self):
        qs = self.get_cards()
        return qs.exists()

    @property
    def default_card(self):
        return self.get_cards().filter(default = True, active = True).first() or False

    def set_cards_inactive(self):
        cards = self.get_cards()
        cards.update(active = False)
        return cards.filter(active = True).count()




class CardManager(models.Manager):
    def all(self):
        return self.model.objects.filter(active = True)
    def add_new(self, bp, token):
        if token:
            customer = stripe.Customer.retrieve(bp.customer_id)
            stripe_response = customer.sources.create(source = token)
            card = self.model(bp = bp, stripe_id = stripe_response.id, brand = stripe_response.brand, country = stripe_response.country, exp_month = stripe_response.exp_month, exp_year = stripe_response.exp_year, last_4 = stripe_response.last4)
            card.save()
            return card
        return None


class Card(models.Model):
    bp = models.ForeignKey(BillingProfile, on_delete = models.CASCADE)
    stripe_id = models.CharField(max_length = 100)
    brand = models.CharField(max_length = 50, blank = True)
    country = models.CharField(max_length = 10, blank = True)
    exp_month = models.IntegerField(blank = True, null = True)
    exp_year = models.IntegerField(blank = True, null = True)
    last_4 = models.CharField(max_length = 4, blank = True)
    default = models.BooleanField(default = True)
    active = models.BooleanField(default = True)
    created = models.DateTimeField(auto_now_add = True)

    objects = CardManager()

    def __str__(self):
        return '{} {}'.format(str(self.brand), self.last_4)


class ChargeManager(models.Manager):
    def do_charge(self, bp, order, card = None):
        charge = None
        if card is None:
            cards = bp.card_set.filter(default = True)
            card = cards.first()
            if cards.count() > 1:
                cards.exclude(id = card.id).update(default = False)
        
        charge_response = stripe.Charge.create(
                                amount = int(order.total * 100),
                                currency="usd",
                                source = card.stripe_id,
                                customer = bp.customer_id,
                                description="Charge for {}".format(bp.email),
                                metadata = {'order_id' : order.order_id}
                                )
        charge = self.model(bp = bp, stripe_id = charge_response.id, paid = charge_response.paid, refunded = charge_response.refunded, outcome = charge_response.outcome)
        charge.save()
        return charge.paid



class Charge(models.Model):
    bp = models.ForeignKey(BillingProfile, on_delete = models.CASCADE)
    stripe_id = models.CharField(max_length = 100)
    paid = models.BooleanField(default = False)
    refunded = models.BooleanField(default = False)
    outcome = models.TextField(blank = True)
    outcome_type = models.CharField(max_length = 120, blank = True)

    objects = ChargeManager()

    def __str__(self):
        return 'Charge: {}'.format(str(self.bp))

