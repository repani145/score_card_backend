from django.contrib import admin
from . import models

# Register your models here.
# admin.site.register(models.CustomUser)

from django.contrib.auth.admin import UserAdmin
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'mobile')}),
        ('Permissions', {'fields': ('user_type', 'is_superuser', 'is_admin', 'is_staff', 'is_blocked', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('module',),
            'fields': ('email', 'full_name', 'mobile', 'password1', 'password2'),
        }),
    )
    list_display = ('full_name', 'mobile', 'email', 'user_type', 'is_superuser', 'is_active', 'last_updated')
    list_filter = ('is_superuser', 'is_active', 'user_type')
    search_fields = ('email', 'full_name', 'mobile')
    ordering = ('email',)
    # filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(models.CustomUser, CustomUserAdmin)