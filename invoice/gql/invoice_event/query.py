import graphene
from django.contrib.auth.models import AnonymousUser
from policy.apps import PolicyConfig

from core.schema import OrderedDjangoFilterConnectionField
from core.utils import append_validity_filter
from invoice.apps import InvoiceConfig
from invoice.gql.gql_types.invoice_types import InvoiceEventGQLType
from invoice.models import InvoiceEvent
import graphene_django_optimizer as gql_optimizer


class InvoiceEventQueryMixin:
    invoice_event = OrderedDjangoFilterConnectionField(
        InvoiceEventGQLType,
        orderBy=graphene.List(of_type=graphene.String),
        dateValidFrom__Gte=graphene.DateTime(),
        dateValidTo__Lte=graphene.DateTime(),
        applyDefaultValidityFilter=graphene.Boolean(),
    )

    def resolve_invoice_event(self, info, **kwargs):
        filters = []
        filters += append_validity_filter(**kwargs)
        InvoiceEventQueryMixin._check_permissions(info.context.user)
        return gql_optimizer.query(InvoiceEvent.objects.filter(*filters).all(), info)

    @staticmethod
    def _check_permissions(user):
        if type(user) is AnonymousUser or not user.id or not user.has_perms(
                InvoiceConfig.gql_invoice_event_search_perms):
            raise PermissionError("Unauthorized")


