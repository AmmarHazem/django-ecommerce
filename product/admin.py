from django.contrib import admin
from .models import Product
from django.contrib.auth.models import Permission

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price')
    fields = ('name', 'description', 'price', 'image')

admin.site.register(Product, ProductAdmin)
admin.site.register(Permission)
