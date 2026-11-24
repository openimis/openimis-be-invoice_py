"""get_queryset honours the OP-2029 validity contract (epic OP-3317, phase 1).

Explicit validity values return the expected rows; a caller asking for
nothing gets what it got before the contract existed.
"""

from django.test import TestCase

from core.test_helpers import assert_row_filters, create_test_interactive_user, mark_deleted
from invoice.models import Invoice
from invoice.tests.helpers import create_test_invoice


class InvoiceRowFiltersTest(TestCase):
    def test_invoice(self):
        user = create_test_interactive_user(username="invrowfilters")
        live = create_test_invoice(user=user, code="RWF1")
        deleted = mark_deleted(create_test_invoice(user=user, code="RWF2"))
        assert_row_filters(
            self, Invoice, Invoice.objects.filter(id__in=[live.id, deleted.id]), user,
            live.id, deleted.id, default_hides_deleted=False,
        )
