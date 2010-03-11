from django.contrib import admin
from django.contrib.contenttypes import generic

from busylizzy.blgroup.models import Group

class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}
    list_display = ('name', )

admin.site.register(Group, GroupAdmin)
