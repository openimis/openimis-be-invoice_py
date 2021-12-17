import graphene

from core.schema import OpenIMISMutation


class CreatePaymentInputType(OpenIMISMutation.Input):
    status = graphene.Int(required=False)

    code_ext = graphene.String(required=False, max_length=32)
    code_tp = graphene.String(required=False, max_length=32)
    code_receipt = graphene.String(required=False, max_length=32)

    payment_origin = graphene.String(required=False, max_length=32)

    label = graphene.String(required=False, max_length=32)

    invoice_id = graphene.UUID(required=False)

    amount_payed = graphene.Decimal(max_digits=18, decimal_places=2, required=False)
    fees = graphene.Decimal(max_digits=18, decimal_places=2, required=False)
    amount_received = graphene.Decimal(max_digits=18, decimal_places=2, required=False)

    date_payment = graphene.Date(required=False)

    date_valid_from = graphene.Date(required=False)
    date_valid_to = graphene.Date(required=False)
    json_ext = graphene.types.json.JSONString(required=False)


class UpdatePaymentInputType(CreatePaymentInputType):
    id = graphene.UUID(required=True)


class CreateInvoiceEventType(OpenIMISMutation.Input):
    invoice_id = graphene.UUID(required=True)
    event_type = graphene.Int(required=True)
    message = graphene.String(required=True)


class UpdateInvoiceEventType(CreateInvoiceEventType):
    id = graphene.UUID(required=True)


class CreateBillPaymentInputType(OpenIMISMutation.Input):
    status = graphene.Int(required=False)

    code_ext = graphene.String(required=False, max_length=32)
    code_tp = graphene.String(required=False, max_length=32)
    code_receipt = graphene.String(required=False, max_length=32)

    payment_origin = graphene.String(required=False, max_length=32)

    label = graphene.String(required=False, max_length=32)

    bill_id = graphene.UUID(required=False)

    amount_payed = graphene.Decimal(max_digits=18, decimal_places=2, required=False)
    fees = graphene.Decimal(max_digits=18, decimal_places=2, required=False)
    amount_received = graphene.Decimal(max_digits=18, decimal_places=2, required=False)

    date_payment = graphene.Date(required=False)

    date_valid_from = graphene.Date(required=False)
    date_valid_to = graphene.Date(required=False)
    json_ext = graphene.types.json.JSONString(required=False)


class UpdateBillPaymentInputType(CreateBillPaymentInputType):
    id = graphene.UUID(required=True)


class CreateBillEventType(OpenIMISMutation.Input):
    bill_id = graphene.UUID(required=True)
    event_type = graphene.Int(required=True)
    message = graphene.String(required=True)


class UpdateBillEventType(CreateBillEventType):
    id = graphene.UUID(required=True)
