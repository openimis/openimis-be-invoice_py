import graphene

from core.schema import signal_mutation_module_validate
from invoice.gql import query_mixins
from invoice.gql.invoice import GenerateTimeframeInvoices
from invoice.gql.invoice_event.mutation import CreateInvoiceEventMutation
from invoice.gql.invoice_payment.mutation import CreateInvoicePaymentMutation, UpdateInvoicePaymentMutation, \
    DeleteInvoicePaymentMutation
from invoice.models import InvoicePayment, InvoicePaymentMutation, InvoiceEventMutation, InvoiceEvent


class Query(
    query_mixins.InvoiceQueryMixin,
    query_mixins.InvoiceLineItemQueryMixin,
    query_mixins.InvoicePaymentQueryMixin,
    query_mixins.InvoiceEventQueryMixin,
    graphene.ObjectType
):
    pass


class Mutation(graphene.ObjectType):
    generate_invoices_for_time_period = GenerateTimeframeInvoices.Field()
    create_invoice_payment = CreateInvoicePaymentMutation.Field()
    update_invoice_payment = UpdateInvoicePaymentMutation.Field()
    delete_invoice_payment = DeleteInvoicePaymentMutation.Field()

    create_invoice_event_message = CreateInvoiceEventMutation.Field()


def _on_mutation_log(mutation_model, model, obj_type, sender, **kwargs):
    uuids = kwargs['data'].get('ids', [])
    if not uuids:
        uuid = kwargs['data'].get('id', None)
        uuids = [uuid] if uuid else []
    if not uuids:
        return []
    impacted = model.objects.filter(uuid__in=uuids).all()
    for item in impacted:
        mutation_model.objects.create(
            **{obj_type: item, 'mutation_id':kwargs['mutation_log_id']}
        )
    return []


def on_invoice_payment_mutation(sender, **kwargs):
    if kwargs.get('mutation_class', None) \
            in ('CreateInvoicePaymentMutation', 'UpdateInvoicePaymentMutation', 'DeleteInvoicePaymentMutation'):
        return _on_mutation_log(InvoicePaymentMutation, InvoicePayment, 'invoice_payment', sender, **kwargs)

    if kwargs.get('mutation_class', None) in ('CreateInvoiceEventMutation'):
        return _on_mutation_log(InvoiceEventMutation, InvoiceEvent, 'invoice_event', sender, **kwargs)

    return []


signal_mutation_module_validate["invoice"].connect(on_invoice_payment_mutation)
