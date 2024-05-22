from django.db import migrations


def generate_entity(apps, schema_editor):
    town_model = apps.get_model("provinces_towns.town")
    entity_model = apps.get_model("entities.entity")

    entity = entity_model()
    entity.email = "codi@codi.coop"
    entity.fiscal_name = "Codi Cooperatiu SCCL"
    entity.nif = "F67151233"
    entity.town = town_model.objects.filter(name="Barcelona").first()
    entity.postal_code = "08004"
    entity.address = "Carrer de Piquer, núm 27, Sobreatic 2º"
    entity.is_resident = True
    entity.save()

    print("\n\tInitial entity created.")


class Migration(migrations.Migration):
    dependencies = [
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(generate_entity)
    ]
