# Generated by Django 4.2.3 on 2023-10-11 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0019_product_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='price',
            field=models.IntegerField(default=0),
        ),
    ]
