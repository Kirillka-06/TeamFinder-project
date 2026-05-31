from django.contrib import admin
from .models import Project, Skill

admin.site.register(Skill)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'status', 'created_at')
    list_filter = ('status',)
    filter_horizontal = ('participants', 'skills')
