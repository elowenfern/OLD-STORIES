# Generated by Django 4.2.3 on 2023-10-12 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0027_section_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('house_no', models.CharField(max_length=100)),
                ('post_code', models.CharField(max_length=20)),
                ('state', models.CharField(max_length=50)),
                ('street', models.CharField(max_length=100)),
                ('phone_no', models.CharField(blank=True, max_length=15)),
                ('city', models.CharField(max_length=100)),
                ('is_default', models.BooleanField(default=False)),
            ],
        ),
    ]
