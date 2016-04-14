from django.contrib import admin

from order_cart.models import OrderCart, Line


class LineInline(admin.TabularInline):
    model = Line
    readonly_fields = ('line_reference', 'product', 'price_excl_tax',
                       'price_incl_tax')


class LineAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity',
                    'price_excl_tax', 'created')
    # readonly_fields = ('cart', 'line_reference', 'product',
    #                    'price_incl_tax', 'price_excl_tax',
    #                    'quantity')


class OrderCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'status',
                    'created', 'date_submitted',
                    'time_before_submit')
    readonly_fields = ('date_submitted',)
    inlines = [LineInline]


admin.site.register(OrderCart, OrderCartAdmin)
admin.site.register(Line, LineAdmin)
