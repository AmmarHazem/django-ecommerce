from django.contrib import admin
from .models import Cart, Guest


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'timestamp', 'updated_at')
    fields = ('user', 'products', 'total')


admin.site.register(Cart, CartAdmin)
admin.site.register(Guest)
