from factory.django import DjangoModelFactory

from apps.rooms.choices import RoomTypeChoices
from apps.rooms.models import Room


class RoomFactory(DjangoModelFactory):
    name = "Room test"
    room_type = RoomTypeChoices.EVENT_ROOM
    price = 10.0
    price_half_day = 30.0
    price_all_day = 50.0
    capacity = 10
    description = "Description test"
    equipment = "Equipment test"

    class Meta:
        model = Room
