# Generated by Django 5.1.1 on 2024-12-15 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_promo_code_promo_image_promo_minimum_order_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promo',
            name='menu',
        ),
        migrations.AddField(
            model_name='menu',
            name='promos',
            field=models.ManyToManyField(blank=True, related_name='menus', to='core.promo'),
        ),
        migrations.AddField(
            model_name='promo',
            name='promo_type',
            field=models.CharField(choices=[('menu', 'Menu'), ('restaurant', 'Restaurant'), ('dineease', 'DineEase')], default='menu', max_length=20),
        ),
    ]