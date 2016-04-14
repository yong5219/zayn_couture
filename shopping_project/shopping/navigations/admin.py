from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from .models import NavigationMenu, FooterNavigationMenu


class NavigationMenuMPTTModelAdmin(MPTTModelAdmin):
    mptt_level_indent = 20
    list_display = ('navigation', 'parent', 'link', 'ordering', 'is_active',)
    # list_editable = ('is_active',)
    prepopulated_fields = {"slug": ('navigation',)}
    # sortable = 'ordering'

admin.site.register(NavigationMenu, NavigationMenuMPTTModelAdmin)


class FooterNavigationMenuMPTTModelAdmin(MPTTModelAdmin):
    mptt_level_indent = 20
    list_display = ('navigation', 'parent', 'link', 'ordering', 'is_active',)
    # list_editable = ('is_active',)
    prepopulated_fields = {"slug": ('navigation',)}
    # sortable = 'ordering'

admin.site.register(FooterNavigationMenu, FooterNavigationMenuMPTTModelAdmin)
