# Generated by Django 2.2 on 2020-03-19 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20200319_1837'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='item',
            options={'ordering': ['title']},
        ),
        migrations.AddField(
            model_name='item',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]