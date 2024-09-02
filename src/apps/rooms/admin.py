from django.contrib import admin

from apps.rooms.models import Room
from project.admin import ModelAdmin


@admin.register(Room)
class RoomAdmin(ModelAdmin):
    fields = [
        "name",
        "room_type",
        "code",
        "price",
        "price_half_day",
        "price_all_day",
        "capacity",
        "picture",
        "description",
        "equipment",
    ]
    list_display = (
        "name",
        "room_type",
        "capacity",
        "code",
    )
    list_filter = ("name", "room_type", "capacity", "equipment")
    search_fields = ("name", "room_type", "capacity", "equipment")
