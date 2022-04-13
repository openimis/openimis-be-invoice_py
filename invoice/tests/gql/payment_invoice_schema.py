import uuid

from core.models import MutationLog
from invoice.models import PaymentInvoice, PaymentInvoiceMutation
from invoice.tests.gql.base import InvoiceGQLTestCase
from invoice.tests.helpers import DEFAULT_TEST_PAYMENT_INVOICE_PAYLOAD


class PaymentInvoiceGQLTest(InvoiceGQLTestCase):

    search_for_payment_invoice_query = F'''
query {{ 
	paymentInvoice(codeTp_Iexact:"{DEFAULT_TEST_PAYMENT_INVOICE_PAYLOAD['code_tp']}", 
	amountReceived: {DEFAULT_TEST_PAYMENT_INVOICE_PAYLOAD['amount_received']}){{
    edges {{
      node {{
        isDeleted,
        codeTp,
        codeExt,
        amountReceived,
        datePayment,
        reconciliationStatus,
        fees,
        payerRef
      }}
    }}
  }}
}}
'''

    create_mutation_str = '''  
mutation {{
  createPaymentInvoice(input:{{reconciliationStatus: 1, codeExt:"{payment_code}", codeTp:"PAY_CODE", codeReceipt:"gqlRec", 
  label:"gql label", fees: "12.00", amountReceived: "91.50", payerRef: "payerRef", 
  datePayment:"2022-04-12", clientMutationId: "{mutation_id}"}}) {{
    internalId
    clientMutationId
  }}
}}
'''

    delete_mutation_str = '''  
mutation {{
  deletePaymentInvoice(input:{{uuids:["{payment_uuid}"], clientMutationId: "{mutation_id}"}}) {{
    internalId
    clientMutationId
  }}
}}
'''

    update_mutation_str = '''  
mutation {{
	updatePaymentInvoice(input:{{id:"{payment_uuid}", codeExt:"updExt", payerRef: "payerRef", clientMutationId: "{mutation_id}"}}){{
    internalId
    clientMutationId
  }}
}}
'''

    def test_fetch_payment_invoice_query(self):
        payment_code = "GQLCOD"
        mutation_client_id = str(uuid.uuid4())
        mutation = self.create_mutation_str.format(
            payment_code=payment_code, mutation_id=mutation_client_id
        )
        self.graph_client.execute(mutation, context=self.BaseTestContext(self.user))
        output = self.graph_client.execute(self.search_for_payment_invoice_query,
                                           context=self.BaseTestContext(self.user))
        expected = \
            {'data': {
                'paymentInvoice': {
                    'edges': [
                        {'node': {
                            'isDeleted': False,
                            'codeExt': 'GQLCOD',
                            'codeTp': 'PAY_CODE',
                            'amountReceived': "91.50",
                            'datePayment': '2022-04-12',
                            'reconciliationStatus': 'A_1',
                            'fees': "12.00",
                            'payerRef': 'payerRef',
        }}]}}}
        self.assertEqual(output, expected)

    def test_create_payment_mutation(self):
        payment_code = "GQLCOD"
        mutation_client_id = str(uuid.uuid4())
        mutation = self.create_mutation_str.format(
            payment_code=payment_code, mutation_id=mutation_client_id
        )
        self.graph_client.execute(mutation, context=self.BaseTestContext(self.user))
        expected = PaymentInvoice.objects.get(code_ext=payment_code)
        mutation_log = MutationLog.objects.filter(client_mutation_id=mutation_client_id).first()
        obj = PaymentInvoiceMutation.objects.get(mutation_id=mutation_log.id).payment_invoice
        self.assertEqual(obj, expected)

    def test_delete_payment_mutation(self):
        payment_code = "GQLCOD"
        mutation_client_id = str(uuid.uuid4())
        mutation = self.create_mutation_str.format(
            payment_code=payment_code, mutation_id=mutation_client_id
        )
        self.graph_client.execute(mutation, context=self.BaseTestContext(self.user))
        expected = PaymentInvoice.objects.get(code_ext=payment_code)
        mutation_client_id = str(uuid.uuid4())
        mutation = self.delete_mutation_str.format(payment_uuid=expected.id, mutation_id=mutation_client_id)
        self.graph_client.execute(mutation, context=self.BaseTestContext(self.user))
        # TODO: Currently deleted entries are not filtered by manager, only in GQL Query. Should we change this?
        payment = PaymentInvoice.objects.filter(code_ext=payment_code).all()
        mutation_ = PaymentInvoiceMutation.objects.filter(payment_invoice=payment[0]).all()
        self.assertEqual(len(payment), 1)
        self.assertTrue(payment[0].is_deleted)
        self.assertTrue(len(mutation_) == 2)

    def test_update_payment_mutation(self):
        payment_code = "GQLCOD"
        mutation_client_id = str(uuid.uuid4())
        mutation = self.create_mutation_str.format(
            payment_code=payment_code, mutation_id=mutation_client_id
        )
        self.graph_client.execute(mutation, context=self.BaseTestContext(self.user))

        created = PaymentInvoice.objects.get(code_ext=payment_code)
        mutation_client_id = str(uuid.uuid4())
        mutation = self.update_mutation_str.format(payment_uuid=created.id, mutation_id=mutation_client_id)
        self.graph_client.execute(mutation, context=self.BaseTestContext(self.user))

        expected_code_ext = "updExt"
        mutation_log = MutationLog.objects.filter(client_mutation_id=mutation_client_id).first()
        obj: PaymentInvoice = PaymentInvoiceMutation.objects.get(mutation_id=mutation_log.id).payment_invoice
        self.assertEqual(obj.code_ext, expected_code_ext)
