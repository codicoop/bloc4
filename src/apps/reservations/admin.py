from django.contrib import admin

from apps.reservations.models import Reservation
from project.admin import ModelAdmin


@admin.register(Reservation)
class ReservationAdmin(ModelAdmin):
    list_display = (
        "date",
        "start_time",
        "end_time",
        "motivation",
        "assistants",
        "room",
        "is_paid",
        "total_price",
        "entity",
        "reserved_by",
        "status",
    )
    list_filter = (
        "date",
        "room",
        "is_paid",
        "entity",
        "reserved_by",
        "status",
    )
    search_fields = (
        "date",
        "room",
        "is_paid",
        "entity",
        "reserved_by",
        "status",
    )
