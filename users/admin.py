from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from django.contrib.auth.forms import AdminPasswordChangeForm


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'surname', 'is_active', 'is_staff')
    ordering = ('email',)
    search_fields = ('email', 'name', 'surname')
    fields = ('email', 'name', 'surname', 'avatar', 'phone', 'github_url', 'about', 'is_active', 'is_staff')
