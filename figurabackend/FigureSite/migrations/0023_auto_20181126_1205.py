# Generated by Django 2.0.8 on 2018-11-26 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FigureSite', '0022_auto_20181120_2347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thread',
            name='title',
            field=models.CharField(max_length=300),
        ),
    ]