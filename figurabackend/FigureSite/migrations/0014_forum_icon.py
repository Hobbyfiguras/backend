# Generated by Django 2.0.8 on 2018-09-20 10:15

import FigureSite.models
from django.db import migrations
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('FigureSite', '0013_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='forum',
            name='icon',
            field=django_resized.forms.ResizedImageField(blank=True, crop=None, force_format='PNG', keep_meta=True, null=True, quality=0, size=[128, 128], upload_to=FigureSite.models.ForumIconRename()),
        ),
    ]
