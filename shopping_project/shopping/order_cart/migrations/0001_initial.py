# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-08 06:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0022_auto_20160408_0648'),
    ]

    operations = [
        migrations.CreateModel(
            name='Line',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('line_reference', models.SlugField(max_length=128, verbose_name='Line Reference')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Quantity')),
                ('price_excl_tax', models.DecimalField(decimal_places=2, max_digits=12, null=True, verbose_name='Price excl. Tax')),
                ('price_incl_tax', models.DecimalField(decimal_places=2, max_digits=12, null=True, verbose_name='Price incl. Tax')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
            ],
            options={
                'verbose_name_plural': 'Order Cart lines',
                'ordering': ['date_created', 'pk'],
                'verbose_name': 'Order Cart line',
            },
        ),
        migrations.CreateModel(
            name='OrderCart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('Open', 'Open - currently active'), ('Merged', 'Merged - superceded by another basket'), ('Saved', 'Saved - for items to be purchased later'), ('Frozen', 'Frozen - the basket cannot be modified'), ('Submitted', 'Submitted - has been ordered at the checkout')], default='Open', max_length=128, verbose_name='Status')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('date_merged', models.DateTimeField(blank=True, null=True, verbose_name='Date merged')),
                ('date_submitted', models.DateTimeField(blank=True, null=True, verbose_name='Date submitted')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_cart_ordercart_created_user', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_cart_ordercart_modified_user', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='baskets', to=settings.AUTH_USER_MODEL, verbose_name='Owner')),
            ],
            options={
                'verbose_name_plural': 'Baskets',
                'verbose_name': 'Basket',
            },
        ),
        migrations.AddField(
            model_name='line',
            name='cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='order_cart.OrderCart', verbose_name='Cart'),
        ),
        migrations.AddField(
            model_name='line',
            name='created_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_cart_line_created_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='line',
            name='modified_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_cart_line_modified_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='line',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_lines', to='products.Product', verbose_name='Product'),
        ),
    ]