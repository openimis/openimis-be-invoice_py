from core.signals import bind_service_signal
from core.service_signals import ServiceSignalBindType
from django.contrib.contenttypes.models import ContentType
from invoice.models import InvoiceLineItem, BillItem
from invoice.services import InvoiceService, InvoiceLineItemService, \
    BillService, BillLineItemService


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

    bind_service_signal(
        'convert_to_bill',
        check_bill_exist,
        bind_type=ServiceSignalBindType.BEFORE
    )
    bind_service_signal(
        'convert_to_bill',
        save_bill_in_db,
        bind_type=ServiceSignalBindType.AFTER
    )
    bind_service_signal(
        'trigger_bill_creation_from_calcrule',
        BillService.bill_creation_from_calculation,
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
        invoice_line_items = convert_results['invoice_data_line']
        invoice_service = InvoiceService(user=user)
        invoice_line_item_service = InvoiceLineItemService(user=user)
        result_invoice = invoice_service.create(convert_results['invoice_data'])
        if result_invoice["success"] is True:
            invoice_update = {
                "id": result_invoice["data"]["id"],
                "amount_net": 0,
                "amount_total": 0,
                "amount_discount": 0
            }
            for invoice_line_item in invoice_line_items:
                invoice_line_item["invoice_id"] = result_invoice["data"]["id"]
                result_invoice_line = invoice_line_item_service.create(invoice_line_item)
                if result_invoice_line["success"] is True:
                    invoice_update["amount_net"] += float(result_invoice_line["data"]["amount_net"])
                    invoice_update["amount_total"] += float(result_invoice_line["data"]["amount_total"])
                    invoice_update["amount_discount"] += 0 if result_invoice_line["data"]["discount"] else result_invoice_line["data"]["discount"]
            invoice_service.update(invoice_update)


def check_bill_exist(**kwargs):
    function_arguments = kwargs.get('data')[1]
    instance = function_arguments.get('instance', None)
    if instance.__class__.__name__ == "QuerySet":
        queryset_model = instance.model
        if queryset_model.__name__ == "Claim":
            claim = instance.first()
            content_type = ContentType.objects.get_for_model(claim.__class__)
            bills = BillItem.objects.filter(line_type=content_type, line_id=claim.id)
            if bills.count() == 0:
                return True


def save_bill_in_db(**kwargs):
    convert_results = kwargs.get('result', {})
    if 'bill_data' in convert_results and 'bill_data_line' in convert_results:
        user = convert_results['user']
        # save in database this invoice and invoice line item
        bill_line_items = convert_results['bill_data_line']
        bill_service = BillService(user=user)
        bill_line_item_service = BillLineItemService(user=user)
        result_bill = bill_service.create(convert_results['bill_data'])
        if result_bill["success"] is True:
            bill_update = {
                "id": result_bill["data"]["id"],
                "amount_net": 0,
                "amount_total": 0,
                "amount_discount": 0
            }
            for bill_line_item in bill_line_items:
                bill_line_item["bill_id"] = result_bill["data"]["id"]
                result_bill_line = bill_line_item_service.create(bill_line_item)
                if result_bill_line["success"] is True:
                    bill_update["amount_net"] += float(result_bill_line["data"]["amount_net"])
                    bill_update["amount_total"] += float(result_bill_line["data"]["amount_total"])
                    bill_update["amount_discount"] += 0 if result_bill_line["data"]["discount"] else result_bill_line["data"]["discount"]
            bill_service.update(bill_update)
