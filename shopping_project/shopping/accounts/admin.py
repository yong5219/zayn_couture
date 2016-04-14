from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from accounts.models import AccountSignup, Profile


class AccountSignupInline(admin.StackedInline):
    model = AccountSignup
    max_num = 1


class UserAdmin(UserAdmin):
    # inlines = [AccountSignupInline, ]
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    list_display_links = ('username', 'email',)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date', 'age', 'state', 'country', )
    search_fields = ['user__first_name', 'user__last_name', 'user__email', ]
    date_hierarchy = 'created'


class AccountSignupAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_active', 'activation_key', 'activation_notification_send',)
    search_fields = ['user__first_name', 'user__last_name', 'user__email', ]
    date_hierarchy = 'created'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(AccountSignup, AccountSignupAdmin)
