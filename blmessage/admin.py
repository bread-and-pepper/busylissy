from busylissy.blmessage.models import Thread, Message
from django.contrib import admin

class MessageInline(admin.TabularInline):
    model = Message

class ThreadAdmin(admin.ModelAdmin):
   inlines = [MessageInline,]

admin.site.register(Thread, ThreadAdmin)
