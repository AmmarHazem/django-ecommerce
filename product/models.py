from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy, reverse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.db.models import Q
from ECommerce.aws.utils import ProtectedS3BotoStorage
from ECommerce.aws.download.utils import AWSDownload
from ECommerce.utils import get_filename

import os

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
    slug = instance.slug
    id_ = instance.id
    print(instance.id)
    if id_ is None:
        klass = instance.__class__
        qs = klass.objects.order_by('-id')
        if qs.exists():
            id_ = qs.first().id + 1
        else:
            id_ = 0
    if not slug:
        instance.slug = slugify(instance.name)
    location = 'products/{}/'.format(instance.product.slug)
    return location + filename


# FileSystemStorage(location = settings.PROTECTED_ROOT)
# ProtectedS3BotoStorage()
class ProductFile(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    file = models.FileField(upload_to = product_file_loc, storage = FileSystemStorage(location = settings.PROTECTED_ROOT))
    name = models.CharField(max_length = 120, blank = True)
    free = models.BooleanField(default = False)
    user_required = models.BooleanField(default = False)
    created = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return str(self.file.name)

    class Meta:
        ordering = ('name', '-created')

    def get_download_url(self):
        return reverse('product:download', kwargs = {'slug' : self.product.slug, 'pk' : self.id})

    @property
    def get_name(self):
        original_name = get_filename(self.file.name)
        if self.name:
            return self.name
        return original_name

    def get_default_url(self):
        return self.product.get_absolute_url()

    def generate_download_url(self):
        bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
        region = getattr(settings, 'S3DIRECT_REGION')
        access_key = getattr(settings, 'AWS_ACCESS_KEY_ID')
        secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
        PROTECTED_DIR_NAME = getattr(settings, 'PROTECTED_DIR_NAME')
        path = '{base}/{file_path}'.format(base = PROTECTED_DIR_NAME, file_path = str(self.file))
        aws_dl_object =  AWSDownload(access_key, secret_key, bucket, region)
        file_url = aws_dl_object.generate_url(path, new_filename=self.get_name)
        return file_url

