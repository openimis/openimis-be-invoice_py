import graphene
from django.contrib.contenttypes.models import ContentType
from graphene_django import DjangoObjectType

from core import prefix_filterset, ExtendedConnection
from invoice.models import Invoice, InvoiceLineItem, InvoicePayment, InvoiceEvent, InvoiceMutation, \
    InvoicePaymentMutation, InvoiceLineItemMutation, InvoiceEventMutation


class InvoiceGQLType(DjangoObjectType):

    subject_type = graphene.Int()
    def resolve_subject_type(root, info):
        return root.subject_type.id

    recipient_type = graphene.Int()
    def resolve_recipient_type(root, info):
        return root.recipient_type.id

    class Meta:
        model = Invoice
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "subject_id": ["exact"],
            "subject_type": ["exact"],
            "recipient_id": ["exact"],
            "recipient_type": ["exact"],

            "code": ["exact", "istartswith", "icontains", "iexact"],
            "code_rcp": ["exact", "istartswith", "icontains", "iexact"],
            "code_ext": ["exact", "istartswith", "icontains", "iexact"],
            "date_due": ["exact", "lt", "lte", "gt", "gte"],
            "date_invoice": ["exact", "lt", "lte", "gt", "gte"],
            "date_payed": ["exact", "lt", "lte", "gt", "gte"],

            "amount_discount": ["exact", "lt", "lte", "gt", "gte"],
            "amount_net": ["exact", "lt", "lte", "gt", "gte"],
            "amount_total": ["exact", "lt", "lte", "gt", "gte"],

            "status": ["exact"],

            "currency_rcp_code": ["exact"],
            "currency_code": ["exact"],
            "note": ["exact", "icontains"],
            "terms": ["exact", "icontains"],

            "payment_reference": ["exact", "istartswith", "icontains", "iexact"],

            "date_created": ["exact", "lt", "lte", "gt", "gte"],
            "date_updated": ["exact", "lt", "lte", "gt", "gte"],
            "is_deleted": ["exact"],
            "version": ["exact"],
        }

        connection_class = ExtendedConnection

        @classmethod
        def get_queryset(cls, queryset, info):
            return Invoice.get_queryset(queryset, info)


class InvoiceLineItemGQLType(DjangoObjectType):

    line_type = graphene.Int()
    def resolve_line_type(root, info):
        return root.line_type.id

    class Meta:
        model = InvoiceLineItem
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "line_type": ["exact"],
            "line_id": ["exact"],

            **prefix_filterset("invoice__", InvoiceGQLType._meta.filter_fields),

            "description": ["istartswith", "icontains", "iexact"],

            "ledger_account": ["istartswith", "iexact"],

            "quantity": ["exact", "lt", "lte", "gt", "gte"],
            "unit_price": ["exact", "lt", "lte", "gt", "gte"],

            "discount": ["exact", "lt", "lte", "gt", "gte"],

            "tax_rate": ["exact"],
            "amount_total": ["exact", "lt", "lte", "gt", "gte"],
            "amount_net": ["exact", "lt", "lte", "gt", "gte"],

            "date_created": ["exact", "lt", "lte", "gt", "gte"],
            "date_updated": ["exact", "lt", "lte", "gt", "gte"],
            "is_deleted": ["exact"],
            "version": ["exact"],
        }

        connection_class = ExtendedConnection

        @classmethod
        def get_queryset(cls, queryset, info):
            return InvoiceLineItem.get_queryset(queryset, info)


class InvoicePaymentGQLType(DjangoObjectType):

    class Meta:
        model = InvoicePayment
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "status": ["exact"],

            "code_ext": ["istartswith", "icontains", "iexact"],
            "code_rcp": ["istartswith", "icontains", "iexact"],
            "code_receipt": ["istartswith", "icontains", "iexact"],

            "label": ["istartswith", "iexact"],

            **prefix_filterset("invoice__", InvoiceGQLType._meta.filter_fields),

            "amount_payed": ["exact", "lt", "lte", "gt", "gte"],
            "fees": ["exact", "lt", "lte", "gt", "gte"],
            "amount_received": ["exact", "lt", "lte", "gt", "gte"],

            "date_payment": ["exact", "lt", "lte", "gt", "gte"],

            "date_created": ["exact", "lt", "lte", "gt", "gte"],
            "date_updated": ["exact", "lt", "lte", "gt", "gte"],
            "is_deleted": ["exact"],
            "version": ["exact"],
        }

        connection_class = ExtendedConnection

        @classmethod
        def get_queryset(cls, queryset, info):
            return InvoicePayment.get_queryset(queryset, info)


class InvoiceEventGQLType(DjangoObjectType):

    class Meta:
        model = InvoiceEvent
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            **prefix_filterset("invoice__", InvoiceGQLType._meta.filter_fields),
            "event_type": ["exact", "lt", "lte", "gt", "gte"],
            "message": ["istartswith", "icontains", "iexact"],

            "date_created": ["exact", "lt", "lte", "gt", "gte"],
            "date_updated": ["exact", "lt", "lte", "gt", "gte"],
            "is_deleted": ["exact"],
            "version": ["exact"],
        }

        connection_class = ExtendedConnection

        @classmethod
        def get_queryset(cls, queryset, info):
            return InvoicePayment.get_queryset(queryset, info)


class InvoiceMutationGQLType(DjangoObjectType):
    class Meta:
        model = InvoiceMutation


class InvoicePaymentMutationGQLType(DjangoObjectType):
    class Meta:
        model = InvoicePaymentMutation


class InvoiceLineItemMutationGQLType(DjangoObjectType):
    class Meta:
        model = InvoiceLineItemMutation


class InvoiceEventMutationGQLType(DjangoObjectType):
    class Meta:
        model = InvoiceEventMutation
