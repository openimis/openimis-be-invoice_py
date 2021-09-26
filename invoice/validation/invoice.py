from invoice.models import Invoice
from invoice.validation.base import BaseInvoiceValidation


class InvoiceModelValidation(BaseInvoiceValidation):
    OBJECT_TYPE = Invoice
