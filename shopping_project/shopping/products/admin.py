from django.contrib import admin

from mptt.admin import MPTTModelAdmin

# from vookle.models import FancyboxMedia
from .models import Category, Product, Variety, UOM, ProductImage


class VarietyInline(admin.StackedInline):
    model = Variety


class ProductImageInline(admin.StackedInline):
    model = ProductImage


class CategoryMPTTModelAdmin(MPTTModelAdmin):
    mptt_level_indent = 20
    list_display = ('name', 'slug', 'ordering', 'publish_date', 'is_active',)
    list_editable = ('is_active',)
    prepopulated_fields = {"slug": ('name',)}
    sortable = 'ordering'


class ProductAdmin(admin.ModelAdmin):
    inlines = [VarietyInline, ProductImageInline]
    list_display = ('get_name', 'structure',
                    'main_category', 'variety_summary', 'price', 'discount_price', 'is_active')
    list_editable = ('is_active',)
    prepopulated_fields = {"slug": ('name',)}
    raw_id_fields = ['parent']
    search_fields = ['name', ]
    list_filter = ['structure', ]

    # def get_queryset(self, request):
    #     qs = super(ProductAdmin, self).get_queryset(request)
    #     if request.user.is_superuser:
    #         return qs
    #     else:
    #         return qs.filter(created_by=request.user)


class UOMAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {"slug": ('name',)}
    search_fields = ['name', ]


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryMPTTModelAdmin)
admin.site.register(UOM, UOMAdmin)
