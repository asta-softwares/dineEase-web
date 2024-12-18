# Generated by Django 5.1.1 on 2024-11-19 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_remove_promo_code_remove_promo_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='promo',
            name='code',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='promo',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='promo_images/'),
        ),
        migrations.AddField(
            model_name='promo',
            name='minimum_order',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='promo',
            name='priority_index',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='promo',
            name='target_audience',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='promo',
            name='time_offer',
            field=models.JSONField(default={'Friday': '9:00AM – 3:00PM', 'Monday': '9:00AM – 3:00PM', 'Saturday': 'Closed', 'Sunday': 'Closed', 'Thursday': '9:00AM – 3:00PM', 'Tuesday': '9:00AM – 3:00PM', 'Wednesday': '9:00AM – 3:00PM'}),
        ),
    ]
