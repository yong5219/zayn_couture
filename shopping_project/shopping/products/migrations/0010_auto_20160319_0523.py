# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-19 05:23
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_auto_20160317_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='publish_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 19, 5, 23, 1, 627842, tzinfo=utc), verbose_name='Publish date'),
        ),
    ]