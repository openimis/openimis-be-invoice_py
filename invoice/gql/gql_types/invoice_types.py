import graphene
from django.contrib.contenttypes.models import ContentType
from graphene_django import DjangoObjectType

from core import prefix_filterset, ExtendedConnection
from invoice.gql.filter_mixin import GenericFilterGQLTypeMixin
from invoice.models import Invoice, InvoiceLineItem, InvoicePayment, InvoiceEvent, InvoiceMutation, \
    InvoicePaymentMutation, InvoiceLineItemMutation, InvoiceEventMutation


class InvoiceGQLType(DjangoObjectType, GenericFilterGQLTypeMixin):

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
            **GenericFilterGQLTypeMixin.get_base_filters_invoice(),
            "recipient_id": ["exact"],
            "recipient_type": ["exact"],
            "code_rcp": ["exact", "istartswith", "icontains", "iexact"],
            "date_invoice": ["exact", "lt", "lte", "gt", "gte"],
            "currency_rcp_code": ["exact"],
        }

        connection_class = ExtendedConnection

        @classmethod
        def get_queryset(cls, queryset, info):
            return Invoice.get_queryset(queryset, info)


class InvoiceLineItemGQLType(DjangoObjectType, GenericFilterGQLTypeMixin):

    line_type = graphene.Int()
    def resolve_line_type(root, info):
        return root.line_type.id

    class Meta:
        model = InvoiceLineItem
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            **GenericFilterGQLTypeMixin.get_base_filters_invoice_line_item(),
            **prefix_filterset("invoice__", InvoiceGQLType._meta.filter_fields),
        }

        connection_class = ExtendedConnection

        @classmethod
        def get_queryset(cls, queryset, info):
            return InvoiceLineItem.get_queryset(queryset, info)


class InvoicePaymentGQLType(DjangoObjectType, GenericFilterGQLTypeMixin):

    class Meta:
        model = InvoicePayment
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            **GenericFilterGQLTypeMixin.get_base_filters_invoice_payment(),
            "code_rcp": ["istartswith", "icontains", "iexact"],
            **prefix_filterset("invoice__", InvoiceGQLType._meta.filter_fields),
        }

        connection_class = ExtendedConnection

        @classmethod
        def get_queryset(cls, queryset, info):
            return InvoicePayment.get_queryset(queryset, info)


class InvoiceEventGQLType(DjangoObjectType, GenericFilterGQLTypeMixin):

    class Meta:
        model = InvoiceEvent
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            **GenericFilterGQLTypeMixin.get_base_filters_invoice_event(),
            **prefix_filterset("invoice__", InvoiceGQLType._meta.filter_fields),
        }

        connection_class = ExtendedConnection

        @classmethod
        def get_queryset(cls, queryset, info):
            return InvoiceEvent.get_queryset(queryset, info)


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
