# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-20 08:31
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0033_auto_20160420_0830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='publish_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 20, 8, 31, 17, 366937, tzinfo=utc), verbose_name='Publish date'),
        ),
    ]
