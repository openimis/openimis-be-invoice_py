import json

from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction

from invoice_payment.models import Invoice
from invoice_payment.validation.invoice import InvoiceModelValidation
from django.forms.models import model_to_dict


def check_authentication(function):
    def wrapper(self, *args, **kwargs):
        if type(self.user) is AnonymousUser or not self.user.id:
            return {
                "success": False,
                "message": "Authentication required",
                "detail": "PermissionDenied",
            }
        else:
            result = function(self, *args, **kwargs)
            return result
    return wrapper


def _model_representation(model):
    uuid_string = str(model.id)
    dict_representation = model_to_dict(model)
    dict_representation["id"], dict_representation["uuid"] = (str(uuid_string), str(uuid_string))
    return dict_representation


def _output_exception(model_name, method, exception):
    return {
        "success": False,
        "message": f"Failed to {method} {model_name}",
        "detail": str(exception),
        "data": "",
    }


def _output_result_success(dict_representation):
    return {
        "success": True,
        "message": "Ok",
        "detail": "",
        "data": json.loads(json.dumps(dict_representation, cls=DjangoJSONEncoder)),
    }


class InvoiceService:

    def __init__(self, user, validation_class: InvoiceModelValidation = InvoiceModelValidation):
        self.user = user
        self.validation_class = validation_class

    @check_authentication
    def create(self, invoice_data):
        try:
            with transaction.atomic():
                invoice_data = self._evaluate_generic_types(invoice_data)

                self.validation_class.validate_create(self.user, **invoice_data)
                invoice = Invoice(**invoice_data)
                return self.save_instance(invoice)
        except Exception as exc:
            return _output_exception(model_name="Invoice", method="create", exception=exc)

    @check_authentication
    def update(self, invoice_data):
        try:
            with transaction.atomic():
                invoice_data = self._evaluate_generic_types(invoice_data)

                self.validation_class.validate_update(self.user, **invoice_data)
                invoice = Invoice.objects.filter(id=invoice_data['id']).first()
                [setattr(invoice, key, invoice_data[key]) for key in invoice_data]
                return self.save_instance(invoice)
        except Exception as exc:
            return _output_exception(model_name="Invoice", method="update", exception=exc)

    @check_authentication
    def delete(self, invoice_data):
        try:
            with transaction.atomic():
                self.validation_class.validate_delete(self.user, **invoice_data)
                invoice = Invoice.objects.filter(id=invoice_data['id']).first()
                return self.delete_instance(invoice)
        except Exception as exc:
            return _output_exception(model_name="Invoice", method="delete", exception=exc)

    def save_instance(self, invoice):
        invoice.save(username=self.user.username)
        dict_repr = _model_representation(invoice)
        return _output_result_success(dict_representation=dict_repr)

    def delete_instance(self, invoice):
        invoice.delete(username=self.user.username)
        return {
            "success": True,
            "message": "Ok",
            "detail": "",
        }

    def _evaluate_generic_types(self, invoice_data):
        if 'subject_type' in invoice_data.keys():
            invoice_data['subject_type'] = ContentType.objects.get(model=invoice_data['subject_type'].lower())

        if 'recipient_type' in invoice_data.keys():
            invoice_data['recipient_type'] = ContentType.objects.get(model=invoice_data['recipient_type'].lower())
        return invoice_data
