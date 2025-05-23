# Generated by Django 5.0.3 on 2024-12-10 15:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('entities', '0002_initial'),
        ('reservations', '0001_initial'),
        ('rooms', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='canceled_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reservation_canceled_by', to=settings.AUTH_USER_MODEL, verbose_name='canceled by'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_related', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='entity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservation_entity', to='entities.entity', verbose_name='entity'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='reserved_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservation_reserved_by', to=settings.AUTH_USER_MODEL, verbose_name='reserved by'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='room',
            field=models.ForeignKey(help_text='If you want to change the room and notify the user, first, change the room, save and then click the button to notify.', on_delete=django.db.models.deletion.CASCADE, related_name='reservation_room', to='rooms.room', verbose_name='room'),
        ),
        migrations.AlterUniqueTogether(
            name='reservation',
            unique_together={('date', 'start_time', 'end_time', 'room_id')},
        ),
    ]
