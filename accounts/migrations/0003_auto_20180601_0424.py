# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-01 02:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_full_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='full_name',
            field=models.CharField(max_length=50),
        ),
    ]
