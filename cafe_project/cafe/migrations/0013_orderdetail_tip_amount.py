# Generated by Django 5.1.6 on 2025-04-04 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cafe', '0012_remove_order_menu_item_remove_order_notes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdetail',
            name='tip_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
