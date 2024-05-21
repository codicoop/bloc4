from django.contrib import admin

from apps.entities.models import Entity
from project.admin import ModelAdmin


@admin.register(Entity)
class EntityAdmin(ModelAdmin):
    list_display = (
        "email",
        "fiscal_name",
        "nif",
        "is_resident",
    )
    list_filter = ("fiscal_name", "is_resident")
    search_fields = ("email", "fiscal_name", "nif", "is_resident", "town")
