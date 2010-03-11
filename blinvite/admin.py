from django.contrib import admin

from busylizzy.blinvite.models import Invite

class InviteAdmin(admin.ModelAdmin):
    pass

admin.site.register(Invite, InviteAdmin)
