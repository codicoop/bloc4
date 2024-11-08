from django.contrib import admin

from apps.entities.models import Entity
from project.admin import ModelAdmin


@admin.register(Entity)
class EntityAdmin(ModelAdmin):
    fields = [
        "entity_email",
        "fiscal_name",
        "nif",
        "address",
        "town",
        "postal_code",
        "country",
        "person_responsible",
        "entity_type",
        "reservation_privilege",
        "logo",
    ]
    list_display = (
        "fiscal_name",
        "entity_email",
        "nif",
        "entity_type",
        "reservation_privilege",
    )
    list_filter = ("fiscal_name", "entity_type")
    search_fields = ("entity_email", "fiscal_name", "nif", "entity_type")
