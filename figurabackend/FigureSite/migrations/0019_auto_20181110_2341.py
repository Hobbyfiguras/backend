# Generated by Django 2.0.8 on 2018-11-10 23:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FigureSite', '0018_auto_20181029_1528'),
    ]

    operations = [
        migrations.CreateModel(
            name='BanReason',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(editable=False)),
                ('ban_reason', models.TextField(max_length=1000)),
                ('ban_expiry_date', models.DateTimeField(editable=False)),
            ],
        ),
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
        migrations.AddField(
            model_name='banreason',
            name='banned_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bans', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='banreason',
            name='banner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='banreason',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bans', to='FigureSite.Post'),
        ),
    ]
