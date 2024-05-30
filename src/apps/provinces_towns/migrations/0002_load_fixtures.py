from django.conf import settings
from django.core.management import call_command
from django.db import migrations


def load_fixtures(apps, schema_editor):
    print("")
    print("Loading Provinces, Counties and Towns")
    path = str(settings.BASE_DIR) + ("/apps/provinces_towns/fixtures"
                                     "/provinces_counties_towns.json")
    call_command("loaddata", path, verbosity=2)
    print("Fixtures loaded.")


class Migration(migrations.Migration):

    dependencies = [
        ('provinces_towns', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixtures)
    ]
