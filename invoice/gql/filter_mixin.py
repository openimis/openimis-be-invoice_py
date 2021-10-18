
class GenericFilterGQLTypeMixin:

    @classmethod
    def get_base_filters_invoice(cls):
        return {
            "id": ["exact"],
            "subject_id": ["exact"],
            "subject_type": ["exact"],

            "code": ["exact", "istartswith", "icontains", "iexact"],
            "code_ext": ["exact", "istartswith", "icontains", "iexact"],
            "date_due": ["exact", "lt", "lte", "gt", "gte"],
            "date_payed": ["exact", "lt", "lte", "gt", "gte"],

            "amount_discount": ["exact", "lt", "lte", "gt", "gte"],
            "amount_net": ["exact", "lt", "lte", "gt", "gte"],
            "amount_total": ["exact", "lt", "lte", "gt", "gte"],

            "status": ["exact"],

            "currency_code": ["exact"],
            "note": ["exact", "icontains"],
            "terms": ["exact", "icontains"],

            "payment_reference": ["exact", "istartswith", "icontains", "iexact"],

            "date_created": ["exact", "lt", "lte", "gt", "gte"],
            "date_updated": ["exact", "lt", "lte", "gt", "gte"],
            "is_deleted": ["exact"],
            "version": ["exact"],
        }

    @classmethod
    def get_base_filters_invoice_line_item(cls):
        return {
            "id": ["exact"],
            "line_type": ["exact"],
            "line_id": ["exact"],

            "description": ["istartswith", "icontains", "iexact"],

            "ledger_account": ["istartswith", "iexact"],

            "quantity": ["exact", "lt", "lte", "gt", "gte"],
            "unit_price": ["exact", "lt", "lte", "gt", "gte"],

            "discount": ["exact", "lt", "lte", "gt", "gte"],

            "tax_rate": ["exact"],
            "amount_total": ["exact", "lt", "lte", "gt", "gte"],
            "amount_net": ["exact", "lt", "lte", "gt", "gte"],

            "date_created": ["exact", "lt", "lte", "gt", "gte"],
            "date_updated": ["exact", "lt", "lte", "gt", "gte"],
            "is_deleted": ["exact"],
            "version": ["exact"],
        }

    @classmethod
    def get_base_filters_invoice_payment(cls):
        return {
            "id": ["exact"],
            "status": ["exact"],

            "code_ext": ["istartswith", "icontains", "iexact"],
            "code_receipt": ["istartswith", "icontains", "iexact"],

            "label": ["istartswith", "iexact"],

            "amount_payed": ["exact", "lt", "lte", "gt", "gte"],
            "fees": ["exact", "lt", "lte", "gt", "gte"],
            "amount_received": ["exact", "lt", "lte", "gt", "gte"],

            "date_payment": ["exact", "lt", "lte", "gt", "gte"],

            "date_created": ["exact", "lt", "lte", "gt", "gte"],
            "date_updated": ["exact", "lt", "lte", "gt", "gte"],
            "is_deleted": ["exact"],
            "version": ["exact"],
        }

    @classmethod
    def get_base_filters_invoice_event(cls):
        return {
            "id": ["exact"],
            "event_type": ["exact", "lt", "lte", "gt", "gte"],
            "message": ["istartswith", "icontains", "iexact"],

            "date_created": ["exact", "lt", "lte", "gt", "gte"],
            "date_updated": ["exact", "lt", "lte", "gt", "gte"],
            "is_deleted": ["exact"],
            "version": ["exact"],
        }
