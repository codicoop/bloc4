from django.db import migrations


def generate_entity(apps, schema_editor):
    town_model = apps.get_model("provinces_towns.town")
    entity_model = apps.get_model("entities.entity")

    # Creation of the Codi Cooperatiu entity
    codi_entity = entity_model()
    codi_entity.email = "codi@codi.coop"
    codi_entity.fiscal_name = "Codi Cooperatiu SCCL"
    codi_entity.nif = "F67151233"
    codi_entity.town = town_model.objects.filter(name="Barcelona").first()
    codi_entity.postal_code = "08004"
    codi_entity.address = "Carrer de Piquer, núm 27, Sobreatic 2º"
    codi_entity.reservation_privilege = False
    codi_entity.save()

    # Creation of the Bloc4 entity
    bloc4_entity = entity_model()
    bloc4_entity.email = "info@bloc4.coop"
    bloc4_entity.fiscal_name = "Bloc4BCN"
    bloc4_entity.nif = "B65789543"
    bloc4_entity.town = town_model.objects.filter(name="Barcelona").first()
    bloc4_entity.postal_code = "08014"
    bloc4_entity.address = "Carrer Constitució, 19"
    bloc4_entity.reservation_privilege = True
    bloc4_entity.save()

    print("\n\tInitial entities created.")


class Migration(migrations.Migration):
    dependencies = [
        ('entities', '0001_initial'),
        ('entities', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(generate_entity)
    ]
