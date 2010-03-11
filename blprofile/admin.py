from django.contrib import admin

from busylizzy.blprofile.models import *

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_public', )

admin.site.register(UserProfile, UserProfileAdmin)
