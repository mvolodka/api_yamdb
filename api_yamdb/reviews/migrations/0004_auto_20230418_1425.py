# Generated by Django 3.2 on 2023-04-18 14:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_auto_20230418_1424'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['pub_date'], 'verbose_name': 'Комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ['pub_date'], 'verbose_name': 'Отзыв', 'verbose_name_plural': 'Отзывы'},
        ),
    ]