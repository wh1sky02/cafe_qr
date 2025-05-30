# Generated by Django 5.1.6 on 2025-02-17 04:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cafe', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('image', models.CharField(max_length=200)),
                ('category', models.CharField(max_length=50)),
                ('is_bestseller', models.BooleanField(default=False)),
                ('is_new', models.BooleanField(default=False)),
            ],
        ),
    ]
