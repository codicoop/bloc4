from factory.django import DjangoModelFactory

from apps.rooms.models import Room
from apps.rooms.choices import RoomTypeChoices


class RoomFactory(DjangoModelFactory):
    name = "Room test"
    location = "Location test"
    price = 10.0
    capacity = 10
    equipment = "Equipment test"
    room_type = RoomTypeChoices.EVENT_ROOM

    class Meta:
        model = Room
