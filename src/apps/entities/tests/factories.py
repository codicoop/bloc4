from factory.django import DjangoModelFactory

from apps.entities.models import Entity


class EntityFactory(DjangoModelFactory):
    class Meta:
        model = Entity
