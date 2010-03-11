from django.contrib import admin

from busylizzy.bltask.models import Task

class TaskAdmin(admin.ModelAdmin):
    """ 
    This is pure aestethics because controlling this in the admin has nu use. 
    
    """
    pass

admin.site.register(Task, TaskAdmin)
