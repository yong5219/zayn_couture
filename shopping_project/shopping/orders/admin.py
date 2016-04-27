from django.contrib import admin

from .models import Order

# Register your models here.


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'price', 'delivery_price', 'order_date', 'is_paid', 'is_delivered')
    list_editable = ('is_paid', 'is_delivered')

admin.site.register(Order, OrderAdmin)
