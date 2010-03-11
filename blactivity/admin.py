from django.contrib import admin
from busylizzy.blactivity.models import Activity

class ActivityAdmin(admin.ModelAdmin):
    pass

admin.site.register(Activity, ActivityAdmin)
