# Generated by Django 2.2 on 2020-03-28 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20200328_1918'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_id',
            field=models.CharField(default=0, max_length=20),
            preserve_default=False,
        ),
    ]
