# Generated by Django 4.2.3 on 2023-10-24 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0048_remove_variation_image_variation_img'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]
