# Generated by Django 3.2 on 2023-07-30 13:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0005_title_rating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='title',
            name='rating',
        ),
    ]