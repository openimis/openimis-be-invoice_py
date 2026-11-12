"""Row security of the invoice sub-resources and of the subject JSON (OP-3322).

The parents' own scope (a GenericScope on the subject) needs a full location
setup to exercise; what these tests pin down is that each child narrows to the
rows of its parent the user may see, whatever that parent's rule is. So the
parent's ``get_queryset`` is patched to a known set of rows.
"""
import json
from types import SimpleNamespace
from unittest import mock

from django.test import TestCase

from core.test_helpers import LogInHelper
from invoice.gql.gql_types.bill_types import BillEventGQLType, BillPaymentGQLType
from invoice.gql.gql_types.invoice_types import (
    InvoiceEventGQLType,
    InvoiceGQLType,
    InvoicePaymentGQLType,
)
from invoice.gql.gql_types.payment_types import PaymentInvoiceGQLType
from invoice.models import (
    BillEvent,
    BillPayment,
    DetailPaymentInvoice,
    InvoiceEvent,
    InvoicePayment,
    PaymentInvoice,
)
from invoice.tests.helpers import (
    create_test_bill,
    create_test_bill_payment,
    create_test_invoice,
    create_test_invoice_payment,
    create_test_payment_invoice_with_details,
    create_test_payment_invoice_without_details,
)
from invoice.utils import SUBJECT_SUMMARY_FIELDS, subject_summary, underscore_to_camel


def _only(model, *rows):
    """A stand-in for ``model.get_queryset`` that lets ``rows`` through."""
    ids = [row.id for row in rows]
    return lambda queryset, user=None: model.objects.filter(id__in=ids)


class SubResourceRowScopeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = LogInHelper().get_or_create_user_api(username="admin_invoice")
        cls.info = SimpleNamespace(context=SimpleNamespace(user=cls.user))

        cls.invoice_in = create_test_invoice(user=cls.user, code="OP3322-IN")
        cls.invoice_out = create_test_invoice(user=cls.user, code="OP3322-OUT")
        cls.invoice_payment_in = create_test_invoice_payment(invoice=cls.invoice_in, user=cls.user)
        cls.invoice_payment_out = create_test_invoice_payment(invoice=cls.invoice_out, user=cls.user)
        cls.invoice_event_in = cls._event(InvoiceEvent, invoice=cls.invoice_in)
        cls.invoice_event_out = cls._event(InvoiceEvent, invoice=cls.invoice_out)

        cls.bill_in = create_test_bill(user=cls.user, code="OP3322-BIN")
        cls.bill_out = create_test_bill(user=cls.user, code="OP3322-BOUT")
        cls.bill_payment_in = create_test_bill_payment(bill=cls.bill_in, user=cls.user)
        cls.bill_payment_out = create_test_bill_payment(bill=cls.bill_out, user=cls.user)
        cls.bill_event_in = cls._event(BillEvent, bill=cls.bill_in)
        cls.bill_event_out = cls._event(BillEvent, bill=cls.bill_out)

    @classmethod
    def _event(cls, model, **parent):
        event = model(message="OP-3322", **parent)
        event.save(username=cls.user.username)
        return event

    def _assert_scoped(self, gql_type, model, parent_field, inside, outside):
        parent = model._meta.get_field(parent_field).related_model
        visible_parent = getattr(inside, parent_field)
        with mock.patch.object(parent, "get_queryset", _only(parent, visible_parent)):
            for queryset in (
                model.get_queryset(model.objects.all(), self.user),
                gql_type.get_queryset(model.objects.all(), self.info),
            ):
                ids = set(queryset.values_list("id", flat=True))
                self.assertIn(inside.id, ids)
                self.assertNotIn(outside.id, ids)

    def test_invoice_payment_follows_its_invoice(self):
        self._assert_scoped(InvoicePaymentGQLType, InvoicePayment, "invoice",
                            self.invoice_payment_in, self.invoice_payment_out)

    def test_invoice_event_follows_its_invoice(self):
        self._assert_scoped(InvoiceEventGQLType, InvoiceEvent, "invoice",
                            self.invoice_event_in, self.invoice_event_out)

    def test_bill_payment_follows_its_bill(self):
        self._assert_scoped(BillPaymentGQLType, BillPayment, "bill",
                            self.bill_payment_in, self.bill_payment_out)

    def test_bill_event_follows_its_bill(self):
        self._assert_scoped(BillEventGQLType, BillEvent, "bill",
                            self.bill_event_in, self.bill_event_out)


class PaymentInvoiceRowScopeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = LogInHelper().get_or_create_user_api(username="admin_invoice")
        cls.info = SimpleNamespace(context=SimpleNamespace(user=cls.user))
        cls.paying_visible = create_test_payment_invoice_with_details(
            invoice=create_test_invoice(user=cls.user, code="OP3322-PV"), user=cls.user)
        cls.paying_hidden = create_test_payment_invoice_with_details(
            invoice=create_test_invoice(user=cls.user, code="OP3322-PH"), user=cls.user)
        cls.no_detail, _invoice, _item = create_test_payment_invoice_without_details(
            invoice=create_test_invoice(user=cls.user, code="OP3322-PN"), user=cls.user)

    def test_payment_follows_its_details(self):
        visible_details = DetailPaymentInvoice.objects.filter(payment=self.paying_visible)
        with mock.patch.object(
            DetailPaymentInvoice, "get_queryset", _only(DetailPaymentInvoice, *visible_details)
        ):
            for queryset in (
                PaymentInvoice.get_queryset(PaymentInvoice.objects.all(), self.user),
                PaymentInvoiceGQLType.get_queryset(PaymentInvoice.objects.all(), self.info),
            ):
                ids = set(queryset.values_list("id", flat=True))
                self.assertIn(self.paying_visible.id, ids)
                self.assertNotIn(self.paying_hidden.id, ids)
                # Nothing to narrow a payment without details by: it stays visible.
                self.assertIn(self.no_detail.id, ids)


class SubjectSummaryTest(TestCase):
    """`subject` / `thirdparty` expose identifying fields, not the whole row."""

    @classmethod
    def setUpTestData(cls):
        cls.user = LogInHelper().get_or_create_user_api(username="admin_invoice")
        cls.invoice = create_test_invoice(user=cls.user, code="OP3322-SUM")

    def test_thirdparty_is_whitelisted(self):
        insuree = self.invoice.thirdparty
        allowed = {underscore_to_camel(field) for field in SUBJECT_SUMMARY_FIELDS}

        payload = json.loads(InvoiceGQLType.resolve_thirdparty(self.invoice, None))

        self.assertLessEqual(set(payload), allowed)
        self.assertEqual(payload["chfId"], insuree.chf_id)
        self.assertEqual(payload["lastName"], insuree.last_name)
        for withheld in ("phone", "email", "auditUserId", "passport", "jsonExt"):
            self.assertNotIn(withheld, payload)

    def test_summary_leaves_the_instance_untouched(self):
        insuree = self.invoice.thirdparty
        subject_summary(insuree)
        self.assertIn("_state", vars(insuree))
