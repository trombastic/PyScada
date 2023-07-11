# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-12-05 09:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hmi", "0017_groupdisplaypermission_forms"),
    ]

    operations = [
        migrations.CreateModel(
            name="DropDown",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(default="", max_length=400)),
                ("empty", models.BooleanField(default=False)),
                ("empty_value", models.CharField(default="------", max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name="DropDownItem",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(default="", max_length=400)),
            ],
        ),
        migrations.AddField(
            model_name="dropdown",
            name="items",
            field=models.ManyToManyField(to="hmi.DropDownItem"),
        ),
        migrations.AddField(
            model_name="controlpanel",
            name="dropdowns",
            field=models.ManyToManyField(blank=True, to="hmi.DropDown"),
        ),
        migrations.AddField(
            model_name="form",
            name="dropdowns",
            field=models.ManyToManyField(
                blank=True, related_name="dropdowns_form", to="hmi.DropDown"
            ),
        ),
        migrations.AddField(
            model_name="groupdisplaypermission",
            name="dropdowns",
            field=models.ManyToManyField(blank=True, to="hmi.DropDown"),
        ),
    ]
