# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-01 17:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('markting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='marktingprefrence',
            name='mailchimp_subscribed',
            field=models.NullBooleanField(),
        ),
    ]
