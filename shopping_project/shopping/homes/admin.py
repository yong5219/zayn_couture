from django.contrib import admin

from homes.models import BannerSlider


class BannerSliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'url_link', 'ordering', 'is_active', 'open_in_new',)
    list_editable = ('is_active', 'open_in_new', 'ordering')
    prepopulated_fields = {"slug": ('title',)}

admin.site.register(BannerSlider, BannerSliderAdmin)
