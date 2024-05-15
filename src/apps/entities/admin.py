from django.contrib import admin

from apps.entities.models import Entity


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    pass
