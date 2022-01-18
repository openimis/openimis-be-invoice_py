from typing import Union, List

from invoice.models import Invoice, InvoiceLineItem
from core.services import BaseService
from core.services.utils import get_generic_type
from invoice.validation.invoice import InvoiceModelValidation, InvoiceItemStatus
from core.signals import *


class InvoiceService(BaseService):

    OBJECT_TYPE = Invoice

    def __init__(self, user, validation_class: InvoiceModelValidation = InvoiceModelValidation):
        super().__init__(user, validation_class)
        self.validation_class = validation_class

    def _base_payload_adjust(self, invoice_data):
        return self._evaluate_generic_types(invoice_data)

    def invoice_validate_items(self, invoice: Invoice):
        # TODO: Implement after calculation rules available
        pass

    def invoice_match_items(self, invoice: Invoice) \
            -> Dict[str, Union[InvoiceItemStatus, Dict[InvoiceLineItem, List[InvoiceItemStatus]]]]:
        """
        Check if items related to invoice are valid.
        @param invoice: Invoice object
        @return: Dict with two keys, 'subject_status' containing information if invoice subject is valid and
        'line_items', containing information about statuses of lines connected to invoice items.
        """
        match_result = {
            'subject': self.validation_class.validate_subject(invoice),
            'line_items': self.validation_class.validate_line_items(invoice)
        }
        return match_result

    def invoiceTaxCalculation(self, invoice: Invoice):
        # TODO: Implement after calculation rules available
        pass

    @classmethod
    @register_service_signal('invoice_creation_from_calculation')
    def invoice_creation_from_calculation(cls, user, from_date, to_date):
        """
        It sends the invoice_creation_from_calculation signal which should inform the
        relevant calculation rule that invoices need to be generated.
        """
        pass

    def _evaluate_generic_types(self, invoice_data):
        if 'subject_type' in invoice_data.keys():
            invoice_data['subject_type'] = get_generic_type(invoice_data['subject_type'])

        if 'thirdparty_type' in invoice_data.keys():
            invoice_data['thirdparty_type'] = get_generic_type(invoice_data['thirdparty_type'])

        return invoice_data
