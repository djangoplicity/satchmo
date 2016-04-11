# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ship_tax_code',
            field=models.CharField(max_length=20, verbose_name='Zip Code', blank=True),
        ),
    ]
