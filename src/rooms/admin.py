from django.contrib import admin

from project.admin import ModelAdmin
from rooms.models import Room


@admin.register(Room)
class RoomAdmin(ModelAdmin):
    list_display = (
        "name",
        "location",
        "price",
        "capacity",
        "picture",
        "equipment",
        "room_type",
    )
    list_filter = ("name", "price", "capacity", "equipment")
    search_fields = ("name", "price", "capacity", "equipment")
