# Generated by Django 2.2.17 on 2020-12-02 20:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hmi", "0048_chartaxis_fill"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chartaxis",
            name="max",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="chartaxis",
            name="min",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
