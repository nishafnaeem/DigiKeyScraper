# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentsMedia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('data_sheets', models.TextField()),
                ('eda_cad_models', models.TextField()),
                ('online_catalog', models.TextField()),
            ],
            options={
                'db_table': 'part_documents_media',
            },
        ),
        migrations.CreateModel(
            name='GenericPart',
            fields=[
                ('uuid', models.UUIDField(default='9e3e758f-be77-42c6-87d7-43324be187e0')),
                ('part_id', models.AutoField(primary_key=True, serialize=False)),
                ('part_type', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2020, 10, 18, 8, 36, 10, 569322))),
            ],
            options={
                'db_table': 'generic_part',
            },
        ),
        migrations.CreateModel(
            name='PartImages',
            fields=[
                ('image_id', models.AutoField(primary_key=True, serialize=False)),
                ('image_link', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'part_images',
            },
        ),
        migrations.CreateModel(
            name='PartSpecifications',
            fields=[
                ('spec_id', models.AutoField(primary_key=True, serialize=False)),
                ('spec_name', models.CharField(max_length=200)),
                ('spec_value', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'part_specifications',
            },
        ),
        migrations.CreateModel(
            name='SpecificPart',
            fields=[
                ('part_id', models.AutoField(primary_key=True, serialize=False)),
                ('digi_key_part_no', models.CharField(max_length=200)),
                ('manufacturer', models.CharField(max_length=200)),
                ('mpn', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('detailed_description', models.TextField()),
                ('digikey_link', models.CharField(max_length=255)),
                ('price', models.CharField(max_length=20)),
                ('generic_part', models.ForeignKey(to='db.GenericPart')),
                ('specifications', models.ManyToManyField(to='db.PartSpecifications')),
            ],
            options={
                'db_table': 'specific_part',
            },
        ),
        migrations.AddField(
            model_name='partimages',
            name='specific_part',
            field=models.ForeignKey(to='db.SpecificPart'),
        ),
        migrations.AddField(
            model_name='documentsmedia',
            name='specific_part',
            field=models.ForeignKey(to='db.SpecificPart'),
        ),
    ]
