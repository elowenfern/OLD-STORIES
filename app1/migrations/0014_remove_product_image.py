# Generated by Django 4.2.3 on 2023-10-07 10:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0013_remove_product_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='image',
        ),
    ]
