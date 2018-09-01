from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Forum, ForumCategory, Thread, Post
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from ordered_model.admin import OrderedModelAdmin

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

class ForumModelAdmin(OrderedModelAdmin):
    list_display = ('name', 'description', 'move_up_down_links')

class ForumCategoryModelAdmin(OrderedModelAdmin):
    list_display = ('name', 'description', 'move_up_down_links')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Forum, ForumModelAdmin)
admin.site.register(ForumCategory, ForumCategoryModelAdmin)
admin.site.register(Thread, admin.ModelAdmin)
admin.site.register(Post, admin.ModelAdmin)
