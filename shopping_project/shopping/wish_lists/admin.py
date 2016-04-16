from django.contrib import admin

from wish_lists.models import WishList, WishListProduct


class WishListProductInline(admin.TabularInline):
    model = WishListProduct


class WishListAdmin(admin.ModelAdmin):
    list_display = ('user', )
    inlines = [WishListProductInline]


admin.site.register(WishList, WishListAdmin)
