import graphene

from core.gql.gql_mutations.base_mutation import BaseMutation, BaseCreateMutationMixin, BaseUpdateMutationMixin, \
    BaseHistoryModelCreateMutationMixin, BaseHistoryModelUpdateMutationMixin, BaseHistoryModelDeleteMutationMixin
from core.schema import OpenIMISMutation
from invoice.gql.input_types import CreatePaymentInputType, UpdatePaymentInputType
from invoice.models import InvoicePayment, InvoicePaymentMutation


class CreateInvoicePaymentMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_class = "CreateInvoicePaymentMutation"
    _mutation_module = "invoice"
    _model = InvoicePayment

    @classmethod
    def _mutate(cls, user, **data):
        client_mutation_id = data.get("client_mutation_id")
        if "client_mutation_id" in data:
            data.pop('client_mutation_id')
        if "client_mutation_label" in data:
            data.pop('client_mutation_label')
        p = cls.create_object(user=user, object_data=data)
        if p:
            InvoicePaymentMutation.object_mutated(
                user,
                client_mutation_id=client_mutation_id,
                invoice_payment=p
            )

    class Input(CreatePaymentInputType):
        pass


class UpdateInvoicePaymentMutation(BaseHistoryModelUpdateMutationMixin, BaseMutation):
    _mutation_class = "UpdateInvoicePaymentMutation"
    _mutation_module = "invoice"
    _model = InvoicePayment

    class Input(UpdatePaymentInputType):
        pass


class DeleteInvoicePaymentMutation(BaseHistoryModelDeleteMutationMixin, BaseMutation):
    _mutation_class = "DeleteInvoicePayment"
    _mutation_module = "contract"
    _model = InvoicePayment

    class Input(OpenIMISMutation.Input):
        uuids = graphene.List(graphene.UUID)
