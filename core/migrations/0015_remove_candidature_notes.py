# Generated by Django 5.1.4 on 2025-03-03 02:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_remove_candidature_date_candidature_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidature',
            name='notes',
        ),
    ]
