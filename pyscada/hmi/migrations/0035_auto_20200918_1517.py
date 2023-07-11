# Generated by Django 2.2.8 on 2020-09-18 15:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hmi", "0034_auto_20200918_1445"),
    ]

    operations = [
        migrations.AlterField(
            model_name="form",
            name="control_items",
            field=models.ManyToManyField(
                blank=True,
                limit_choices_to={"type": "0"},
                related_name="control_items_form",
                to="hmi.ControlItem",
            ),
        ),
        migrations.AlterField(
            model_name="form",
            name="hidden_control_items_to_true",
            field=models.ManyToManyField(
                blank=True,
                limit_choices_to={"type": "0"},
                related_name="hidden_control_items_form",
                to="hmi.ControlItem",
            ),
        ),
    ]
