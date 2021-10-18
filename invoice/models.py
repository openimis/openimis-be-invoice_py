from enum import IntEnum

from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from graphql import ResolveInfo

from core.models import HistoryBusinessModel, HistoryModel, UUIDModel, ObjectMutation, MutationLog
from core.fields import DateTimeField, DateField
from datetime import date
from jsonfallback.fields import FallbackJSONField
from invoice.apps import InvoiceConfig
from django.utils.translation import gettext as _
# Create your models here.
from invoice.mixins import GenericInvoiceQuerysetMixin, GenericInvoiceManager


def get_default_currency():
    return InvoiceConfig.default_currency_code


class GenericInvoice(GenericInvoiceQuerysetMixin, HistoryBusinessModel):
    class Status(models.IntegerChoices):
        DRAFT = 0, _('draft')
        VALIDATED = 1, _('validated')
        PAYED = 2, _('payed')
        CANCELLED = 3, _('cancelled')
        DELETED = 4, _('deleted')
        SUSPENDED = 5, _('suspended')

    code = models.CharField(db_column='Code', max_length=255, null=False)
    code_ext = models.CharField(db_column='CodeExt', max_length=255, null=True)

    date_due = DateField(db_column='DateDue', null=True)

    date_payed = DateField(db_column='DatePayed', null=True)

    amount_discount = models.DecimalField(
        db_column='AmountDiscount', max_digits=18, decimal_places=2, null=True, default=0.0)
    amount_net = models.DecimalField(
        db_column='AmountNet', max_digits=18, decimal_places=2, default=0.0)
    amount_total = models.DecimalField(
        db_column='AmountTotal', max_digits=18, decimal_places=2, default=0.0)

    tax_analysis = FallbackJSONField(db_column='TaxAnalysis', null=True)

    status = models.SmallIntegerField(
        db_column='Status', null=False, choices=Status.choices, default=Status.DRAFT)

    currency_code = models.CharField(
        db_column='CurrencyCode', null=False, max_length=255, default=get_default_currency)

    note = models.TextField(db_column='Note', blank=True, null=True)
    terms = models.TextField(db_column='Terms', blank=True, null=True)

    payment_reference = models.CharField(db_column='PaymentReference', max_length=255, null=True)

    class Meta:
        abstract = True


class GenericInvoiceLineItem(GenericInvoiceQuerysetMixin, HistoryBusinessModel):
    code = models.CharField(db_column='Code', max_length=255, null=False)

    description = models.TextField(db_column='Description', blank=True, null=True)
    details = FallbackJSONField(db_column='Details', null=True)

    ledger_account = models.CharField(db_column='LedgerAccount', max_length=255, null=True)

    quantity = models.IntegerField(db_column='Quantity', default=0.0)
    unit_price = models.DecimalField(db_column='UnitPrice', max_digits=18, decimal_places=2, default=0.0)

    discount = models.DecimalField(db_column='Discount', max_digits=18, decimal_places=2, default=0.0)

    tax_rate = models.UUIDField(db_column="CalculationUUID", null=True)
    tax_analysis = FallbackJSONField(db_column='TaxAnalysis', null=True)

    amount_total = models.DecimalField(db_column='AmountTotal', max_digits=18, decimal_places=2, null=True)
    amount_net = models.DecimalField(db_column='AmountNet', max_digits=18, decimal_places=2, default=0.0)

    objects = GenericInvoiceManager()

    class Meta:
        abstract = True


class GenericInvoicePayment(GenericInvoiceQuerysetMixin, HistoryModel):
    class PaymentStatus(models.IntegerChoices):
        REJECTED = 0, _('rejected')
        ACCEPTED = 1, _('accepted')
        REFUNDED = 2, _('refunded')
        CANCELLED = 3, _('cancelled')

    code_ext = models.CharField(db_column='CodeExt', max_length=255, null=True)
    code_receipt = models.CharField(db_column='CodeReceipt', max_length=255, null=True)

    label = models.CharField(db_column='Label', max_length=255, null=True)

    status = models.SmallIntegerField(db_column='Status', null=False, choices=PaymentStatus.choices)

    amount_payed = models.DecimalField(db_column='AmountPayed', max_digits=18, decimal_places=2, null=True)
    fees = models.DecimalField(db_column='Fees', max_digits=18, decimal_places=2, null=True)
    amount_received = models.DecimalField(db_column='AmountReceived', max_digits=18, decimal_places=2, null=True)

    date_payment = DateField(db_column='DatePayment', null=True)

    objects = GenericInvoiceManager()

    class Meta:
        abstract = True


class GenericInvoiceEvent(GenericInvoiceQuerysetMixin, HistoryModel):
    class EventType(models.IntegerChoices):
        MESSAGE = 0, _('message')
        STATUS = 1, _('status')
        WARNING = 2, _('warning')
        PAYMENT = 3, _('payment')
        PAYMENT_ERROR = 4, _('payment_error')

    message = models.CharField(db_column='Message', max_length=500, null=True)
    event_type = models.SmallIntegerField(
        db_column='Status', null=False, choices=EventType.choices, default=EventType.MESSAGE)

    objects = GenericInvoiceManager()

    class Meta:
        abstract = True


