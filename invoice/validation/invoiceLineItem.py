from invoice.models import InvoiceLineItem
from invoice.validation.base import BaseInvoiceValidation


class InvoiceLineItemModelValidation(BaseInvoiceValidation):
    OBJECT_TYPE = InvoiceLineItem
