# Generated by Django 5.1.4 on 2025-04-07 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_notifications'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notifications',
            name='lu',
            field=models.BooleanField(default=False),
        ),
    ]
