# Generated by Django 5.2 on 2025-04-14 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_rename_address1_profile_address1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='old_cart',
            field=models.TextField(blank=True, default='{}', null=True),
        ),
    ]
