from django.contrib import admin

from apps.entities.models import Entity
from project.admin import ModelAdmin


@admin.register(Entity)
class EntityAdmin(ModelAdmin):
    pass
