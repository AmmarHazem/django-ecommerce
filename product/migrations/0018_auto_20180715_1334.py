# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-15 11:34
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0017_auto_20180715_1325'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productfile',
            options={'ordering': ('name', '-created')},
        ),
        migrations.AddField(
            model_name='productfile',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2018, 7, 15, 13, 34, 17, 813378)),
            preserve_default=False,
        ),
    ]
