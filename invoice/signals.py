from core.signals import bind_service_signal
from core.service_signals import ServiceSignalBindType
from django.contrib.contenttypes.models import ContentType
from invoice.models import InvoiceLineItem
from invoice.services import InvoiceService, InvoiceLineItemService


def bind_service_signals():
    bind_service_signal(
        'convert_to_invoice',
        check_invoice_exist,
        bind_type=ServiceSignalBindType.BEFORE
    )
    bind_service_signal(
        'convert_to_invoice',
        save_invoice_in_db,
        bind_type=ServiceSignalBindType.AFTER
    )


def check_invoice_exist(**kwargs):
    function_arguments = kwargs.get('data')[1]
    instance = function_arguments.get('instance', None)
    content_type_policy = ContentType.objects.get_for_model(instance.__class__)
    invoices = InvoiceLineItem.objects.filter(line_type=content_type_policy, line_id=instance.id)
    if invoices.count() == 0:
        return True


def save_invoice_in_db(**kwargs):
    convert_results = kwargs.get('result', {})
    if 'invoice_data' in convert_results and 'invoice_data_line' in convert_results:
        user = convert_results['user']
        # save in database this invoice and invoice line item
        invoice_line_item = convert_results['invoice_data_line']
        invoice_service = InvoiceService(user=user)
        invoice_line_item_service = InvoiceLineItemService(user=user)
        result_invoice = invoice_service.create(convert_results['invoice_data'])
        if result_invoice["success"] is True:
            # build invoice item
            invoice_line_item["invoice_id"] = result_invoice["data"]["id"]
            result_invoice_line = invoice_line_item_service.create(invoice_line_item)
            if result_invoice_line["success"] is True:
                # build invoice amounts based on invoice_line_item data
                invoice_update = {
                    "id": result_invoice["data"]["id"],
                    "amount_net": result_invoice_line["data"]["amount_net"],
                    "amount_total": result_invoice_line["data"]["amount_total"],
                    "amount_discount": 0 if result_invoice_line["data"]["discount"] else result_invoice_line["data"]["discount"]
                }
                invoice_service.update(invoice_update)
