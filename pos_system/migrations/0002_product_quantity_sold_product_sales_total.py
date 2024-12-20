# Generated by Django 5.1 on 2024-11-26 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos_system', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='quantity_sold',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='sales_total',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
