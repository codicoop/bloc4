from django.contrib import admin
from django.utils.translation import gettext as _

from apps.entities.choices import EntityTypesChoices
from apps.entities.models import Entity, EntityPrivilege, MonthlyBonus
from project.admin import ModelAdmin


class EntityPrivilegeInline(admin.StackedInline):
    model = EntityPrivilege
    can_delete = False
    verbose_name = _("Entity Privileges")
    fields = (
        "monthly_hours_meeting",
        "anual_hours_class",
        "class_reservation_privilege",
    )


@admin.register(Entity)
class EntityAdmin(ModelAdmin):
    fields = (
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
    )
    list_display = (
        "fiscal_name",
        "entity_email",
        "nif",
        "entity_type",
        "reservation_privilege",
    )
    list_filter = ("fiscal_name", "entity_type")
    search_fields = ("entity_email", "fiscal_name", "nif", "entity_type")

    def get_inlines(self, request, obj=None):
        if not obj or obj.entity_type in [
            EntityTypesChoices.HOSTED,
            EntityTypesChoices.BLOC4,
        ]:
            return [EntityPrivilegeInline]
        return []


@admin.register(MonthlyBonus)
class MonthlyBonusAdmin(ModelAdmin):
    fields = (
        "entity",
        "date",
        "amount",
        "created_at",
        "updated_at",
        "created_by",
    )
    list_display = (
        "entity",
        "month_and_year",
        "amount",
    )
    search_fields = ("entity__fiscal_name",)
