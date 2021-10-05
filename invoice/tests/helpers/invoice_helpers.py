from datetime import date

from django.contrib.contenttypes.models import ContentType

from contract.tests.helpers import create_test_contract
from policyholder.tests.helpers import create_test_policy_holder
from insuree.test_helpers import create_test_insuree
from core.forms import User

from invoice.models import Invoice

DEFAULT_TEST_INVOICE_PAYLOAD = {
    'subject_type': 'contract',
    'subject_id': None,
    'recipient_type': 'insuree',
    'recipient_id': None,
    'code': 'INVOICE_CODE',
    'code_rcp': 'INVOICE_CODE_RCP',
    'code_ext': 'INVOICE_CODE_EXT',
    'date_due': date(2021, 9, 13),
    'date_invoice': date(2021, 9, 11),
    'date_payed': date(2021, 9, 12),
    'amount_discount': 20.1,
    'amount_net': 20.1,
    'tax_analysis': {'lines': [{'code': 'c', 'label': 'l', 'base': '0.1', 'amount': '2.01'}], 'total': '2.01'},
    'amount_total': 20.1,
    'status': Invoice.InvoiceStatus.VALIDATED,  # Validated
    'note': 'NOTE',
    'terms': 'TERMS',
    'payment_reference': 'payment reference'
}


def __get_or_create_user():
    user = User.objects.filter(username='admin_invoice').first()
    if not user:
        user = User.objects.create_superuser(username='admin_invoice', password='S\/pe®Pąßw0rd™')
    return user


def create_test_invoice(subject=None, recipient=None, user=None, **custom_props):
    subject = subject or __create_test_subject()
    recipient = recipient or __create_test_recipient()
    payload = DEFAULT_TEST_INVOICE_PAYLOAD.copy()
    payload['subject'] = subject
    payload['subject_type'] = ContentType.objects.get_for_model(subject)
    payload['recipient'] = recipient
    payload['recipient_type'] = ContentType.objects.get_for_model(recipient)
    payload.update(**custom_props)
    user = user or __get_or_create_user()

    if Invoice.objects.filter(code=payload['code']).exists():
        i = Invoice.objects.filter(code=payload['code']).first()
        i.payments.all().delete()
        i.line_items.all().delete()
        Invoice.objects.filter(code=payload['code']).delete()

    invoice = Invoice(**payload)
    invoice.save(username=user.username)

    return invoice


def __create_test_subject():
    policy_holder = create_test_policy_holder()
    return create_test_contract(policy_holder)


def __create_test_recipient():
    return create_test_insuree(with_family=False)
