from typing import Type

from core.models import HistoryModel
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from invoice_payment.models import Invoice
from invoice_payment.services.base import BaseService
from invoice_payment.services.service_utils import _check_authentication as check_authentication, _output_exception, \
    _model_representation, _output_result_success, _get_generic_type
from invoice_payment.validation.invoice import InvoiceModelValidation


class InvoiceService(BaseService):

    OBJECT_TYPE = Invoice

    def __init__(self, user, validation_class: InvoiceModelValidation = InvoiceModelValidation):
        super().__init__(user, validation_class)

    def _base_payload_adjust(self, invoice_data):
        return self._evaluate_generic_types(invoice_data)

    def _evaluate_generic_types(self, invoice_data):
        if 'subject_type' in invoice_data.keys():
            invoice_data['subject_type'] = _get_generic_type(invoice_data['subject_type'])

        if 'recipient_type' in invoice_data.keys():
            invoice_data['recipient_type'] = _get_generic_type(invoice_data['recipient_type'])

        return invoice_data

