# Generated by Django 2.0.8 on 2018-11-11 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FigureSite', '0020_privatemessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forum',
            name='description',
            field=models.CharField(max_length=500),
        ),
    ]
