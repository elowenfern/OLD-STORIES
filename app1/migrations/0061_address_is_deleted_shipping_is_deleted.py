# Generated by Django 4.2.5 on 2023-11-17 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0060_remove_contact_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='shipping',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
