from django.contrib import admin

from monitor.models import Website, StatusCheck

# Register your models here.
admin.site.register(Website)
admin.site.register(StatusCheck)