# Generated by Django 4.2.3 on 2023-10-09 12:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0016_remove_product_images_remove_product_price_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='variation',
            name='image',
        ),
        migrations.AlterField(
            model_name='variation',
            name='price',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='variation',
            name='image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app1.images'),
        ),
    ]
