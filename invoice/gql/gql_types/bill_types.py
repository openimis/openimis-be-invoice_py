import graphene
import json
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from graphene_django import DjangoObjectType

from core import prefix_filterset, ExtendedConnection
from invoice.gql.filter_mixin import GenericFilterGQLTypeMixin
from invoice.models import Bill, \
    BillItem, BillEvent, BillPayment
from invoice.utils import underscore_to_camel
from location.models import Location
from product.models import Product


class BillGQLType(DjangoObjectType, GenericFilterGQLTypeMixin):

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
        subject_object_dict = {
            underscore_to_camel(k): v for k, v in list(subject_object_dict.items())
        }
        if root.subject_type.name == "batch run":
            location = Location.objects.filter(id=subject_object_dict['locationId'], validity_to__isnull=True)
            location = location.values('code', 'name')
            subject_object_dict['location'] = {
                underscore_to_camel(k): v for k, v in location.first().items()
            }
        subject_object_dict = json.dumps(subject_object_dict, cls=DjangoJSONEncoder)
        return subject_object_dict

    thirdparty = graphene.JSONString()
    def resolve_thirdparty(root, info):
        thirdparty_object_dict = root.thirdparty.__dict__
        thirdparty_object_dict.pop('_state')
        thirdparty_object_dict = {
            underscore_to_camel(k): v for k, v in list(thirdparty_object_dict.items())
        }
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


class BillItemGQLType(DjangoObjectType, GenericFilterGQLTypeMixin):

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
