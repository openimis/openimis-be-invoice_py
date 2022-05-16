from django.db import transaction

from core.services import BaseService
from core.services.utils import (
    check_authentication,
    output_exception,
    output_result_success,
    model_representation
)
from invoice.models import (
    Bill,
    PaymentInvoice,
    Invoice,
    DetailPaymentInvoice
)
from invoice.utils import resolve_payment_details
from invoice.validation.paymentInvoice import PaymentInvoiceModelValidation


class PaymentInvoiceService(BaseService):

    OBJECT_TYPE = PaymentInvoice

    def __init__(self, user, validation_class: PaymentInvoiceModelValidation = PaymentInvoiceModelValidation):
        super().__init__(user, validation_class)
        self.validation_class = validation_class

    @check_authentication
    def update(self, obj_data):
        raise NotImplementedError("Update method is not implemented for PaymentInvoice")

    @check_authentication
    def create_with_detail(self, payment_invoice, payment_detail):
        try:
            with transaction.atomic():
                payment = PaymentInvoice(**payment_invoice)
                payment.save(username=self.user.username)
                payment_detail.payment = payment
                payment_detail.subject = self._get_generic_object(
                    payment_detail.subject_id,
                    payment_detail.subject_type
                )
                payment_detail.save(username=self.user.username)
                dict_repr = model_representation(payment)
                dict_repr['payment_detail_uuid'] = payment_detail.uuid
                return output_result_success(dict_representation=dict_repr)
        except Exception as exc:
            return output_exception(model_name="PaymentInvoice", method="create_with_detail", exception=exc)

    @check_authentication
    def ref_received(self, payment_invoice: PaymentInvoice, payment_ref):
        try:
            with transaction.atomic():
                self.validation_class.validate_ref_received(self.user, payment_invoice, payment_ref)
                payment_invoice.code_ext = payment_ref
                return self.save_instance(payment_invoice)
        except Exception as exc:
            return output_exception(model_name="PaymentInvoice", method="ref_received", exception=exc)

    def payment_received(self, payment_invoice: PaymentInvoice, payment_status: DetailPaymentInvoice.DetailPaymentStatus):
        try:
            with transaction.atomic():
                self.validation_class.validate_receive_payment(self.user, payment_invoice)
                self._update_all_dependencies_for_payment(
                    payment_invoice,
                    payment_status,
                    Invoice.Status.PAYED
                )
                dict_repr = model_representation(payment_invoice)
                return output_result_success(dict_representation=dict_repr)
        except Exception as exc:
            return output_exception(model_name="PaymentInvoice", method="payment_received", exception=exc)

    def payment_refunded(self, payment_invoice):
        try:
            with transaction.atomic():
                self._update_all_dependencies_for_payment(
                    payment_invoice,
                    DetailPaymentInvoice.DetailPaymentStatus.REFUNDED,
                    Invoice.Status.SUSPENDED
                )
                dict_repr = model_representation(payment_invoice)
                return output_result_success(dict_representation=dict_repr)
        except Exception as exc:
            return output_exception(model_name="PaymentInvoice", method="payment_refunded", exception=exc)

    def payment_cancelled(self, payment_invoice):
        try:
            with transaction.atomic():
                self._update_all_dependencies_for_payment(
                    payment_invoice,
                    DetailPaymentInvoice.DetailPaymentStatus.CANCELLED,
                    Invoice.Status.SUSPENDED
                )
                dict_repr = model_representation(payment_invoice)
                return output_result_success(dict_representation=dict_repr)
        except Exception as exc:
            return output_exception(model_name="PaymentInvoice", method="payment_cancelled", exception=exc)

    def _update_all_dependencies_for_payment(self, payment_invoice, payment_status, invoice_status):
        invoices, bills = resolve_payment_details(payment_invoice)
        payment_details = payment_invoice.invoice_payments.all()
        self._update_detail(payment_details, payment_status)
        self._update_detail(invoices, invoice_status)
        self._update_detail(bills, invoice_status)

    def _update_detail(self, detail_collection, status):
        for detail in detail_collection:
            if detail.status != status:
                detail.status = status
                detail.save(username=self.user.username)

    @classmethod
    def _get_field_for_detail(cls, data):
        status = data.pop('status')
        subject_id = data.pop('subject_id')
        subject_type = data.pop('subject_type')
        return status, subject_id, subject_type

    @classmethod
    def _create_payment_detail(cls, user, data, payment, status, subject_id, subject_type):
        payment_detail = cls._build_payment_detail(data, payment, status, subject_id, subject_type)
        detail_payment_invoice = DetailPaymentInvoice(**payment_detail)
        detail_payment_invoice.save(username=user.username)

    @classmethod
    def _get_generic_object(cls, uuid, type):
        if type.model == 'invoice':
            object = Invoice.objects.get(id=uuid)
        else:
            object = Bill.objects.get(id=uuid)
        return object

