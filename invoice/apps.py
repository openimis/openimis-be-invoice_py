import logging

from django.apps import AppConfig

MODULE_NAME = 'invoice'

DEFAULT_CONFIG = {
    "default_currency_code": "USD",
    "gql_invoice_search_perms": ["155101"],
    "gql_invoice_create_perms": ["155102"],
    "gql_invoice_update_perms": ["155103"],
    "gql_invoice_delete_perms": ["155104"],
    "gql_invoice_amend_perms":  ["155109"],

    "gql_invoice_payment_search_perms": ["155201"],
    "gql_invoice_payment_create_perms": ["155202"],
    "gql_invoice_payment_update_perms": ["155203"],
    "gql_invoice_payment_delete_perms": ["155204"],
    "gql_invoice_payment_refund_perms": ["155206"],

    "gql_invoice_event_search_perms":             ["155201"],
    "gql_invoice_event_create_perms":             ["155202"],
    "gql_invoice_event_update_perms":             ["155203"],
    "gql_invoice_event_delete_perms":             ["155204"],
    "gql_invoice_event_create_message_perms":     ["155206"],
    "gql_invoice_event_delete_my_message_perms":  ["155206"],
    "gql_invoice_event_delete_all_message_perms": ["155206"],
}

logger = logging.getLogger(__name__)


class InvoiceConfig(AppConfig):
    name = MODULE_NAME

    default_currency_code = None
    gql_invoice_search_perms = None
    gql_invoice_create_perms = None
    gql_invoice_update_perms = None
    gql_invoice_delete_perms = None
    gql_invoice_amend_perms = None
    gql_invoice_payment_search_perms = None
    gql_invoice_payment_create_perms = None
    gql_invoice_payment_update_perms = None
    gql_invoice_payment_delete_perms = None
    gql_invoice_payment_refund_perms = None
    gql_invoice_event_search_perms = None
    gql_invoice_event_create_perms = None
    gql_invoice_event_update_perms = None
    gql_invoice_event_delete_perms = None
    gql_invoice_event_create_message_perms = None
    gql_invoice_event_delete_my_message_perms = None
    gql_invoice_event_delete_all_message_perms = None

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CONFIG)
        self._configure_perms(cfg)

    def _configure_perms(self, cfg):
        InvoiceConfig.default_currency_code = cfg["default_currency_code"]
        InvoiceConfig.gql_invoice_search_perms = cfg["gql_invoice_search_perms"]
        InvoiceConfig.gql_invoice_create_perms = cfg["gql_invoice_create_perms"]
        InvoiceConfig.gql_invoice_update_perms = cfg["gql_invoice_update_perms"]
        InvoiceConfig.gql_invoice_delete_perms = cfg["gql_invoice_delete_perms"]
        InvoiceConfig.gql_invoice_amend_perms = cfg["gql_invoice_amend_perms"]
        InvoiceConfig.gql_invoice_payment_search_perms = cfg["gql_invoice_payment_search_perms"]
        InvoiceConfig.gql_invoice_payment_create_perms = cfg["gql_invoice_payment_create_perms"]
        InvoiceConfig.gql_invoice_payment_update_perms = cfg["gql_invoice_payment_update_perms"]
        InvoiceConfig.gql_invoice_payment_delete_perms = cfg["gql_invoice_payment_delete_perms"]
        InvoiceConfig.gql_invoice_payment_refund_perms = cfg["gql_invoice_payment_refund_perms"]
        InvoiceConfig.gql_invoice_event_search_perms = cfg["gql_invoice_event_search_perms"]
        InvoiceConfig.gql_invoice_event_create_perms = cfg["gql_invoice_event_create_perms"]
        InvoiceConfig.gql_invoice_event_update_perms = cfg["gql_invoice_event_update_perms"]
        InvoiceConfig.gql_invoice_event_delete_perms = cfg["gql_invoice_event_delete_perms"]
        InvoiceConfig.gql_invoice_event_create_message_perms = cfg["gql_invoice_event_create_message_perms"]
        InvoiceConfig.gql_invoice_event_delete_my_message_perms = cfg["gql_invoice_event_delete_my_message_perms"]
        InvoiceConfig.gql_invoice_event_delete_all_message_perms = cfg["gql_invoice_event_delete_all_message_perms"]
