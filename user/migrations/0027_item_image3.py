# Generated by Django 3.0.3 on 2020-04-15 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0026_auto_20200415_1125'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='image3',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
