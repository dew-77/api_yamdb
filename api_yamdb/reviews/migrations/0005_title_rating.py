# Generated by Django 3.2 on 2023-07-30 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_remove_title_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='title',
            name='rating',
            field=models.FloatField(null=True, verbose_name='Рейтинг'),
        ),
    ]
