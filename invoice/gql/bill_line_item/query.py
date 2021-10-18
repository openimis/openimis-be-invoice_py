import graphene
from django.contrib.auth.models import AnonymousUser

from core.schema import OrderedDjangoFilterConnectionField
from core.utils import append_validity_filter
from invoice.apps import InvoiceConfig
from invoice.gql.gql_types.bill_types import BillItemGQLType
from invoice.models import BillItem
import graphene_django_optimizer as gql_optimizer


class BillItemQueryMixin:
    bill_event = OrderedDjangoFilterConnectionField(
        BillItemGQLType,
        orderBy=graphene.List(of_type=graphene.String),
        dateValidFrom__Gte=graphene.DateTime(),
        dateValidTo__Lte=graphene.DateTime(),
        applyDefaultValidityFilter=graphene.Boolean(),
    )

    def resolve_bill_line_item(self, info, **kwargs):
        filters = []
        filters += append_validity_filter(**kwargs)
        BillItemQueryMixin._check_permissions(info.context.user)
        return gql_optimizer.query(BillItem.objects.filter(*filters).all(), info)

    @staticmethod
    def _check_permissions(user):
        if type(user) is AnonymousUser or not user.id or not user.has_perms(
                InvoiceConfig.gql_bill_search_perms):
            raise PermissionError("Unauthorized")
