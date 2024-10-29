# Generated by Django 5.1.1 on 2024-10-14 21:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0009_addonoption_menu_item_alter_addonoption_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('preparing', 'Preparing'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], max_length=50)),
                ('order_time', models.DateTimeField(auto_now_add=True)),
                ('special_instructions', models.TextField(blank=True, null=True)),
                ('delivery_address', models.CharField(blank=True, max_length=255, null=True)),
                ('is_delivery', models.BooleanField(default=False)),
                ('order_type', models.CharField(choices=[('dine_in', 'Dine-in'), ('takeaway', 'Takeaway'), ('delivery', 'Delivery')], max_length=50)),
                ('tax', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('tip', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('addon_options', models.ManyToManyField(blank=True, to='core.addonoption')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='core.restaurant')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('special_instructions', models.TextField(blank=True, null=True)),
                ('addon_options', models.ManyToManyField(blank=True, to='core.addonoption')),
                ('menu_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.menu')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payments.order')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='menu_items',
            field=models.ManyToManyField(through='payments.OrderItem', to='core.menu'),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_method', models.CharField(choices=[('credit_card', 'Credit Card'), ('cash', 'Cash'), ('mobile_payment', 'Mobile Payment'), ('wallet', 'Wallet')], max_length=50)),
                ('payment_status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('refunded', 'Refunded')], max_length=50)),
                ('transaction_id', models.CharField(max_length=255, unique=True)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('payment_gateway', models.CharField(choices=[('paypal', 'PayPal'), ('stripe', 'Stripe'), ('manual', 'Manual')], max_length=50)),
                ('refund_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('is_refunded', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='payments.order')),
            ],
        ),
    ]
