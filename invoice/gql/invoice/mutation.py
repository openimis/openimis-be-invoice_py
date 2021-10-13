import logging

import graphene
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from graphql import GraphQLError
from policy.apps import PolicyConfig

from core.gql.gql_mutations.base_mutation import BaseMutation
from core.schema import OpenIMISMutation
from invoice.models import Invoice
from invoice.services import InvoiceService

logger = logging.getLogger(__name__)


class GenerateTimeframeInvoices(BaseMutation):
    _model = Invoice
    _invoice_service_class: InvoiceService = InvoiceService
    _mutation_module = 'invoice'
    _mutation_class = 'GenerateTimeframeInvoices'

    @classmethod
    def _validate_mutation(cls, user, **data):
        # TODO: What permissions should be used?
        if type(user) is AnonymousUser or not user.id or not user.has_perms(
                PolicyConfig.gql_mutation_create_policies_perms):
            raise ValidationError("mutation.authentication_required")

    @classmethod
    def _mutate(cls, user, **data):
        if "client_mutation_id" in data:
            data.pop('client_mutation_id')
        if "client_mutation_label" in data:
            data.pop('client_mutation_label')

        from_date, to_date = data.get("date_from", None), data.get("date_to", None)

        if not from_date or not to_date:
            raise GraphQLError('To generate invoices for a time period, '
                               'it is necessary to specify from_date and to_date')

        output = cls._generate_timeframe_invoices(user, from_date, to_date)

        return [] if output is None else f"Error during invoice generation: {output}"

    @classmethod
    def _generate_timeframe_invoices(cls, user, from_date, to_date):
        try:
            # invoice_creation_from_calculation doesn't have implementation,
            # it sends a signal, if a binded function throws an exception it's message is returned.
            service = cls._invoice_service_class(user)
            service.invoice_creation_from_calculation(user=user, from_date=from_date, to_date=to_date)
        except Exception as e:
            logger.exception(F"Exception occurred during invoice generation. Details: {e}")
            return str(e)
        return None

    class Input(OpenIMISMutation.Input):
        date_from = graphene.Date(required=False)
        date_to = graphene.Date(required=False)

