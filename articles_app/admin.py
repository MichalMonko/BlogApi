from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

from articles_app.forms import CustomUserChangeForm, CustomUserCreationForm
from articles_app.models import *


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username']


admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(Author)
admin.site.register(Tag)
admin.site.register(CustomUser, CustomUserAdmin)
