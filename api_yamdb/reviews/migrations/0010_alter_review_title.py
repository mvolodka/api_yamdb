# Generated by Django 3.2 on 2023-04-19 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0009_auto_20230419_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='title',
            field=models.IntegerField(default=1),
        ),
    ]
