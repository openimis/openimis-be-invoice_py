"""
OP-3343: the GenericForeignKey outputs of the invoice and bill lists (subject,
thirdparty, line and their type names) are loaded for the whole page at once,
not with one query per row, and the JSON they return is unchanged.
"""
import json
from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection
from django.test.utils import CaptureQueriesContext

from claim_batch.models import BatchRun
from contract.tests.helpers import create_test_contract
from insuree.test_helpers import create_test_insuree
from location.models import Location
from policy.test_helpers import create_test_policy
from policyholder.tests.helpers import create_test_policy_holder
from product.test_helpers import create_test_product

from invoice.models import Bill, BillItem, Invoice, InvoiceLineItem
from invoice.tests.gql.base import InvoiceGQLTestCase
from invoice.tests.helpers import create_test_bill, create_test_bill_line_item, \
    create_test_invoice, create_test_invoice_line_item
from invoice.utils import underscore_to_camel

PREFIX = "GFK3343-"
ROWS = 6


def _legacy_json(obj, **extra):
    # What the resolvers returned before OP-3343: the instance's fields, camelCased.
    data = {underscore_to_camel(k): v for k, v in obj.__dict__.items() if k != '_state'}
    data.update(extra)
    return json.loads(json.dumps(data, cls=DjangoJSONEncoder))


def _load(value):
    # The resolvers return a JSON string, which graphene's JSONString encodes again.
    value = json.loads(value)
    return json.loads(value) if isinstance(value, str) else value


def _fresh(content_type, object_id):
    return content_type.get_object_for_this_type(pk=object_id)


