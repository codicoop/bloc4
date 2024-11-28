import random

import factory
from factory.django import DjangoModelFactory

from apps.rooms.choices import RoomTypeChoices
from apps.rooms.models import Room


class RoomFactory(DjangoModelFactory):
    class Meta:
        model = Room
