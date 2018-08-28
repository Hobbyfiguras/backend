from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CustomUserAdmin(UserAdmin):
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'fields': ('avatar',),
        }),
    )
    fieldsets = UserAdmin.fieldsets + (
        (None, {
            'fields': ('avatar',),
        }),
    )


admin.site.register(User, CustomUserAdmin)
