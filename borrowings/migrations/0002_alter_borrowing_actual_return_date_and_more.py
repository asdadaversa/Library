# Generated by Django 5.0.4 on 2024-04-15 18:15

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0001_initial"),
        ("borrowings", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="borrowing",
            name="actual_return_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddConstraint(
            model_name="borrowing",
            constraint=models.UniqueConstraint(
                fields=("borrow_date", "expected_return_date", "actual_return_date"),
                name="post_like",
            ),
        ),
    ]