class GenericForeignKeyOutputTest(InvoiceGQLTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        heads = [create_test_insuree(with_family=True) for _ in range(3)]
        families = [head.family for head in heads]
        contract = create_test_contract(create_test_policy_holder())
        location = Location.objects.filter(validity_to__isnull=True).first()
        batch_run = BatchRun.objects.create(
            location=location, run_date=datetime(2021, 1, 31), audit_user_id=-1, run_year=2021, run_month=1)
        thirdparty = create_test_insuree(with_family=False)
        product = create_test_product("GFK3343", custom_props={"insurance_period": 12})
        policy = create_test_policy(product=product, insuree=heads[2])

        # Two rows share each family, so a prefetched target is reused across rows.
        invoice_subjects = [families[0], families[0], contract, families[1], families[1], families[2]]
        bill_subjects = [families[0], families[0], batch_run, batch_run, contract, families[1]]
        for i in range(ROWS):
            invoice = create_test_invoice(
                invoice_subjects[i], thirdparty, cls.user, code=f"{PREFIX}{i}", code_ext=f"{PREFIX}{i}")
            create_test_invoice_line_item(invoice, policy, cls.user, code=f"{PREFIX}L{i}")
            bill = create_test_bill(
                bill_subjects[i], thirdparty, cls.user, code=f"{PREFIX}{i}", code_ext=f"{PREFIX}{i}")
            create_test_bill_line_item(bill, policy, cls.user, code=f"{PREFIX}L{i}")

    def _execute(self, query):
        output = self.graph_client.execute(query, context=self.user_context.get_request())
        self.assertIsNone(output.get('errors'), output.get('errors'))
        return output['data']

    def _count_queries(self, query):
        self._execute(query)  # warm the caches (rights, content types) first
        with CaptureQueriesContext(connection) as ctx:
            data = self._execute(query)
        return len(ctx), data

    def _assert_constant(self, template):
        few, data = self._count_queries(template % 2)
        self.assertEqual(len(next(iter(data.values()))['edges']), 2)
        many, data = self._count_queries(template % ROWS)
        self.assertEqual(len(next(iter(data.values()))['edges']), ROWS)
        self.assertEqual(few, many, f"{few} queries for 2 rows, {many} for {ROWS}")

    INVOICE = '{ invoice(first: %%d, code_Istartswith: "%s", orderBy: ["code"]) { edges { node {' \
              ' code subject subjectTypeName thirdparty thirdpartyTypeName } } } }' % PREFIX
    BILL = '{ bill(first: %%d, code_Istartswith: "%s", orderBy: ["code"]) { edges { node {' \
           ' code subject subjectTypeName thirdparty thirdpartyTypeName } } } }' % PREFIX
    INVOICE_LINE = '{ invoiceLineItem(first: %%d, code_Istartswith: "%sL", orderBy: ["code"]) { edges { node {' \
                   ' code line lineTypeName } } } }' % PREFIX
    BILL_LINE = '{ billItem(first: %%d, code_Istartswith: "%sL", orderBy: ["code"]) { edges { node {' \
                ' code line lineTypeName } } } }' % PREFIX

    def test_invoice_query_count_does_not_depend_on_rows(self):
        self._assert_constant(self.INVOICE)

    def test_bill_query_count_does_not_depend_on_rows(self):
        self._assert_constant(self.BILL)

    def test_invoice_line_query_count_does_not_depend_on_rows(self):
        self._assert_constant(self.INVOICE_LINE)

    def test_bill_line_query_count_does_not_depend_on_rows(self):
        self._assert_constant(self.BILL_LINE)

    def test_invoice_output_is_unchanged(self):
        edges = self._execute(self.INVOICE % ROWS)['invoice']['edges']
        for edge in edges:
            node = edge['node']
            invoice = Invoice.objects.get(code=node['code'])
            subject = _fresh(invoice.subject_type, invoice.subject_id)
            extra = {}
            if invoice.subject_type.name == "family":
                head = subject.head_insuree
                extra['headInsuree'] = {
                    'id': head.id, 'chfId': head.chf_id, 'uuid': head.uuid,
                    'lastName': head.last_name, 'otherNames': head.other_names,
                } if head.validity_to is None else {}
            with self.subTest(code=node['code']):
                self.assertEqual(_load(node['subject']), _legacy_json(subject, **extra))
                self.assertEqual(node['subjectTypeName'], invoice.subject_type.name)
                self.assertEqual(
                    _load(node['thirdparty']),
                    _legacy_json(_fresh(invoice.thirdparty_type, invoice.thirdparty_id)))

    def test_bill_output_is_unchanged(self):
        edges = self._execute(self.BILL % ROWS)['bill']['edges']
        for edge in edges:
            node = edge['node']
            bill = Bill.objects.get(code=node['code'])
            subject = _fresh(bill.subject_type, bill.subject_id)
            extra = {}
            if bill.subject_type.name == "batch run" and subject.location_id:
                extra['location'] = {'code': subject.location.code, 'name': subject.location.name}
            with self.subTest(code=node['code']):
                self.assertEqual(_load(node['subject']), _legacy_json(subject, **extra))
                self.assertEqual(
                    _load(node['thirdparty']),
                    _legacy_json(_fresh(bill.thirdparty_type, bill.thirdparty_id)))

    def test_line_output_is_unchanged(self):
        for query, model in ((self.INVOICE_LINE, InvoiceLineItem), (self.BILL_LINE, BillItem)):
            data = self._execute(query % ROWS)
            for edge in next(iter(data.values()))['edges']:
                node = edge['node']
                item = model.objects.get(code=node['code'])
                with self.subTest(model=model.__name__, code=node['code']):
                    self.assertEqual(_load(node['line']), _legacy_json(_fresh(item.line_type, item.line_id)))
                    self.assertEqual(node['lineTypeName'], item.line_type.name)

    def test_rows_sharing_a_subject_both_return_it(self):
        edges = self._execute(self.INVOICE % ROWS)['invoice']['edges']
        shared = [_load(e['node']['subject']) for e in edges[:2]]
        family_type = ContentType.objects.get(app_label='insuree', model='family')
        self.assertTrue(Invoice.objects.filter(code=f"{PREFIX}0", subject_type=family_type).exists())
        self.assertEqual(shared[0], shared[1])
        self.assertIn('headInsuree', shared[1])
