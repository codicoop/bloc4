from factory.django import DjangoModelFactory

from apps.rooms.models import Room


class RoomFactory(DjangoModelFactory):
    capacity = 10

    class Meta:
        model = Room
