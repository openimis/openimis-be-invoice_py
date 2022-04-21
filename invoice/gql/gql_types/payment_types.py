import json
import graphene

from django.core.serializers.json import DjangoJSONEncoder
from graphene_django import DjangoObjectType

from core import prefix_filterset, ExtendedConnection
from invoice.gql.filter_mixin import GenericFilterGQLTypeMixin
from invoice.models import PaymentInvoice, DetailPaymentInvoice
from invoice.utils import underscore_to_camel


class PaymentInvoiceGQLType(DjangoObjectType, GenericFilterGQLTypeMixin):

    class Meta:
        model = PaymentInvoice
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            **GenericFilterGQLTypeMixin.get_base_filters_payment_invoice(),
        }

        connection_class = ExtendedConnection

        @classmethod
        def get_queryset(cls, queryset, info):
            return PaymentInvoice.get_queryset(queryset, info)


class DetailPaymentInvoiceGQLType(DjangoObjectType, GenericFilterGQLTypeMixin):

    subject_type = graphene.Int()
    def resolve_subject_type(root, info):
        return root.subject_type.id

    subject_type_name = graphene.String()
    def resolve_subject_type_name(root, info):
        return root.subject_type.name

    subject = graphene.JSONString()
    def resolve_subject(root, info):
        subject_object_dict = root.subject.__dict__
        subject_object_dict.pop('_state')
        subject_object_dict = {
            underscore_to_camel(k): v for k, v in list(subject_object_dict.items())
        }
        subject_object_dict = json.dumps(subject_object_dict, cls=DjangoJSONEncoder)
        return subject_object_dict

    class Meta:
        model = DetailPaymentInvoice
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            **GenericFilterGQLTypeMixin.get_base_filters_detail_invoice_payment(),
            **prefix_filterset("payment__", PaymentInvoiceGQLType._meta.filter_fields),
        }

        connection_class = ExtendedConnection

        @classmethod
        def get_queryset(cls, queryset, info):
            return DetailPaymentInvoice.get_queryset(queryset, info)
