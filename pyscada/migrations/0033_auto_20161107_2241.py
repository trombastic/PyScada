# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-07 22:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0032_auto_20161107_2206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='device_type',
            field=models.CharField(choices=[(b'generic', b'no Protocol'), (b'systemstat', b'Local System Monitoring'), (b'modbus', b'Modbus Device'), (b'smbus', b'SMBus/I2C Device'), (b'phant', b'Phant Device'), (b'visa', b'VISA Device')], default=b'generic', max_length=400),
        ),
    ]
