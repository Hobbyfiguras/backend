# Generated by Django 2.0.8 on 2019-01-17 02:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FigureSite', '0026_remove_mfcitem_manufacturer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mfcitem',
            old_name='title',
            new_name='name',
        ),
    ]
