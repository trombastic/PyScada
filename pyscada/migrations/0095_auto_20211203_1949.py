# Generated by Django 2.2.24 on 2021-12-03 19:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0094_move_dictionaries"),
    ]

    operations = [
        migrations.AlterField(
            model_name="calculatedvariableselector",
            name="main_variable",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="pyscada.Variable"
            ),
        ),
    ]
