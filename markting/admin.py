from django.contrib import admin
from .models import MarktingPrefrence

class MarktingPrefrenceAdmin(admin.ModelAdmin):

    readonly_fields = ('mailchimp_msg', 'mailchimp_subscribed', 'created', 'updated')

    class Meta:
        model = MarktingPrefrence
        fields = ('user', 'subscribed', 'mailchimp_msg', 'mailchimp_subscribed', 'created', 'updated')


admin.site.register(MarktingPrefrence, MarktingPrefrenceAdmin)
