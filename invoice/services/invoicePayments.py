from django.db import transaction

from invoice.models import InvoicePayment, Invoice
from invoice.services.base import BaseService
from invoice.services.service_utils import _check_authentication as check_authentication, _output_exception
from invoice.validation.invoicePayment import InvoicePaymentModelValidation


class InvoicePaymentsService(BaseService):

    OBJECT_TYPE = InvoicePayment

    def __init__(self, user, validation_class: InvoicePaymentModelValidation = InvoicePaymentModelValidation):
        super().__init__(user, validation_class)
        self.validation_class = validation_class

    @check_authentication
    def update(self, obj_data):
        raise NotImplementedError("Update method is not implemented for InvoicePayment")

    @check_authentication
    def create(self, obj_data):
        raise NotImplementedError("Create method is not implemented for InvoicePayment")

    @check_authentication
    def ref_received(self, invoice_payment: InvoicePayment, payment_ref):
        try:
            with transaction.atomic():
                self.validation_class.validate_ref_received(self.user, invoice_payment, payment_ref)
                invoice_payment.code_ext = payment_ref
                return self.save_instance(invoice_payment)
        except Exception as exc:
            return _output_exception(model_name="InvoicePayment", method="ref_received", exception=exc)

    def payment_received(self, invoice_payment: InvoicePayment, payment_status: InvoicePayment.InvoicePaymentStatus):
        try:
            with transaction.atomic():
                invoice_payment.status = payment_status
                self.validation_class.validate_receive_payment(self.user, invoice_payment)

                self._update_invoice_status(invoice_payment.invoice, Invoice.InvoiceStatus.PAYED)

                invoice_payment.invoice.save(username=self.user.username)
                return self.save_instance(invoice_payment)
        except Exception as exc:
            return _output_exception(model_name="InvoicePayment", method="payment_received", exception=exc)

    def payment_refunded(self, invoice_payment):
        try:
            with transaction.atomic():
                self.validation_class.validate_refund_payment(self.user, invoice_payment)
                self._update_payment_status(invoice_payment, InvoicePayment.InvoicePaymentStatus.REFUNDED)
                self._update_invoice_status(invoice_payment.invoice, Invoice.InvoiceStatus.SUSPENDED)

                invoice_payment.invoice.save(username=self.user.username)
                return self.save_instance(invoice_payment)
        except Exception as exc:
            return _output_exception(model_name="InvoicePayment", method="payment_refunded", exception=exc)

    def payment_cancelled(self, invoice_payment):
        try:
            with transaction.atomic():
                self.validation_class.validate_cancel_payment(self.user, invoice_payment)

                self._update_payment_status(invoice_payment.invoice, InvoicePayment.InvoicePaymentStatus.CANCELLED)
                self._update_invoice_status(invoice_payment.invoice, Invoice.InvoiceStatus.SUSPENDED)

                invoice_payment.invoice.save(username=self.user.username)
                return self.save_instance(invoice_payment)
        except Exception as exc:
            return _output_exception(model_name="InvoicePayment", method="payment_refunded", exception=exc)

    def _update_payment_status(self, invoice_payment: InvoicePayment, status: InvoicePayment.InvoicePaymentStatus):
        invoice_payment.status = status

    def _update_invoice_status(self, invoice_payment: Invoice, status: Invoice.InvoiceStatus):
        invoice_payment.status = status
