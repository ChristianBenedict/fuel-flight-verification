# Generated by Django 5.0.3 on 2024-05-06 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ReconApp', '0003_missinginvoiceinocc_missinginvoiceinvendor'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MissingInvoice',
        ),
        migrations.DeleteModel(
            name='MissingInvoiceOcc',
        ),
        migrations.DeleteModel(
            name='Reconsiliasi',
        ),
        migrations.AlterField(
            model_name='missinginvoiceinocc',
            name='arrival',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='missinginvoiceinocc',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='missinginvoiceinocc',
            name='departure',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='missinginvoiceinocc',
            name='flight',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='missinginvoiceinocc',
            name='fuel_agent',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='missinginvoiceinocc',
            name='invoice_no',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='missinginvoiceinocc',
            name='registration',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='missinginvoiceinocc',
            name='uplift_in_lts',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='missinginvoiceinvendor',
            name='arrival',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='missinginvoiceinvendor',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='missinginvoiceinvendor',
            name='departure',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='missinginvoiceinvendor',
            name='flight',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='missinginvoiceinvendor',
            name='fuel_agent',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='missinginvoiceinvendor',
            name='invoice_no',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='missinginvoiceinvendor',
            name='registration',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='missinginvoiceinvendor',
            name='uplift_in_lts',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
