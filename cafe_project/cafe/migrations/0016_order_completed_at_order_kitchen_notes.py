# Generated by Django 5.1.6 on 2025-04-05 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cafe', '0015_orderdetail_table_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='completed_at',
            field=models.DateTimeField(blank=True, help_text='When the order was marked as completed', null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='kitchen_notes',
            field=models.TextField(blank=True, help_text='Notes from kitchen staff about the order', null=True),
        ),
    ]
