from django.contrib import admin
from .models import Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ('title', 'timestamp')
    fields = ('title', 'products')


admin.site.register(Tag, TagAdmin)
