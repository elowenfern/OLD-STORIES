# Generated by Django 4.2.3 on 2023-10-16 16:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0036_remove_address_full_name_address_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='stock',
        ),
    ]
