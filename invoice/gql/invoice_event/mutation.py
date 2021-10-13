from core.gql.gql_mutations.base_mutation import BaseHistoryModelCreateMutationMixin, BaseMutation, \
    BaseHistoryModelUpdateMutationMixin
from invoice.gql.input_types import CreateInvoiceEventType, UpdateInvoiceEventType
from invoice.models import InvoiceEvent, InvoiceEventMutation


class CreateInvoiceEventMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_class = "CreateInvoiceEventMutation"
    _mutation_module = "invoice"
    _model = InvoiceEvent

    @classmethod
    def _mutate(cls, user, **data):
        client_mutation_id = data.get("client_mutation_id")
        if "client_mutation_id" in data:
            data.pop('client_mutation_id')
        if "client_mutation_label" in data:
            data.pop('client_mutation_label')
        p = cls.create_object(user=user, object_data=data)
        if p:
            InvoiceEventMutation.object_mutated(
                user,
                client_mutation_id=client_mutation_id,
                invoice_event=p
            )

    class Input(CreateInvoiceEventType):
        pass
