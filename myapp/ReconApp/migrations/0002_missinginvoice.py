# Generated by Django 5.0.3 on 2024-03-26 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ReconApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MissingInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('flight', models.CharField(max_length=50)),
                ('departure', models.CharField(max_length=100)),
                ('arrival', models.CharField(max_length=100)),
                ('registration', models.CharField(max_length=20)),
                ('uplift_in_lts', models.FloatField()),
                ('invoice_no', models.CharField(max_length=100)),
                ('vendor', models.CharField(blank=True, choices=[('pertamina', 'Pertamina'), ('shell', 'Shell'), ('total', 'Total'), ('chevron', 'Chevron'), ('petronas', 'Petronas'), ('air_bp', 'Air BP')], max_length=100, null=True)),
            ],
        ),
    ]
