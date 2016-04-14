from django.contrib import admin

from .models import Order, OrderProduct

# Register your models here.


class OrderProductInline(admin.StackedInline):
    model = OrderProduct


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderProductInline, ]
    list_display = ('user', 'price', 'delivery_price', 'order_date', 'is_paid', 'is_delivered')
    list_editable = ('is_paid', 'is_delivered')

admin.site.register(Order, OrderAdmin)
