import graphene
from django.contrib.contenttypes.models import ContentType
from graphene_django import DjangoObjectType

from core import prefix_filterset, ExtendedConnection
from invoice.gql.filter_mixin import GenericFilterGQLTypeMixin
from invoice.models import Bill, \
    BillItem, BillEvent, BillPayment


class BillGQLType(DjangoObjectType, GenericFilterGQLTypeMixin):

    subject_type = graphene.Int()
    def resolve_subject_type(root, info):
        return root.subject_type.id

    sender_type = graphene.Int()
    def resolve_recipient_type(root, info):
        return root.sender_type.id

    class Meta:
        model = Bill
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            **GenericFilterGQLTypeMixin.get_base_filters_invoice(),
            "sender_id": ["exact"],
            "sender_type": ["exact"],
            "code_sdr": ["exact", "istartswith", "icontains", "iexact"],
            "date_bill": ["exact", "lt", "lte", "gt", "gte"],
            "currency_sdr_code": ["exact"],
        }

        connection_class = ExtendedConnection

        @classmethod
        def get_queryset(cls, queryset, info):
            return Bill.get_queryset(queryset, info)


class BillItemGQLType(DjangoObjectType, GenericFilterGQLTypeMixin):

    line_type = graphene.Int()
    def resolve_line_type(root, info):
        return root.line_type.id

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
            "code_sdr": ["istartswith", "icontains", "iexact"],
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
