# Generated by Django 3.0.3 on 2020-07-24 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dgsys2', '0002_auto_20200615_1422'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='price_per_unit',
            field=models.BooleanField(default=False, verbose_name='Show number input in app'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='rental_related',
            field=models.BooleanField(default=True, verbose_name='Associated to rentals'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='itempurchase',
            name='quantity',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
