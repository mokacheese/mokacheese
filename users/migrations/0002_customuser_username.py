# Generated by Django 5.1.1 on 2024-10-05 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="username",
            field=models.CharField(max_length=150, null=True, unique=True),
        ),
    ]
