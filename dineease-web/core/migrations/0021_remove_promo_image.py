# Generated by Django 5.1.1 on 2024-12-16 08:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_alter_promo_promo_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promo',
            name='image',
        ),
    ]