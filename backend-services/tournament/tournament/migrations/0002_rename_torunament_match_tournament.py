# Generated by Django 5.1.4 on 2024-12-07 11:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tournament", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="match",
            old_name="torunament",
            new_name="tournament",
        ),
    ]
