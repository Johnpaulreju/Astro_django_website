# Generated by Django 5.1.6 on 2025-03-06 17:12

import myapp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='unique_id',
            field=models.CharField(default=myapp.models.generate_unique_id, editable=False, max_length=4, unique=True),
        ),
    ]
