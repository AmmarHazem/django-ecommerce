# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-15 12:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_auto_20180710_1436'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
