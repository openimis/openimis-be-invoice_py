# Generated by Django 3.0.14 on 2022-04-13 08:24

import core.models
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_add_last_login_on_interactive_user'),
        ('invoice', '0008_auto_20220411_1358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpaymentinvoice',
            name='reconciliation_status',
            field=models.SmallIntegerField(choices=[(0, 'not reconciliated'), (1, 'reconciliated'), (2, 'refunded'), (3, 'cancelled')], db_column='ReconciliationStatus'),
        ),
        migrations.AlterField(
            model_name='paymentinvoice',
            name='reconciliation_status',
            field=models.SmallIntegerField(choices=[(0, 'not reconciliated'), (1, 'reconciliated'), (2, 'refunded'), (3, 'cancelled')], db_column='ReconciliationStatus'),
        ),
        migrations.CreateModel(
            name='PaymentInvoiceMutation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('mutation', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='payment_invoices', to='core.MutationLog')),
                ('payment_invoice', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='mutations', to='invoice.PaymentInvoice')),
            ],
            options={
                'db_table': 'paymentinvoice_PaymentInvoiceMutation',
                'managed': True,
            },
            bases=(models.Model, core.models.ObjectMutation),
        ),
        migrations.CreateModel(
            name='DetailPaymentInvoiceMutation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('detail_payment_invoice', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='mutations', to='invoice.DetailPaymentInvoice')),
                ('mutation', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='detail_payment_invoices', to='core.MutationLog')),
            ],
            options={
                'db_table': 'paymentinvoice_DetailPaymentInvoiceMutation',
                'managed': True,
            },
            bases=(models.Model, core.models.ObjectMutation),
        ),
    ]