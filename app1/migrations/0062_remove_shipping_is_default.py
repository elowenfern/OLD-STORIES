# Generated by Django 4.2.3 on 2023-11-17 11:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0061_address_is_deleted_shipping_is_deleted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shipping',
            name='is_default',
        ),
    ]
