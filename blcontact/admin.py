from busylizzy.blcontact.models import Contact
from django.contrib import admin

class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email' )
    prepopulated_fields = {'slug': ('first_name', 'last_name')}
    
admin.site.register(Contact, ContactAdmin)
