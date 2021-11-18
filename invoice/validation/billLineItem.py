from invoice.models import BillItem
from invoice.validation.base import BaseModelValidation


class BillLineItemModelValidation(BaseModelValidation):
    OBJECT_TYPE = BillItem
