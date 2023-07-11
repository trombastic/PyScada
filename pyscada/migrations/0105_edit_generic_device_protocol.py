# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-24 12:45
from __future__ import unicode_literals

from django.db import migrations


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    DeviceProtocol = apps.get_model("pyscada", "DeviceProtocol")
    db_alias = schema_editor.connection.alias
    DeviceProtocol.objects.filter(pk=1).update(
        device_class="pyscada.generic.device", daq_daemon=True, single_thread=True
    )


def reverse_func(apps, schema_editor):
    # forwards_func() creates two Country instances,
    # so reverse_func() should delete them.
    DeviceProtocol = apps.get_model("pyscada", "DeviceProtocol")
    db_alias = schema_editor.connection.alias
    DeviceProtocol.objects.filter(pk=1).update(
        device_class="None", daq_daemon=False, single_thread=False
    )


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0104_rename_complexeventitem_complexeventinput_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
