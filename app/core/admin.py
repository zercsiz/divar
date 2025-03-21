from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models
from django.contrib.auth import get_user_model


@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email',
                    'phone_number',
                    'first_name',
                    'last_name',
                    'plan',
                    'is_active',
                    'is_staff',
                    'is_superuser')

    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    ordering = ['email']
    list_filter = ('is_active', 'is_superuser', 'is_staff', 'plan')
    fieldsets = (
        (None,
            {'fields': ('email', 'password')}),
        ('Personal Info',
            {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Plan', {'fields': ('plan',)}),
        ('Permissions',
            {'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'first_name',
                'last_name',
                'phone_number',
                'plan',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )


class EntryImageInline(admin.TabularInline):
    """
    Inline class for entry image.
    """
    model = models.EntryImage
    extra = 4


@admin.register(models.Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category',
                    'price', 'created_at', 'is_expired')
    ordering = ['created_at',]
    readonly_fields = ['created_at', 'edited_at']
    search_fields = ('title', 'description')
    list_filter = ('is_expired',)
    inlines = [EntryImageInline]


admin.site.register(models.Category)


class UserInline(admin.TabularInline):
    """
    Inline class for user model.
    """
    model = get_user_model()
    fields = ('email',)
    readonly_fields = ('email',)
    extra = 0
    can_delete = False


@admin.register(models.Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_entries', 'days_to_expire')
    ordering = ['name',]
    inlines = [UserInline]


@admin.register(models.EntryImage)
class EntryImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'uploaded_at', 'entry')
    readonly_fields = ['uploaded_at',]
