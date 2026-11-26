import graphene
import json
from django.core.serializers.json import DjangoJSONEncoder
from graphene_django import DjangoObjectType

from core import prefix_filterset, ExtendedConnection
from invoice.gql.filter_mixin import GenericFilterGQLTypeMixin
from invoice.models import Invoice, InvoiceLineItem, InvoicePayment, InvoiceEvent, InvoiceMutation, \
    InvoicePaymentMutation, InvoiceLineItemMutation, InvoiceEventMutation
from invoice.gql.gfk_outputs import target_dict
from core.gql import ScopedQuerysetMixin


class InvoiceGQLType(ScopedQuerysetMixin, DjangoObjectType, GenericFilterGQLTypeMixin):
    subject = graphene.JSONString()
    subject_type = graphene.Int()
    subject_type_name = graphene.String()
    thirdparty = graphene.JSONString()
    thirdparty_type = graphene.Int()
    thirdparty_type_name = graphene.String()

    def resolve_subject_type(root, info):
        if root.subject_type:
            return root.subject_type.id

    def resolve_subject_type_name(root, info):
        if root.subject_type:
            return root.subject_type.name

    def resolve_thirdparty_type(root, info):
        if root.thirdparty_type:
            return root.thirdparty_type.id

    def resolve_thirdparty_type_name(root, info):
        if root.thirdparty_type:
            return root.thirdparty_type.name

    def resolve_subject(root, info):
        if root.subject:
            subject_object_dict = target_dict(root.subject)
            if root.subject_type.name == "family":
                head = root.subject.head_insuree
                subject_object_dict['headInsuree'] = {
                    'id': head.id, 'chfId': head.chf_id, 'uuid': head.uuid,
                    'lastName': head.last_name, 'otherNames': head.other_names,
                } if head and head.validity_to is None else {}
            subject_object_dict = json.dumps(subject_object_dict, cls=DjangoJSONEncoder)
            return subject_object_dict

    def resolve_thirdparty(root, info):
        if root.thirdparty:
            thirdparty_object_dict = target_dict(root.thirdparty)
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


class InvoiceLineItemGQLType(ScopedQuerysetMixin, DjangoObjectType, GenericFilterGQLTypeMixin):
    line = graphene.JSONString()
    line_type = graphene.Int()
    line_type_name = graphene.String()

    def resolve_line_type(root, info):
        if root.line_type:
            return root.line_type.id

    def resolve_line_type_name(root, info):
        if root.line_type:
            return root.line_type.name

    def resolve_line(root, info):
        if root.line:
            line_object_dict = target_dict(root.line)
            line_object_dict = json.dumps(line_object_dict, cls=DjangoJSONEncoder)
            return line_object_dict

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
