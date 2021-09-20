from invoice_payment.models import InvoiceLineItem
from invoice_payment.validation.base import BaseInvoiceValidation


class InvoiceLineItemModelValidation(BaseInvoiceValidation):
    OBJECT_TYPE = InvoiceLineItem
