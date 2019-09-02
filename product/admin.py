from django.contrib import admin
from .models import Product, ProductFile
from django.contrib.auth.models import Permission


class ProductFileInline(admin.TabularInline):
    model = ProductFile
    extra  = 1


# the inlines attribute will only work if the model of the class in the list 
# have a foreign key to the model in the Meta class
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price')
    fields = ('name', 'description', 'price', 'is_digital', 'image')
    inlines = [ProductFileInline]
    class Meta:
        model = Product

admin.site.register(Product, ProductAdmin)
admin.site.register(Permission)
