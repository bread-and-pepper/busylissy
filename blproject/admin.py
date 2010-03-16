from django.contrib import admin
from django.contrib.contenttypes import generic

from busylissy.blproject.models import Project

class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'date', 'status', )

admin.site.register(Project, ProjectAdmin)
