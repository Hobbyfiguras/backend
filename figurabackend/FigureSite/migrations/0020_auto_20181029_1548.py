# Generated by Django 2.0.8 on 2018-10-29 15:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FigureSite', '0019_banreason'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='ban_reason',
        ),
        migrations.RemoveField(
            model_name='post',
            name='banner',
        ),
        migrations.RemoveField(
            model_name='user',
            name='ban_expiry_date',
        ),
        migrations.RemoveField(
            model_name='user',
            name='ban_reason',
        ),
        migrations.AlterField(
            model_name='banreason',
            name='banner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]