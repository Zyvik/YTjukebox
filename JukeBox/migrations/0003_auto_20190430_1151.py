# Generated by Django 2.1.4 on 2019-04-30 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('JukeBox', '0002_auto_20190429_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='currentstate',
            name='play_pause_count',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='currentstate',
            name='rewind_count',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='currentstate',
            name='time',
            field=models.PositiveIntegerField(default=0),
        ),
    ]