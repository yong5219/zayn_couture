# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-17 17:51
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_auto_20160317_1709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='publish_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 17, 17, 51, 57, 464467, tzinfo=utc), verbose_name='Publish date'),
        ),
    ]