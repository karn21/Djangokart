# Generated by Django 2.2 on 2020-03-28 13:25

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0011_order_coupon'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BillingAddress',
            new_name='ShippingAddress',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='billing_address',
            new_name='shipping_address',
        ),
    ]
