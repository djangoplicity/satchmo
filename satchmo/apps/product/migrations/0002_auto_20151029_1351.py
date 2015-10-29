# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='related_categories',
            field=models.ManyToManyField(related_name='_related_categories_+', verbose_name='Related Categories', to='product.Category', blank=True),
        ),
        migrations.AlterField(
            model_name='categoryattribute',
            name='languagecode',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='language', choices=[(b'en', b'English')]),
        ),
        migrations.AlterField(
            model_name='categoryimagetranslation',
            name='languagecode',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', b'English')]),
        ),
        migrations.AlterField(
            model_name='categorytranslation',
            name='languagecode',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', b'English')]),
        ),
        migrations.AlterField(
            model_name='discount',
            name='valid_categories',
            field=models.ManyToManyField(to='product.Category', verbose_name='Valid Categories', blank=True),
        ),
        migrations.AlterField(
            model_name='discount',
            name='valid_products',
            field=models.ManyToManyField(to='product.Product', verbose_name='Valid Products', blank=True),
        ),
        migrations.AlterField(
            model_name='optiongrouptranslation',
            name='languagecode',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', b'English')]),
        ),
        migrations.AlterField(
            model_name='optiontranslation',
            name='languagecode',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', b'English')]),
        ),
        migrations.AlterField(
            model_name='product',
            name='also_purchased',
            field=models.ManyToManyField(related_name='_also_purchased_+', verbose_name='Previously Purchased', to='product.Product', blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='related_items',
            field=models.ManyToManyField(related_name='_related_items_+', verbose_name='Related Items', to='product.Product', blank=True),
        ),
        migrations.AlterField(
            model_name='productattribute',
            name='languagecode',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='language', choices=[(b'en', b'English')]),
        ),
        migrations.AlterField(
            model_name='productimagetranslation',
            name='languagecode',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', b'English')]),
        ),
        migrations.AlterField(
            model_name='producttranslation',
            name='languagecode',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', b'English')]),
        ),
    ]
