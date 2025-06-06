# Generated by Django 5.0.3 on 2025-04-24 13:05

import django.core.validators
import django.db.models.deletion
import project.storage_backends
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_related', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AlterField(
            model_name='room',
            name='description',
            field=models.CharField(default='', max_length=500, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='room',
            name='name',
            field=models.CharField(default='', max_length=50, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='room',
            name='picture',
            field=models.ImageField(default='', storage=project.storage_backends.PublicMediaStorage(), upload_to='', validators=[django.core.validators.validate_image_file_extension], verbose_name='Picture'),
        ),
        migrations.AlterField(
            model_name='room',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Hourly price (VAT not included)'),
        ),
        migrations.AlterField(
            model_name='room',
            name='price_all_day',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='All day price (VAT not included)'),
        ),
        migrations.AlterField(
            model_name='room',
            name='price_half_day',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Half day price (VAT not included)'),
        ),
    ]
