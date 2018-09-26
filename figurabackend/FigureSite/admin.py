from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Forum, ForumCategory, Thread, Post, VoteType
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from ordered_model.admin import OrderedModelAdmin

class CustomUserAdmin(UserAdmin):
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'fields': ('avatar', 'mal_username', 'anilist_username', 'mfc_username', 'twitter_username',),
        }),
    )
    fieldsets = UserAdmin.fieldsets + (
        (None, {
            'fields': ('avatar', 'mal_username', 'anilist_username', 'mfc_username', 'twitter_username', 'nsfw_enabled',),
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
admin.site.register(VoteType, admin.ModelAdmin)
