# Generated by Django 2.2.8 on 2020-10-06 13:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0069_complexeventgroup_current_level"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="complexeventgroup",
            name="current_level",
        ),
        migrations.AddField(
            model_name="complexevent",
            name="active",
            field=models.BooleanField(default=False),
        ),
    ]
