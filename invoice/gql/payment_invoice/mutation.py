import graphene
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError

from core.gql.gql_mutations.base_mutation import (
    BaseMutation,
    BaseHistoryModelCreateMutationMixin,
    BaseHistoryModelUpdateMutationMixin,
    BaseHistoryModelDeleteMutationMixin
)
from core.schema import OpenIMISMutation
from invoice.apps import InvoiceConfig
from invoice.gql.input_types import CreatePaymentInvoiceInputType, UpdatePaymentInvoiceInputType
from invoice.models import PaymentInvoice, PaymentInvoiceMutation


class CreatePaymentInvoiceMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_class = "CreatePaymentInvoiceMutation"
    _mutation_module = "invoice"
    _model = PaymentInvoice

    @classmethod
    def _mutate(cls, user, **data):
        client_mutation_id = data.get("client_mutation_id")
        if "client_mutation_id" in data:
            data.pop('client_mutation_id')
        if "client_mutation_label" in data:
            data.pop('client_mutation_label')
        payment_invoice = cls.create_object(user=user, object_data=data)
        if payment_invoice:
            PaymentInvoiceMutation.object_mutated(
                user,
                client_mutation_id=client_mutation_id,
                payment_invoice=payment_invoice
            )

    @classmethod
    def _validate_mutation(cls, user, **data):
        if type(user) is AnonymousUser or not user.id or not user.has_perms(
                InvoiceConfig.gql_invoice_payment_create_perms):
            raise ValidationError("mutation.authentication_required")

    class Input(CreatePaymentInvoiceInputType):
        pass


class UpdatePaymentInvoiceMutation(BaseHistoryModelUpdateMutationMixin, BaseMutation):
    _mutation_class = "UpdatePaymentInvoiceMutation"
    _mutation_module = "invoice"
    _model = PaymentInvoice

    @classmethod
    def _validate_mutation(cls, user, **data):
        if type(user) is AnonymousUser or not user.id or not user.has_perms(
                InvoiceConfig.gql_invoice_payment_update_perms):
            raise ValidationError("mutation.authentication_required")

    class Input(UpdatePaymentInvoiceInputType):
        pass


class DeletePaymentInvoiceMutation(BaseHistoryModelDeleteMutationMixin, BaseMutation):
    _mutation_class = "DeletePaymentInvoiceMutation"
    _mutation_module = "invoice"
    _model = PaymentInvoice

    @classmethod
    def _validate_mutation(cls, user, **data):
        if type(user) is AnonymousUser or not user.id or not user.has_perms(
                InvoiceConfig.gql_invoice_payment_delete_perms):
            raise ValidationError("mutation.authentication_required")

    class Input(OpenIMISMutation.Input):
        uuids = graphene.List(graphene.UUID)
