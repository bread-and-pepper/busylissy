from django.contrib import admin

from busylissy.blinvite.models import Invite

class InviteAdmin(admin.ModelAdmin):
    pass

admin.site.register(Invite, InviteAdmin)