class Invoice(GenericInvoice):
    subject_type = models.OneToOneField(ContentType, models.DO_NOTHING,
                                        db_column='SubjectType', null=True, related_name='subject_type')
    subject_id = models.CharField(db_column='SubjectId', max_length=255, null=True)  # object is referenced by uuid
    subject = GenericForeignKey('subject_type', 'subject_id')

    recipient_type = models.OneToOneField(ContentType, models.DO_NOTHING,
                                          db_column='RecipientType', null=True, related_name='recipient_type')
    recipient_id = models.CharField(db_column='RecipientId', max_length=255, null=True)   # object is referenced by uuid
    recipient = GenericForeignKey('recipient_type', 'recipient_id')

    code_rcp = models.CharField(db_column='CodeRcp', max_length=255, null=True)

    date_invoice = DateField(db_column='DateInvoice', default=date.today, null=True)

    currency_rcp_code = models.CharField(
        db_column='CurrencyRcpCode', null=False, max_length=255, default=get_default_currency)

    class Meta:
        managed = True
        db_table = 'tblInvoice'


class InvoiceLineItem(GenericInvoiceLineItem):
    line_type = models.OneToOneField(
        ContentType, models.DO_NOTHING, db_column='LineType', null=True, related_name='line_type')
    line_id = models.CharField(db_column='LineId', max_length=255, null=True)  # object is referenced by uuid
    line = GenericForeignKey('line_type', 'line_id')

    invoice = models.ForeignKey(Invoice, models.DO_NOTHING, db_column='InvoiceId', related_name="line_items")

    objects = GenericInvoiceManager()

    class Meta:
        managed = True
        db_table = 'tblInvoiceLineItem'


class InvoicePayment(GenericInvoicePayment):
    invoice = models.ForeignKey(Invoice, models.DO_NOTHING, db_column='InvoiceId', related_name="payments")
    code_rcp = models.CharField(db_column='CodeRcp', max_length=255, null=True)

    objects = GenericInvoiceManager()

    class Meta:
        managed = True
        db_table = 'tblInvoicePayment'


class InvoiceEvent(GenericInvoiceEvent):
    invoice = models.ForeignKey(Invoice, models.DO_NOTHING, db_column='InvoiceId', related_name="events")

    class Meta:
        managed = True
        db_table = 'tblInvoiceEvent'


class Bill(GenericInvoice):
    subject_type = models.OneToOneField(ContentType, models.DO_NOTHING,
                                        db_column='SubjectType', null=True, related_name='subject_type_bill')
    subject_id = models.CharField(db_column='SubjectId', max_length=255, null=True)  # object is referenced by uuid
    subject = GenericForeignKey('subject_type', 'subject_id')

    sender_type = models.OneToOneField(ContentType, models.DO_NOTHING,
                                       db_column='SenderType', null=True, related_name='sender_type')
    sender_id = models.CharField(db_column='SenderId', max_length=255, null=True)  # object is referenced by uuid
    sender = GenericForeignKey('sender_type', 'sender_id')

    code_sdr = models.CharField(db_column='CodeSdr', max_length=255, null=True)

    date_invoice = DateField(db_column='DateInvoice', default=date.today, null=True)

    currency_sdr_code = models.CharField(
        db_column='CurrencySdrCode', null=False, max_length=255, default=get_default_currency)

    class Meta:
        managed = True
        db_table = 'tblBill'


class BillItem(GenericInvoiceLineItem):
    line_type = models.OneToOneField(
        ContentType, models.DO_NOTHING, db_column='LineType', null=True, related_name='line_type_bill')
    line_id = models.CharField(db_column='LineId', max_length=255, null=True)  # object is referenced by uuid
    line = GenericForeignKey('line_type', 'line_id')

    bill = models.ForeignKey(Bill, models.DO_NOTHING, db_column='BillId', related_name="line_items_bill")

    objects = GenericInvoiceManager()

    class Meta:
        managed = True
        db_table = 'tblBillLineItem'


class BillPayment(GenericInvoicePayment):
    bill = models.ForeignKey(Bill, models.DO_NOTHING, db_column='BillId', related_name="payments_bill")
    code_sdr = models.CharField(db_column='CodeSdr', max_length=255, null=True)

    objects = GenericInvoiceManager()

    class Meta:
        managed = True
        db_table = 'tblBillPayment'


class BillEvent(GenericInvoiceEvent):
    bill = models.ForeignKey(Bill, models.DO_NOTHING, db_column='BillId', related_name="events_bill")

    class Meta:
        managed = True
        db_table = 'tblBillEvent'


class InvoiceMutation(UUIDModel, ObjectMutation):
    invoice = models.ForeignKey(Invoice, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(MutationLog, models.DO_NOTHING, related_name='invoices')

    class Meta:
        managed = True
        db_table = "invoice_invoiceMutation"


class InvoicePaymentMutation(UUIDModel, ObjectMutation):
    invoice_payment = models.ForeignKey(InvoicePayment, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(MutationLog, models.DO_NOTHING, related_name='invoice_payments')

    class Meta:
        managed = True
        db_table = "invoice_InvoicePaymentMutation"


class InvoiceLineItemMutation(UUIDModel, ObjectMutation):
    invoice_line_items = models.ForeignKey(InvoiceLineItem, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(MutationLog, models.DO_NOTHING, related_name='invoice_line_items')

    class Meta:
        managed = True
        db_table = "invoice_InvoiceLineItemsMutation"


class InvoiceEventMutation(UUIDModel, ObjectMutation):
    invoice_event = models.ForeignKey(InvoiceEvent, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(MutationLog, models.DO_NOTHING, related_name='event_messages')

    class Meta:
        managed = True
        db_table = "invoice_InvoiceEventMutation"
