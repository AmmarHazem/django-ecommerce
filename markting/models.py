from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class MarktingPrefrence(models.Model):
    user = models.OneToOneField(User)
    subscribed = models.BooleanField(default = True)
    mailchimp_msg = models.TextField(blank = True)
    mailchimp_subscribed = models.NullBooleanField(null = True, blank = True)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    def __str__(self):
        return str(self.user)