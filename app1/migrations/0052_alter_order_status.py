# Generated by Django 4.2.3 on 2023-11-14 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0051_remove_userrating_order_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('processing', 'processing'), ('shipped', 'shipped'), ('delivered', 'delivered'), ('completed', 'Completed'), ('return', 'Return'), ('cancelled', 'Cancelled'), ('refunded', 'refunded'), ('on_hold', 'on_hold')], default='pending', max_length=100),
        ),
    ]
