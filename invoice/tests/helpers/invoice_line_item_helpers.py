from datetime import date

from django.contrib.contenttypes.models import ContentType
from policy.test_helpers import create_test_policy
from product.models import Product
from product.test_helpers import create_test_product

from contract.tests.helpers import create_test_contract
from policyholder.tests.helpers import create_test_policy_holder
from insuree.test_helpers import create_test_insuree
from core.forms import User

from invoice.models import Invoice, InvoiceLineItem
from invoice.tests.helpers import create_test_invoice

DEFAULT_TEST_INVOICE_LINE_ITEM_PAYLOAD = {
        'code': 'LineItem1',
        'description': 'description_str',
        'details': '{"test_int": 1, "test_txt": "some_str"}',
        'ledger_account': 'account',
        'quantity': 10,
        'unit_price': 10.5,
        'discount': 15.5,
        'tax_rate': None,
        'tax_analysis': {'lines': [{'code': 'c', 'label': 'l', 'base': '0.1', 'amount': '2.00'}], 'total': '2.0'},
        'amount_net': 10*10.5-15.5,
        'amount_total': (10*10.5-15.5) + 2.0
    }


def __get_or_create_user():
    user = User.objects.filter(username='admin_invoice').first()
    if not user:
        user = User.objects.create_superuser(username='admin_invoice', password='S\/pe®Pąßw0rd™')
    return user


def __get_or_create_product():
    product = Product.objects.filter(code='InvLine').first()
    if not product:
        product = create_test_product("InvLine", custom_props={"insurance_period": 12})
    return product


def __create_test_policy():
    insuree = create_test_insuree(with_family=True)
    product = __get_or_create_product()
    return create_test_policy(
        product=product,
        insuree=insuree
    )


def create_test_invoice_line_item(invoice=None, line_item=None, user=None, **custom_props):
    payload = DEFAULT_TEST_INVOICE_LINE_ITEM_PAYLOAD.copy()
    payload['invoice'] = invoice or create_test_invoice()
    payload['line'] = line_item or __create_test_policy()
    payload.update(**custom_props)

    InvoiceLineItem.objects.filter(code=payload['code']).delete()

    user = user or __get_or_create_user()
    invoice = InvoiceLineItem(**payload)
    invoice.save(username=user.username)

    return invoice
