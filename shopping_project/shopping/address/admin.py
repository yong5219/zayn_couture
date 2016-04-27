from django.contrib import admin

from address.models import UserAddress, Address, ShippingAddress


class UserAddressAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class AddressAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class ShippingAddressAdmin(admin.ModelAdmin):
    search_fields = ('name',)


admin.site.register(UserAddress, UserAddressAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
