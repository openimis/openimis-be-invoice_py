"""
OP-3342: every GenericForeignKey pair of the invoice models has a composite
(type, id) index, so that looking rows up by their target (the bills of a batch
run, the line items of a policy) does not scan the table.
"""
from django.db import connection
from django.test import TestCase

from invoice.models import Bill, BillItem, DetailPaymentInvoice, Invoice, InvoiceLineItem

GFK_PAIRS = [
    (Invoice, "subject_type", "subject_id"),
    (Invoice, "thirdparty_type", "thirdparty_id"),
    (Bill, "subject_type", "subject_id"),
    (Bill, "thirdparty_type", "thirdparty_id"),
    (InvoiceLineItem, "line_type", "line_id"),
    (BillItem, "line_type", "line_id"),
    (DetailPaymentInvoice, "subject_type", "subject_id"),
]


class GenericForeignKeyIndexTest(TestCase):
    def test_every_gfk_pair_has_a_type_id_index(self):
        for model, type_field, id_field in GFK_PAIRS:
            table = model._meta.db_table
            columns = [model._meta.get_field(f).column for f in (type_field, id_field)]
            with self.subTest(table=table, columns=columns):
                with connection.cursor() as cursor:
                    constraints = connection.introspection.get_constraints(cursor, table)
                self.assertTrue(
                    any(c["index"] and c["columns"][:2] == columns for c in constraints.values()),
                    f"no ({', '.join(columns)}) index on {table}",
                )
