from typing import Dict, Union, List

from invoice.models import Bill, BillItem
from invoice.services.base import BaseService
from invoice.services.service_utils import _get_generic_type
from invoice.validation.bill import BillModelValidation, BillItemStatus
from core.signals import *


class BillService(BaseService):

    OBJECT_TYPE = Bill

    def __init__(self, user, validation_class: BillModelValidation = BillModelValidation):
        super().__init__(user, validation_class)
        self.validation_class = validation_class

    def _base_payload_adjust(self, bill_data):
        return self._evaluate_generic_types(bill_data)

    def bill_validate_items(self, bill: Bill):
        # TODO: Implement after calculation rules available
        pass

    def bill_match_items(self, bill: Bill) \
            -> Dict[str, Union[BillItemStatus, Dict[BillItem, List[BillItemStatus]]]]:
        """
        Check if items related to bill are valid.
        @param bill: Bill object
        @return: Dict with two keys, 'subject_status' containing information if bill subject is valid and
        'line_items', containing information about statuses of lines connected to bill items.
        """
        match_result = {
            'subject': self.validation_class.validate_subject(bill),
            'line_items': self.validation_class.validate_line_items(bill)
        }
        return match_result

    def billTaxCalculation(self, bill: Bill):
        # TODO: Implement after calculation rules available
        pass

    @classmethod
    @register_service_signal('signal_after_invoice_module_bill_creation_from_calculation_run_service')
    def bill_creation_from_calculation(cls, **kwargs):
        """
        It sends the signal_after_invoice_module_bill_creation_from_calculation_run_service
        signal which should inform the relevant calculation rule that bills need to be generated.
        """
        pass

    def _evaluate_generic_types(self, bill_data):
        if 'subject_type' in bill_data.keys():
            bill_data['subject_type'] = _get_generic_type(bill_data['subject_type'])

        if 'thirdparty_type' in bill_data.keys():
            bill_data['thirdparty_type'] = _get_generic_type(bill_data['thirdparty_type'])

        return bill_data
