import graphene
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from policy.apps import PolicyConfig

from core.schema import OrderedDjangoFilterConnectionField
from core.utils import append_validity_filter
from invoice.gql.gql_types import InvoicePaymentGQLType
from invoice.models import InvoicePayment
import graphene_django_optimizer as gql_optimizer


class InvoicePaymentQueryMixin:
    invoice_payment = OrderedDjangoFilterConnectionField(
        InvoicePaymentGQLType,
        orderBy=graphene.List(of_type=graphene.String),
        dateValidFrom__Gte=graphene.DateTime(),
        dateValidTo__Lte=graphene.DateTime(),
        applyDefaultValidityFilter=graphene.Boolean(),
    )

    def resolve_invoice_payment(self, info, **kwargs):
        filters = []
        filters += append_validity_filter(**kwargs)
        InvoicePaymentQueryMixin.__check_permissions(info.context.user)
        return gql_optimizer.query(InvoicePayment.objects.filter(*filters).all(), info)

    @staticmethod
    def __check_permissions(user):
        # TODO: What permissions should we use?
        if type(user) is AnonymousUser or not user.id or not user.has_perms(
                PolicyConfig.gql_mutation_create_policies_perms):
            raise PermissionError("Unauthorized")


