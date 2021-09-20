from invoice_payment.models import Invoice
from invoice_payment.validation.base import BaseInvoiceValidation


class InvoiceModelValidation(BaseInvoiceValidation):
    OBJECT_TYPE = Invoice
