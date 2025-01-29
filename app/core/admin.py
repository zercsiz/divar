from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models


@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email',
                    'phone_number',
                    'first_name',
                    'last_name',
                    'is_active',
                    'is_staff',
                    'is_superuser')

    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    ordering = ['email']
    exclude = ['username']
    list_filter = ('is_active', 'is_superuser', 'is_staff')
    fieldsets = (
        ('Credentials',
            {'fields': ('email', 'password')}),
        ('Personal Info',
            {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions',
            {'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fields = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',

            )
        }),
    )
