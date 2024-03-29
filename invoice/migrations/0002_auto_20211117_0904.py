# Generated by Django 3.0.14 on 2021-11-17 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0001_initial_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='billitem',
            name='deduction',
            field=models.DecimalField(db_column='Deduction', decimal_places=2, default=0.0, max_digits=18),
        ),
        migrations.AddField(
            model_name='historicalbillitem',
            name='deduction',
            field=models.DecimalField(db_column='Deduction', decimal_places=2, default=0.0, max_digits=18),
        ),
        migrations.AddField(
            model_name='historicalinvoicelineitem',
            name='deduction',
            field=models.DecimalField(db_column='Deduction', decimal_places=2, default=0.0, max_digits=18),
        ),
        migrations.AddField(
            model_name='invoicelineitem',
            name='deduction',
            field=models.DecimalField(db_column='Deduction', decimal_places=2, default=0.0, max_digits=18),
        ),
    ]
