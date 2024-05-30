from django.test import TestCase

from apps.provinces_towns.models import (
    AutonomousCommunityChoices,
    County,
    Province,
    Town,
)


class ProvinceTest(TestCase):
    def setUp(self):
        self.province = Province.objects.filter(name="Barcelona").first()

    def test_save(self):
        self.assertIsInstance(self.province, Province)
        self.assertEqual(self.province.name, "Barcelona")
        self.assertEqual(
            self.province.autonomous_community, AutonomousCommunityChoices.CATALUNYA
        )


class CountyTest(TestCase):
    def setUp(self):
        self.county = County.objects.filter(name="Barcelonès ").first()

    def test_save(self):
        self.assertIsInstance(self.county, County)
        self.assertEqual(self.county.name, "Barcelonès ")
        self.assertEqual(self.county.province.name, "Barcelona")
        self.assertEqual(
            self.county.province.autonomous_community,
            AutonomousCommunityChoices.CATALUNYA,
        )


class TownTest(TestCase):
    def setUp(self):
        self.town = Town.objects.filter(name="Barcelona").first()

    def test_save(self):
        self.assertIsInstance(self.town, Town)
        self.assertEqual(self.town.name, "Barcelona")
        self.assertEqual(self.town.county.name, "Barcelonès ")
        self.assertEqual(self.town.county.province.name, "Barcelona")
        self.assertEqual(
            self.town.county.province.autonomous_community,
            AutonomousCommunityChoices.CATALUNYA,
        )
