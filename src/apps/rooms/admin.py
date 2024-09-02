from django.contrib import admin

from apps.rooms.models import Room
from project.admin import ModelAdmin


@admin.register(Room)
class RoomAdmin(ModelAdmin):
    list_display = (
        "name",
        "code",
        "price",
        "capacity",
        "room_type",
    )
    list_filter = ("name", "price", "capacity", "equipment")
    search_fields = ("name", "price", "capacity", "equipment")
