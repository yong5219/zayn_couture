# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-15 17:58
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0029_auto_20160410_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='publish_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 15, 17, 58, 22, 280255, tzinfo=utc), verbose_name='Publish date'),
        ),
    ]