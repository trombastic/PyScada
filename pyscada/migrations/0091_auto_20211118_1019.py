# Generated by Django 2.2.8 on 2021-11-18 10:19

import datetime
from django.db import migrations, models
from datetime import timezone


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0090_auto_20211117_1239"),
    ]

    operations = [
        migrations.AlterField(
            model_name="periodicfield",
            name="start_from",
            field=models.DateTimeField(
                default=datetime.datetime(2021, 11, 18, 0, 0, tzinfo=timezone.utc),
                help_text="Calculate from this DateTime and then each period_factor*period",
            ),
        ),
    ]
