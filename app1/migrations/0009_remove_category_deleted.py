# Generated by Django 4.2.3 on 2023-10-07 07:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0008_category_deleted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='deleted',
        ),
    ]
