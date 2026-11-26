import graphene
import json
from django.core.serializers.json import DjangoJSONEncoder
from graphene_django import DjangoObjectType

from core import prefix_filterset, ExtendedConnection
from invoice.gql.filter_mixin import GenericFilterGQLTypeMixin
from invoice.models import Bill, \
    BillItem, BillEvent, BillPayment
from invoice.gql.gfk_outputs import target_dict
from core.gql import ScopedQuerysetMixin


class BillGQLType(ScopedQuerysetMixin, DjangoObjectType, GenericFilterGQLTypeMixin):
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
            if root.subject_type.name == "batch run" and subject_object_dict.get('locationId', None):
                location = root.subject.location
                subject_object_dict['location'] = (
                    {'code': location.code, 'name': location.name} if location.validity_to is None else None
                )
            subject_object_dict = json.dumps(subject_object_dict, cls=DjangoJSONEncoder)
            return subject_object_dict

    def resolve_thirdparty(root, info):
        if root.thirdparty:
            thirdparty_object_dict = target_dict(root.thirdparty)
            thirdparty_object_dict = json.dumps(thirdparty_object_dict, cls=DjangoJSONEncoder)
            return thirdparty_object_dict

    class Meta:
        model = Bill
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            **GenericFilterGQLTypeMixin.get_base_filters_invoice(),
            "date_bill": ["exact", "lt", "lte", "gt", "gte"],
        }

        connection_class = ExtendedConnection

        @classmethod
        def get_queryset(cls, queryset, info):
            return Bill.get_queryset(queryset, info)


class BillItemGQLType(ScopedQuerysetMixin, DjangoObjectType, GenericFilterGQLTypeMixin):
    line_type = graphene.Int()
    line_type_name = graphene.String()
    line = graphene.JSONString()

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
        model = BillItem
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            **GenericFilterGQLTypeMixin.get_base_filters_invoice_line_item(),
            **prefix_filterset("bill__", BillGQLType._meta.filter_fields),
        }

        connection_class = ExtendedConnection

        @classmethod
        def get_queryset(cls, queryset, info):
            return BillItem.get_queryset(queryset, info)


class BillPaymentGQLType(DjangoObjectType, GenericFilterGQLTypeMixin):
    class Meta:
        model = BillPayment
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            **GenericFilterGQLTypeMixin.get_base_filters_invoice_payment(),
            **prefix_filterset("bill__", BillGQLType._meta.filter_fields),
        }

        connection_class = ExtendedConnection

        @classmethod
        def get_queryset(cls, queryset, info):
            return BillPayment.get_queryset(queryset, info)


class BillEventGQLType(DjangoObjectType, GenericFilterGQLTypeMixin):
    class Meta:
        model = BillEvent
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            **prefix_filterset("bill__", BillGQLType._meta.filter_fields),
            **GenericFilterGQLTypeMixin.get_base_filters_invoice_event(),
        }

        connection_class = ExtendedConnection

        @classmethod
        def get_queryset(cls, queryset, info):
            return BillEvent.get_queryset(queryset, info)
