import graphene
import json
from django.core.serializers.json import DjangoJSONEncoder
from graphene_django import DjangoObjectType

from core import prefix_filterset, ExtendedConnection
from insuree.models import Insuree
from invoice.gql.filter_mixin import GenericFilterGQLTypeMixin
from invoice.models import Invoice, InvoiceLineItem, InvoicePayment, InvoiceEvent, InvoiceMutation, \
    InvoicePaymentMutation, InvoiceLineItemMutation, InvoiceEventMutation
from invoice.utils import underscore_to_camel


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

        key_values = list(subject_object_dict.items())
        subject_object_dict.clear()
        for k, v in key_values:
            new_key = underscore_to_camel(k)
            subject_object_dict[new_key] = v

        # when we have family - we need for contribution nested head insuree data
        if root.subject_type.name == "family":
            insuree = Insuree.objects.filter(id=subject_object_dict['headInsureeId'], validity_to__isnull=True)
            insuree = insuree.values('id', 'chf_id', 'uuid', 'last_name', 'other_names')
            insuree_dict = insuree.first()
            key_values = list(insuree_dict.items())
            insuree_dict.clear()
            for k, v in key_values:
                new_key = underscore_to_camel(k)
                insuree_dict[new_key] = v
            subject_object_dict["headInsuree"] = insuree_dict

        subject_object_dict = json.dumps(subject_object_dict, cls=DjangoJSONEncoder)
        return subject_object_dict

    thirdparty = graphene.JSONString()
    def resolve_thirdparty(root, info):
        thirdparty_object_dict = root.thirdparty.__dict__
        thirdparty_object_dict.pop('_state')
        key_values = list(thirdparty_object_dict.items())
        thirdparty_object_dict.clear()
        for k, v in key_values:
            new_key = underscore_to_camel(k)
            thirdparty_object_dict[new_key] = v
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

    line = graphene.JSONString()
    def resolve_line(root, info):
        line_object_dict = root.line.__dict__
        line_object_dict.pop('_state')
        key_values = list(line_object_dict.items())
        line_object_dict.clear()
        for k, v in key_values:
            new_key = underscore_to_camel(k)
            line_object_dict[new_key] = v
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
