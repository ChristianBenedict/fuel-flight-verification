# Generated by Django 5.0.3 on 2024-05-03 03:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
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
                ('Vendor', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='MissingInvoiceOcc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('flight', models.CharField(max_length=50)),
                ('departure', models.CharField(max_length=100)),
                ('arrival', models.CharField(max_length=100)),
                ('registration', models.CharField(max_length=20)),
                ('uplift_in_lts', models.FloatField()),
                ('invoice_no', models.CharField(max_length=100)),
                ('vendor', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Reconsiliasi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_occ', models.DateField()),
                ('flight_occ', models.CharField(max_length=50)),
                ('departure_occ', models.CharField(max_length=100)),
                ('arrival_occ', models.CharField(max_length=100)),
                ('registration_occ', models.CharField(max_length=20)),
                ('uplift_in_lts_occ', models.FloatField()),
                ('date_ven', models.DateField()),
                ('flight_ven', models.CharField(max_length=50)),
                ('departure_ven', models.CharField(max_length=100)),
                ('arrival_ven', models.CharField(max_length=100)),
                ('registration_ven', models.CharField(max_length=20)),
                ('uplift_in_lts_ven', models.FloatField()),
                ('invoice_no', models.CharField(max_length=100)),
                ('vendor', models.CharField(blank=True, choices=[('pertamina', 'Pertamina'), ('petronas_dagangan', 'Petronas Dagangan'), ('pttor', 'PTTOR'), ('bafs', 'BAFS'), ('petronas_dagangan_berhad', 'Petronas Dagangan Berhad'), ('shell', 'Shell'), ('petron', 'Petron'), ('airbp', 'AIRBP'), ('ptt_public_co_ltd', 'PTT Public Co. Ltd'), ('singapore_petroleum_company_limited', 'Singapore Petroleum Company Limited'), ('shell_malaysia_trading', 'Shell Malaysia Trading')], max_length=100, null=True)),
            ],
        ),
    ]
