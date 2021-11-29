import graphene
import json
from django.core.serializers.json import DjangoJSONEncoder
from graphene_django import DjangoObjectType

from core import prefix_filterset, ExtendedConnection
from invoice.gql.filter_mixin import GenericFilterGQLTypeMixin
from invoice.models import Invoice, InvoiceLineItem, InvoicePayment, InvoiceEvent, InvoiceMutation, \
    InvoicePaymentMutation, InvoiceLineItemMutation, InvoiceEventMutation


class InvoiceGQLType(DjangoObjectType, GenericFilterGQLTypeMixin):

    subject_type = graphene.Int()
    def resolve_subject_type(root, info):
        return root.subject_type.id

    subject_type_name = graphene.String()
    def resolve_subject_type_name(root, info):
        return root.subject_type.name

    thirdparty_type = graphene.Int()
    def resolve_thirdparty_type(root, info):
        return root.thirdparty_type.id

    thirdparty_type_name = graphene.String()
    def resolve_thirdparty_type_name(root, info):
        return root.thirdparty_type.name

    subject = graphene.JSONString()
    def resolve_subject(root, info):
        subject_object_dict = root.subject.__dict__
        subject_object_dict.pop('_state')
        subject_object_dict = json.dumps(subject_object_dict, cls=DjangoJSONEncoder)
        return subject_object_dict

    thirdparty = graphene.JSONString()
    def resolve_thirdparty(root, info):
        thirdparty_object_dict = root.thirdparty.__dict__
        thirdparty_object_dict.pop('_state')
        thirdparty_object_dict = json.dumps(thirdparty_object_dict, cls=DjangoJSONEncoder)
        return thirdparty_object_dict

    class Meta:
        model = Invoice
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            **GenericFilterGQLTypeMixin.get_base_filters_invoice(),
            "date_invoice": ["exact", "lt", "lte", "gt", "gte"],
        }

        connection_class = ExtendedConnection

        @classmethod
        def get_queryset(cls, queryset, info):
            return Invoice.get_queryset(queryset, info)


class InvoiceLineItemGQLType(DjangoObjectType, GenericFilterGQLTypeMixin):

    line_type = graphene.Int()
    def resolve_line_type(root, info):
        return root.line_type.id

    line_type_name = graphene.String()
    def resolve_line_type_name(root, info):
        return root.line_type.name

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
