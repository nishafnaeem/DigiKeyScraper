from datetime import datetime

import uuid as uuid
from django.db import models


class GenericPart(models.Model):
    uuid = models.UUIDField(default=str(uuid.uuid4()))
    part_id = models.AutoField(primary_key=True)
    part_type = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=datetime.now())

    class Meta:
        db_table = 'generic_part'


class PartSpecifications(models.Model):
    spec_id = models.AutoField(primary_key=True)
    spec_name = models.CharField(max_length=200)
    spec_value = models.CharField(max_length=200)

    class Meta:
        db_table = 'part_specifications'


class SpecificPart(models.Model):
    part_id = models.AutoField(primary_key=True)
    generic_part = models.ForeignKey(GenericPart)
    digi_key_part_no = models.CharField(max_length=200)
    manufacturer = models.CharField(max_length=200)
    mpn = models.CharField(max_length=200)
    description = models.TextField()
    detailed_description = models.TextField()
    digikey_link = models.CharField(max_length=255)
    price = models.CharField(max_length=20)
    specifications = models.ManyToManyField(PartSpecifications)

    class Meta:
        db_table = 'specific_part'


class DocumentsMedia(models.Model):
    specific_part = models.ForeignKey(SpecificPart)
    data_sheets = models.TextField()
    eda_cad_models = models.TextField()
    online_catalog = models.TextField()

    class Meta:
        db_table = 'part_documents_media'


class PartImages(models.Model):
    image_id = models.AutoField(primary_key=True)
    specific_part = models.ForeignKey(SpecificPart)
    image_link = models.CharField(max_length=200)

    class Meta:
        db_table = 'part_images'
