# Generated by Django 3.0.14 on 2021-12-03 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0002_auto_20211117_0904'),
    ]

    operations = [
        migrations.AddField(
            model_name='billpayment',
            name='payment_origin',
            field=models.CharField(db_column='PaymentOrigin', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='historicalbillpayment',
            name='payment_origin',
            field=models.CharField(db_column='PaymentOrigin', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='historicalinvoicepayment',
            name='payment_origin',
            field=models.CharField(db_column='PaymentOrigin', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='invoicepayment',
            name='payment_origin',
            field=models.CharField(db_column='PaymentOrigin', max_length=255, null=True),
        ),
    ]
