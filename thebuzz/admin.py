from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Post, Comment, Site_API_User
# Register your models here.

#This Inline code allows profile fields to be put under the User in the admin site
class AuthorInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'author'

class UserAdmin(BaseUserAdmin):
    inlines = (AuthorInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Site_API_User)
