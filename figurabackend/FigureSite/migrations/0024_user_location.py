# Generated by Django 2.0.8 on 2018-10-12 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FigureSite', '0023_post_banner'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='location',
            field=models.TextField(default='', max_length=100),
        ),
    ]
