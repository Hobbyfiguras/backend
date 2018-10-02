# Generated by Django 2.0.8 on 2018-09-27 09:37

import FigureSite.models
from django.db import migrations
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('FigureSite', '0016_auto_20180926_1013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='votetype',
            name='icon',
            field=django_resized.forms.ResizedImageField(crop=['middle', 'center'], force_format='PNG', keep_meta=True, quality=0, size=[32, 32], upload_to=FigureSite.models.VoteTypeRename()),
        ),
    ]