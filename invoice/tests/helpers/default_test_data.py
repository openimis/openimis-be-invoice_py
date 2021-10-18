from datetime import date

from invoice.models import Invoice, InvoicePayment

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
    'status': Invoice.Status.VALIDATED,  # Validated
    'note': 'NOTE',
    'terms': 'TERMS',
    'payment_reference': 'payment reference'
}


DEFAULT_TEST_INVOICE_PAYMENT_PAYLOAD = {
    'label': 'label_pay',
    'code_rcp': 'pay_sys_ref',
    'code_receipt': 'receipt number',
    'invoice': None,
    'amount_payed': 91.5,
    'fees': 12.0,
    'amount_received': 22.0,
    'date_payment': date(2021, 10, 10),
    'status': InvoicePayment.PaymentStatus.ACCEPTED
}