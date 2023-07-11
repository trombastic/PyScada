# Generated by Django 2.2.17 on 2020-12-03 21:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("hmi", "0049_auto_20201202_2037"),
    ]

    operations = [
        migrations.CreateModel(
            name="ControlElementOption",
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
                ("name", models.CharField(max_length=400)),
                (
                    "placeholder",
                    models.CharField(default="Enter a value", max_length=30),
                ),
                ("empty_dictionary", models.BooleanField(default=False)),
                (
                    "dictionary",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="hmi.Dictionary",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="controlitem",
            name="control_element_options",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="hmi.ControlElementOption",
            ),
        ),
    ]
