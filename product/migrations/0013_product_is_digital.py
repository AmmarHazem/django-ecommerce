# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-09 17:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0012_auto_20180506_1750'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_digital',
            field=models.BooleanField(default=False),
        ),
    ]
