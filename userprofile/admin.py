from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
# Register your models here.
User = get_user_model()


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name',)
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    model = User
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number',),
        }
        ),
    )


admin.site.register(User, CustomUserAdmin)
