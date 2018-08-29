from django.contrib import admin
from . import models

admin.site.register(models.ContentCategory)
admin.site.register(models.Content)