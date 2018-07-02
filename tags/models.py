from django.db import models
from product.models import Product
from django.template.defaultfilters import slugify


class Tag(models.Model):
    title = models.CharField(max_length = 100, unique = True)
    slug = models.CharField(max_length = 100)
    timestamp = models.DateTimeField(auto_now_add = True)
    products = models.ManyToManyField(Product, blank = True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Tag, self).save(*args, **kwargs)

