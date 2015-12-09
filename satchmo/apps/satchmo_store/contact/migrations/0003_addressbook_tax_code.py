# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0002_auto_20151029_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='addressbook',
            name='tax_code',
            field=models.CharField(max_length=20, verbose_name='Tax Code', blank=True),
        ),
    ]
