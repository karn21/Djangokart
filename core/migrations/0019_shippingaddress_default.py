# Generated by Django 2.2 on 2020-04-01 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20200329_1050'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingaddress',
            name='default',
            field=models.BooleanField(default=False),
        ),
    ]
