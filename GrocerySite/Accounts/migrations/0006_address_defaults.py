# Generated by Django 4.1.7 on 2023-03-14 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0005_order_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='defaults',
            field=models.BooleanField(default=False),
        ),
    ]