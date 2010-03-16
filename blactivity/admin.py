from django.contrib import admin
from busylissy.blactivity.models import Activity

class ActivityAdmin(admin.ModelAdmin):
    pass

admin.site.register(Activity, ActivityAdmin)
