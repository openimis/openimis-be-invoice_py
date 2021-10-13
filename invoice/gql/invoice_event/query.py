import graphene
from django.contrib.auth.models import AnonymousUser
from policy.apps import PolicyConfig

from core.schema import OrderedDjangoFilterConnectionField
from core.utils import append_validity_filter
from invoice.gql.gql_types import InvoiceEventGQLType
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
        InvoiceEventQueryMixin.__check_permissions(info.context.user)
        return gql_optimizer.query(InvoiceEvent.objects.filter(*filters).all(), info)

    @staticmethod
    def __check_permissions(user):
        # TODO: What permissions should we use?
        if type(user) is AnonymousUser:
            raise PermissionError("Unauthorized")


