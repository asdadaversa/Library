# Generated by Django 5.0.4 on 2024-05-07 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="session",
            field=models.CharField(max_length=100),
        ),
    ]
