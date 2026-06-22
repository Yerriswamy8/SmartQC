from django.contrib import admin
from .models import Project, Recipe, AIModel
admin.site.register([Project, Recipe, AIModel])
