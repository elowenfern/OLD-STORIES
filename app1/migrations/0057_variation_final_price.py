# Generated by Django 4.2.3 on 2023-11-15 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0056_remove_category_description_remove_product_offer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='variation',
            name='final_price',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
