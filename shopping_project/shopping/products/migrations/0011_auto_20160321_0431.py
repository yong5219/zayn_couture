# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-21 04:31
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_auto_20160319_0523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='publish_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 21, 4, 31, 50, 545401, tzinfo=utc), verbose_name='Publish date'),
        ),
    ]
