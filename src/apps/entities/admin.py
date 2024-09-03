from django.contrib import admin

from apps.entities.models import Entity
from project.admin import ModelAdmin


@admin.register(Entity)
class EntityAdmin(ModelAdmin):
    list_display = (
        "email",
        "fiscal_name",
        "nif",
        "entity_type",
    )
    list_filter = ("fiscal_name", "entity_type")
    search_fields = ("email", "fiscal_name", "nif", "entity_type", "town")
