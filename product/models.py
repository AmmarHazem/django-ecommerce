from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy, reverse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.db.models import Q
from ECommerce.utils import get_filename

class ProductManager(models.Manager):

    def get_by_id(self, id):
        return self.get_queryset().filter(id = id) #self.get_query_set() == Product.objects

    def search(self, q):
        # to filter using more than on query 
        lookup = Q(name__icontains = q) | Q(description__icontains = q) | Q(price__icontains = q) | Q(tag__title__icontains = q)
        return self.get_queryset().filter(lookup).distinct()


class Product(models.Model):
    name = models.CharField(max_length = 50)
    description = models.TextField()
    price = models.DecimalField(default = 0.00, max_digits = 6, decimal_places = 2)
    image = models.ImageField(upload_to = '', null = True, blank = True)
    slug = models.CharField(max_length = 50, null = True, blank = True)
    is_digital = models.BooleanField(default = False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    objects = ProductManager()

    def get_absolute_url(self):
        return reverse_lazy('product:detail', args = (self.slug,))

    def get_downloads(self):
        return self.productfile_set.all()

    def __str__(self):
        return self.name

    class Mete:
        ordering = ('name',)
        permissions = (('can_view_products', 'Can view products'),)


def product_file_loc(instance, filename):
    if not instance.product.slug:
        instance.slug = slugify(instance.name)
    location = 'products/{}/'.format(instance.product.slug)
    return location + filename


class ProductFile(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    file = models.FileField(upload_to = product_file_loc, storage = FileSystemStorage(location = settings.PROTECTED_ROOT))
    free = models.BooleanField(default = False)
    user_required = models.BooleanField(default = False)

    def __str__(self):
        return str(self.file.name)

    def get_download_url(self):
        return reverse('product:download', kwargs = {'slug' : self.product.slug, 'pk' : self.id})

    @property
    def name(self):
        return get_filename(self.file.name)

    def get_default_url(self):
        return self.product.get_absolute_url()

