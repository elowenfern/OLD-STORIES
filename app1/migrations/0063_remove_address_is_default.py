# Generated by Django 4.2.3 on 2023-11-17 11:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0062_remove_shipping_is_default'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='is_default',
        ),
    ]
