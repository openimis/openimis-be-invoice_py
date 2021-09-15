from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from policyholder.models import PolicyHolder

from contract.models import Contract
from core.forms import User
from django.test import TestCase

from invoice_payment.models import Invoice
from invoice_payment.services.invoice import InvoiceService
from contract.tests.helpers import create_test_contract
from policyholder.tests.helpers import create_test_policy_holder
from insuree.test_helpers import create_test_insuree
from datetime import date


class ServiceTestPolicyHolder(TestCase):
    BASE_TEST_INVOICE_PAYLOAD = {
            'subject_type': 'contract',
            'subject_id': None,
            'recipient_type': 'insuree',
            'recipient_id': None,
            'code': 'INVOICE_CODE',
            'code_rcp': 'INVOICE_CODE_RCP',
            'code_ext': 'INVOICE_CODE_EXT',
            'date_due': date(2021, 9, 13),
            'date_invoice': date(2021, 9, 11),
            'date_payed':  date(2021, 9, 12),
            'amount_discount': 20.1,
            'amount_net': 20.1,
            'tax_analysis': {'lines': [{'code': 'c', 'label': 'l', 'base': '0.1', 'amount': '2.01'}], 'total': '2.01'},
            'amount_total': 20.1,
            'status': 0,  # Draft
            'note': 'NOTE',
            'terms': 'TERMS',
            'payment_reference': 'payment reference'
        }

    BASE_TEST_UPDATE_INVOICE_PAYLOAD = {
        'id': None,
        'recipient_type': 'policyholder',
        'recipient_id': None,
        'code': 'INVOICE_CODE_2',
        'code_rcp': 'INVOICE_CODE_RCP_2',
        'code_ext': 'INVOICE_CODE_EXT_2',
        'date_due': date(2021, 10, 13),
        'date_invoice': date(2021, 10, 11),
        'date_payed': date(2021, 10, 12),
        'amount_discount': 22.1,
        'amount_net': 22.1,
        'tax_analysis': {'lines': [{'code': 'c', 'label': 'l', 'base': '0.1', 'amount': '2.21'}], 'total': '2.21'},
        'amount_total': 22.1,
        'status': 1,  # Draft
        'note': 'NOTE_2',
        'terms': 'TERMS_2',
        'payment_reference': 'payment reference 2'
    }

    BASE_EXPECTED_CREATE_RESPONSE = {
        "success": True,
        "message": "Ok",
        "detail": "",
        "data": {
            'subject_type': None,
            'subject_id':  None,
            'recipient_type': None,
            'recipient_id': None,
            'code': 'INVOICE_CODE',
            'code_rcp': 'INVOICE_CODE_RCP',
            'code_ext': 'INVOICE_CODE_EXT',
            'date_due': '2021-09-13',
            'date_invoice': '2021-09-11',
            'date_payed':  '2021-09-12',
            'amount_discount': 20.1,
            'amount_net': 20.1,
            'tax_analysis': {'lines': [{'code': 'c', 'label': 'l', 'base': '0.1', 'amount': '2.01'}], 'total': '2.01'},
            'amount_total': 20.1,
            'status': 0,  # Draft
            'note': 'NOTE',
            'terms': 'TERMS',
            'payment_reference': 'payment reference',
            'currency_code': 'USD'
        },
    }

    BASE_EXPECTED_UPDATE_RESPONSE = {
        "success": True,
        "message": "Ok",
        "detail": "",
        "data": {
            'recipient_type': None,
            'recipient_id': None,
            'code': 'INVOICE_CODE_2',
            'code_rcp': 'INVOICE_CODE_RCP_2',
            'code_ext': 'INVOICE_CODE_EXT_2',
            'date_due': '2021-10-13',
            'date_invoice': '2021-10-11',
            'date_payed':  '2021-10-12',
            'amount_discount': 22.1,
            'amount_net': 22.1,
            'tax_analysis': {'lines': [{'code': 'c', 'label': 'l', 'base': '0.1', 'amount': '2.21'}], 'total': '2.21'},
            'amount_total': 22.1,
            'status': 1,  # Draft
            'note': 'NOTE_2',
            'terms': 'TERMS_2',
            'payment_reference': 'payment reference 2'
        },
    }

    @classmethod
    def setUpClass(cls):
        if not User.objects.filter(username='admin_invoice').exists():
            User.objects.create_superuser(username='admin_invoice', password='S\/pe®Pąßw0rd™')
        Invoice.objects.filter(code=cls.BASE_TEST_INVOICE_PAYLOAD['code']).delete()

        cls.policy_holder = create_test_policy_holder()
        cls.contract = create_test_contract(cls.policy_holder)
        cls.user = User.objects.filter(username='admin').first()
        cls.insuree = create_test_insuree(with_family=False)
        cls.insuree_service = InvoiceService(cls.user)

        cls.BASE_TEST_INVOICE_PAYLOAD['subject_id'] = cls.contract.uuid
        cls.BASE_TEST_INVOICE_PAYLOAD['recipient_id'] = cls.insuree.uuid

        cls.BASE_EXPECTED_CREATE_RESPONSE['data']['subject_id'] = str(cls.contract.uuid)
        cls.BASE_EXPECTED_CREATE_RESPONSE['data']['recipient_id'] = str(cls.insuree.uuid)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        Contract.objects.filter(id=cls.contract.id).delete()
        PolicyHolder.objects.filter(id=cls.policy_holder.id).delete()
        cls.insuree.delete()
        super().tearDownClass()

    def test_policy_holder_create(self):
        with transaction.atomic():
            payload = self.BASE_TEST_INVOICE_PAYLOAD.copy()
            expected_response = self.BASE_EXPECTED_CREATE_RESPONSE.copy()
            response = self.insuree_service.create(payload)
            truncated_output = response
            truncated_output['data'] = {k: v for k, v in truncated_output['data'].items()
                                        if k in expected_response['data'].keys()}

            invoice = Invoice.objects.filter(code=payload['code']).first()
            expected_response['data']['subject_type'] = invoice.subject_type.id
            expected_response['data']['recipient_type'] = invoice.recipient_type.id

            self.assertDictEqual(expected_response, response)
            Invoice.objects.filter(code=payload['code']).delete()

    def test_policy_holder_update(self):
        with transaction.atomic():
            create_payload = self.BASE_TEST_INVOICE_PAYLOAD.copy()
            update_payload = self.BASE_TEST_UPDATE_INVOICE_PAYLOAD.copy()
            expected_response = self.BASE_EXPECTED_UPDATE_RESPONSE.copy()

            self.insuree_service.create(create_payload)
            update_payload['id'] = \
                Invoice.objects.filter(code=create_payload['code']).first().id

            response = self.insuree_service.update(update_payload)

            truncated_output = response
            truncated_output['data'] = {k: v for k, v in truncated_output['data'].items()
                                        if k in expected_response['data'].keys()}

            invoice = Invoice.objects.filter(code=update_payload['code']).first()

            expected_response['data']['recipient_type'] = invoice.recipient_type.id
            self.assertDictEqual(expected_response, response)

            Invoice.objects.filter(code=update_payload['code']).delete()
    def test_policy_holder_update(self):
        with transaction.atomic():
            create_payload = self.BASE_TEST_INVOICE_PAYLOAD.copy()
            update_payload = self.BASE_TEST_UPDATE_INVOICE_PAYLOAD.copy()
            expected_response = self.BASE_EXPECTED_UPDATE_RESPONSE.copy()

            self.insuree_service.create(create_payload)
            update_payload['id'] = \
                Invoice.objects.filter(code=create_payload['code']).first().id

            response = self.insuree_service.update(update_payload)

            truncated_output = response
            truncated_output['data'] = {k: v for k, v in truncated_output['data'].items()
                                        if k in expected_response['data'].keys()}

            invoice = Invoice.objects.filter(code=update_payload['code']).first()

            expected_response['data']['recipient_type'] = invoice.recipient_type.id
            self.assertDictEqual(expected_response, response)

            Invoice.objects.filter(code=update_payload['code']).delete()

    def test_policy_holder_delete(self):
        with transaction.atomic():
            payload = self.BASE_TEST_INVOICE_PAYLOAD.copy()
            expected_response = {
                "success": True,
                "message": "Ok",
                "detail": "",
            }

            response = self.insuree_service.create(payload)
            response = self.insuree_service.delete(response['data'])
            self.assertDictEqual(expected_response, response)
            Invoice.objects.filter(code=payload['code']).delete()
