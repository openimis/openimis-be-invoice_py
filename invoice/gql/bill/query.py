import graphene
from django.contrib.auth.models import AnonymousUser

from core.schema import OrderedDjangoFilterConnectionField
from core.utils import append_validity_filter
from invoice.apps import InvoiceConfig
from invoice.gql.gql_types.bill_types import BillGQLType
from invoice.models import Bill
import graphene_django_optimizer as gql_optimizer


class BillQueryMixin:
    bill = OrderedDjangoFilterConnectionField(
        BillGQLType,
        orderBy=graphene.List(of_type=graphene.String),
        dateValidFrom__Gte=graphene.DateTime(),
        dateValidTo__Lte=graphene.DateTime(),
        applyDefaultValidityFilter=graphene.Boolean(),
    )

    def resolve_bill(self, info, **kwargs):
        filters = []
        filters += append_validity_filter(**kwargs)
        BillQueryMixin._check_permissions(info.context.user)
        return gql_optimizer.query(Bill.objects.filter(*filters).all(), info)

    @staticmethod
    def _check_permissions(user):
        if type(user) is AnonymousUser or not user.id or not user.has_perms(
                InvoiceConfig.gql_bill_search_perms):
            raise PermissionError("Unauthorized")
