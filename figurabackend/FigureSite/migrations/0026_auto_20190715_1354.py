# Generated by Django 2.2.3 on 2019-07-15 13:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FigureSite', '0025_auto_20190124_1810'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='forum',
            options={'permissions': (('change_threads_subscription', 'Change subscription status in forum'), ('move_threads', 'Move threads in forum'), ('make_threads_nsfw', 'Make thread be NSFW in forum'), ('create_threads', 'Create threads in forum'))},
        ),
    ]