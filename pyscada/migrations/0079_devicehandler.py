# Generated by Django 2.2.8 on 2021-06-01 09:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0078_auto_20201123_1906"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeviceHandler",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(default="", max_length=255)),
                (
                    "handler_class",
                    models.CharField(
                        default="pyscada.visa.devices.HP3456A",
                        help_text="a Base class to extend can be found at pyscada.PROTOCOL.devices.GenericDevice. Exemple : pyscada.visa.devices.HP3456A, pyscada.smbus.devices.ups_pico, pyscada.serial.devices.AirLinkGX450",
                        max_length=255,
                    ),
                ),
                (
                    "handler_path",
                    models.CharField(
                        blank=True,
                        default=None,
                        help_text="If no handler class, pyscada will look at the path. Exemple : /home/pi/my_handler.py",
                        max_length=255,
                        null=True,
                    ),
                ),
            ],
        ),
    ]
