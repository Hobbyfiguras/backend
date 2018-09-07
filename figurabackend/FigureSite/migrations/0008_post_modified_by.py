# Generated by Django 2.1 on 2018-09-05 19:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FigureSite', '0007_post_delete_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
