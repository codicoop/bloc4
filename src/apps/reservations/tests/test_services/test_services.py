from datetime import date

from django.test import TestCase

from apps.entities.choices import EntityTypesChoices
from apps.reservations.choices import ReservationTypeChoices
from apps.reservations.services import get_monthly_bonus
from apps.reservations.tests.factories import (
    EntityFactory,
    EntityPrivilegeFactory,
    MonthlyBonusFactory,
    ReservationFactory,
    UserFactory,
)


class ServicesTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.entity = EntityFactory(entity_type=EntityTypesChoices.GENERAL)
        self.reservation = ReservationFactory(
            title="Title test",
            reservation_type=ReservationTypeChoices.HOURLY,
            date=date(2024, 12, 25),
            assistants=10,
            entity=self.entity,
            reserved_by=self.user,
        )
        self.entity_privilege = EntityPrivilegeFactory(entity=self.entity)
        self.monthly_bonus = MonthlyBonusFactory(entity=self.entity)

    def test_get_monthly_bonus(self):
        self.results = get_monthly_bonus(self.monthly_bonus, self.reservation)
        print("self", self.results)
