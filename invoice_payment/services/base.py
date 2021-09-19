from abc import ABC

from core.models import HistoryModel
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from typing import Type

from invoice_payment.services.service_utils import _check_authentication as check_authentication, _output_exception, \
    _model_representation, _output_result_success, _get_generic_type
from invoice_payment.validation.base import BaseModelValidation


class BaseService(ABC):
    """ Base service for invoice related objects. """

    @property
    def OBJECT_TYPE(self) -> Type[HistoryModel]:
        """
        Django ORM model. It's expected that it'll be inheriting from HistoryModel.
        """
        raise NotImplementedError("Class has to define OBJECT_TYPE for service.")

    def __init__(self, user, validation_class: BaseModelValidation):
        self.user = user
        self.validation_class = validation_class

    @check_authentication
    def create(self, invoice_data):
        try:
            with transaction.atomic():
                invoice_data = self._adjust_create_payload(invoice_data)

                self.validation_class.validate_create(self.user, **invoice_data)
                invoice = self.OBJECT_TYPE(**invoice_data)
                return self.save_instance(invoice)
        except Exception as exc:
            return _output_exception(model_name="Invoice", method="create", exception=exc)

    @check_authentication
    def update(self, invoice_data):
        try:
            with transaction.atomic():
                invoice_data = self._adjust_update_payload(invoice_data)
                self.validation_class.validate_update(self.user, **invoice_data)

                invoice = self.OBJECT_TYPE.objects.filter(id=invoice_data['id']).first()
                [setattr(invoice, key, invoice_data[key]) for key in invoice_data]
                return self.save_instance(invoice)
        except Exception as exc:
            return _output_exception(model_name="Invoice", method="update", exception=exc)

    @check_authentication
    def delete(self, invoice_data):
        try:
            with transaction.atomic():
                self.validation_class.validate_delete(self.user, **invoice_data)
                invoice = self.OBJECT_TYPE.objects.filter(id=invoice_data['id']).first()
                return self.delete_instance(invoice)
        except Exception as exc:
            return _output_exception(model_name="Invoice", method="delete", exception=exc)

    def save_instance(self, invoice):
        invoice.save(username=self.user.username)
        dict_repr = _model_representation(invoice)
        return _output_result_success(dict_representation=dict_repr)

    def delete_instance(self, invoice):
        invoice.delete(username=self.user.username)
        return self._build_delete_instance_payload(invoice)

    def _adjust_create_payload(self, payload_data):
        return self._base_payload_adjust(payload_data)

    def _adjust_update_payload(self, payload_data):
        return self._base_payload_adjust(payload_data)

    def _base_payload_adjust(self, invoice_data):
        return invoice_data

    def _build_delete_instance_payload(self, invoice):
        return {
            "success": True,
            "message": "Ok",
            "detail": "",
        }
