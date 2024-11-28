from factory.django import DjangoModelFactory

from apps.reservations.models import Reservation


class ReservationFactory(DjangoModelFactory):
    class Meta:
        model = Reservation
