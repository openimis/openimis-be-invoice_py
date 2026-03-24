import decimal
from typing import Union, List

from simple_history.utils import bulk_create_with_history

from invoice.models import Bill, BillItem
from core.services import BaseService
from invoice.services.billLineItem import BillLineItemService
from core.services.utils import get_generic_type
from invoice.validation.bill import BillModelValidation, BillItemStatus
from core.signals import *


BULK_CREATE_BATCH_SIZE = 500

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
    @register_service_signal('signal_after_invoice_module_bill_create_service')
    def bill_create(cls, **kwargs):
        convert_results = kwargs.get('convert_results', {})
        if 'bill_data' in convert_results and 'bill_data_line' in convert_results:
            user = convert_results['user']
            # save in database this invoice and invoice line item
            bill_line_items = convert_results['bill_data_line']
            bill_service = BillService(user=user)
            bill_line_item_service = BillLineItemService(user=user)
            result_bill = bill_service.create(convert_results['bill_data'])
            if result_bill["success"] is True:
                bill_update = {
                    "id": result_bill["data"]["id"],
                    "amount_net": decimal.Decimal(0),
                    "amount_total": decimal.Decimal(0),
                    "amount_discount": decimal.Decimal(0),
                }
                for bill_line_item in bill_line_items:
                    bill_line_item["bill_id"] = result_bill["data"]["id"]
                    result_bill_line = bill_line_item_service.create(bill_line_item)
                    if result_bill_line["success"] is True:
                        bill_update["amount_net"] += decimal.Decimal(result_bill_line["data"]["amount_net"])
                        bill_update["amount_total"] += decimal.Decimal(result_bill_line["data"]["amount_total"])
                        bill_update["amount_discount"] += decimal.Decimal(0) \
                            if not result_bill_line["data"]["discount"] \
                            else decimal.Decimal(result_bill_line["data"]["discount"])
                generated_bill = bill_service.update(bill_update)
                return generated_bill

    def _evaluate_generic_types(self, bill_data):
        if 'subject_type' in bill_data.keys():
            bill_data['subject_type'] = get_generic_type(bill_data['subject_type'])

        if 'thirdparty_type' in bill_data.keys():
            bill_data['thirdparty_type'] = get_generic_type(bill_data['thirdparty_type'])

        return bill_data

    @classmethod
    def bulk_create_bills(cls, bills):
        created = bulk_create_with_history(bills, Bill, batch_size=BULK_CREATE_BATCH_SIZE)
        # Re-fetch codes assigned by DB trigger and patch history records.
        # Chunked to stay under MSSQL's ~2100 parameter limit for IN clauses.
        empty_code_bills = [b for b in created if not b.code]
        history_model = Bill.history.model
        for i in range(0, len(empty_code_bills), BULK_CREATE_BATCH_SIZE):
            chunk = empty_code_bills[i:i + BULK_CREATE_BATCH_SIZE]
            chunk_ids = [b.id for b in chunk]
            refreshed = {
                b.id: b.code
                for b in Bill.objects.filter(id__in=chunk_ids).only('id', 'code')
            }
            for b in chunk:
                if b.id in refreshed:
                    b.code = refreshed[b.id]
            # Patch history creation records with DB-assigned codes.
            history_records = list(history_model.objects.filter(
                id__in=chunk_ids, history_type='+', code='',
            ))
            for h in history_records:
                code = refreshed.get(h.id)
                if code:
                    h.code = code
            updated_history = [h for h in history_records if h.code]
            if updated_history:
                history_model.objects.bulk_update(updated_history, ['code'])
        return created

    @classmethod
    def bulk_create_bill_items(cls, bill_items):
        return bulk_create_with_history(bill_items, BillItem, batch_size=BULK_CREATE_BATCH_SIZE)
