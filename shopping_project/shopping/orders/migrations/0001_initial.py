# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-13 17:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0006_auto_20160313_1725'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='Total Price')),
                ('delivery_price', models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='Delivery Price')),
                ('discount_price', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('remark', models.TextField(blank=True, max_length=255, null=True, verbose_name='Remark')),
                ('order_date', models.DateTimeField(verbose_name='Order Date')),
                ('is_paid', models.BooleanField(default=False)),
                ('is_delivered', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders_order_created_user', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders_order_modified_user', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrderProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('quantity', models.PositiveIntegerField(default=0, verbose_name='Quantity')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=11, verbose_name='Product Price')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders_orderproduct_created_user', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders_orderproduct_modified_user', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_product_order', to='orders.Order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_product_product', to='products.Product')),
                ('uom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_product_uom', to='products.UOM')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
