from invoice.models import InvoiceLineItem
from invoice.validation.base import BaseModelValidation


class InvoiceLineItemModelValidation(BaseModelValidation):
    OBJECT_TYPE = InvoiceLineItem
