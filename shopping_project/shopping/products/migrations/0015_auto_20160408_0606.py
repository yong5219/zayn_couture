# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-08 06:06
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0014_auto_20160408_0605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='publish_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 8, 6, 6, 48, 270552, tzinfo=utc), verbose_name='Publish date'),
        ),
    ]