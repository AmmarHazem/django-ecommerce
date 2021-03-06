# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-12 12:33
from __future__ import unicode_literals

import django.core.files.storage
from django.db import migrations, models
import product.models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0015_auto_20180711_1805'),
    ]

    operations = [
        migrations.AddField(
            model_name='productfile',
            name='free',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='productfile',
            name='user_required',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='productfile',
            name='file',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(location='C:\\Users\\Ammar\\Desktop\\ECommerce\\static_cdn\\protected_media'), upload_to=product.models.product_file_loc),
        ),
    ]
