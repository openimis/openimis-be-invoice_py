import logging

from django.apps import AppConfig

from core.bootstrap import rerun_after_migrate, skip_without_database
from core.rights_declaration import RightsDeclaration
from core.utils import ConfigUtilMixin

MODULE_NAME = 'invoice'


# Rights, by entity then by action. Same structure as `core.apps.DJANGO_PERMS`.
#
# The module carries two symmetric families of documents - the invoice issued to a
# third party (`invoice`, 1551xx) and the bill received (`bill`, 1561xx) - each with its
# block of payments (1552xx / 1562xx) and its block of events (1553xx / 1563xx). The
# entities are separate because the identifiers are: a role may read the invoices
# without reading the bills.
#
# The `PaymentInvoice` / `DetailPaymentInvoice` models (the "new approach" payment
# tables) have no block of their own: the code checks them with `invoicePayment`'s
# rights (155201-155204). They are therefore not declared as a distinct entity, for
# want of config keys that would belong to them - giving them a block presupposes
# minting new identifiers, which is a catalogue decision.
#
# `app_label` is "invoice" for all ten models: Bill and PaymentInvoice live in
# `invoice/models.py`, despite the table names `tblBill` / `tblPaymentInvoice`.
DJANGO_PERMS = {
    "invoice": {
        "query": ("invoice.view_invoice", 155101),
        "create": ("invoice.add_invoice", 155102),
        "update": ("invoice.change_invoice", 155103),
        "delete": ("invoice.delete_invoice", 155104),
        # `amend` creates a new version of the invoice rather than modifying it: a
        # business action, not an `update`.
        "amend": ("invoice.amend_invoice", 155109),
    },
    "invoicePayment": {
        "query": ("invoice.view_invoicepayment", 155201),
        "create": ("invoice.add_invoicepayment", 155202),
        "update": ("invoice.change_invoicepayment", 155203),
        "delete": ("invoice.delete_invoicepayment", 155204),
        # Rembourser n'est ni creer ni supprimer un paiement : identifiant propre.
        "refund": ("invoice.refund_invoicepayment", 155206),
    },
    "invoiceEvent": {
        "query": ("invoice.view_invoiceevent", 155301),
        "create": ("invoice.add_invoiceevent", 155302),
        "update": ("invoice.change_invoiceevent", 155303),
        "delete": ("invoice.delete_invoiceevent", 155304),
        # An event may be a system fact or a user message; the three "message"
        # actions have their own identifiers because a role may comment on an invoice
        # without being able to touch its event log, and because deleting *one's own*
        # message and deleting *other people's* are not granted together.
        "createMessage": ("invoice.create_message_invoiceevent", 155306),
        "deleteMyMessage": ("invoice.delete_my_message_invoiceevent", 155307),
        "deleteAllMessage": ("invoice.delete_all_message_invoiceevent", 155308),
    },
    "bill": {
        "query": ("invoice.view_bill", 156101),
        "create": ("invoice.add_bill", 156102),
        "update": ("invoice.change_bill", 156103),
        "delete": ("invoice.delete_bill", 156104),
        "amend": ("invoice.amend_bill", 156109),
    },
    "billPayment": {
        "query": ("invoice.view_billpayment", 156201),
        "create": ("invoice.add_billpayment", 156202),
        "update": ("invoice.change_billpayment", 156203),
        "delete": ("invoice.delete_billpayment", 156204),
        "refund": ("invoice.refund_billpayment", 156206),
    },
    "billEvent": {
        "query": ("invoice.view_billevent", 156301),
        "create": ("invoice.add_billevent", 156302),
        "update": ("invoice.change_billevent", 156303),
        "delete": ("invoice.delete_billevent", 156304),
        "createMessage": ("invoice.create_message_billevent", 156306),
        "deleteMyMessage": ("invoice.delete_my_message_billevent", 156307),
        "deleteAllMessage": ("invoice.delete_all_message_billevent", 156308),
    },
}

# The keys marked "dormant" are read nowhere in the assembly: the right is declared and
# grantable to a role, but no check requires it today. We keep them - deployed roles
# already carry them - without inventing a call site for them.
_PERM_CFG = {
    "gql_invoice_search_perms": ("invoice", "query"),
    "gql_invoice_create_perms": ("invoice", "create"),
    "gql_invoice_update_perms": ("invoice", "update"),
    "gql_invoice_delete_perms": ("invoice", "delete"),
    "gql_invoice_amend_perms": ("invoice", "amend"),  # dormante
    "gql_invoice_payment_search_perms": ("invoicePayment", "query"),
    "gql_invoice_payment_create_perms": ("invoicePayment", "create"),
    "gql_invoice_payment_update_perms": ("invoicePayment", "update"),
    "gql_invoice_payment_delete_perms": ("invoicePayment", "delete"),
    "gql_invoice_payment_refund_perms": ("invoicePayment", "refund"),  # dormante
    "gql_invoice_event_search_perms": ("invoiceEvent", "query"),
    "gql_invoice_event_create_perms": ("invoiceEvent", "create"),  # dormante
    "gql_invoice_event_update_perms": ("invoiceEvent", "update"),  # dormante
    "gql_invoice_event_delete_perms": ("invoiceEvent", "delete"),  # dormante
    "gql_invoice_event_create_message_perms": ("invoiceEvent", "createMessage"),
    "gql_invoice_event_delete_my_message_perms": ("invoiceEvent", "deleteMyMessage"),
    "gql_invoice_event_delete_all_message_perms": ("invoiceEvent", "deleteAllMessage"),  # dormante
    "gql_bill_search_perms": ("bill", "query"),
    "gql_bill_create_perms": ("bill", "create"),
    "gql_bill_update_perms": ("bill", "update"),
    "gql_bill_delete_perms": ("bill", "delete"),
    "gql_bill_amend_perms": ("bill", "amend"),  # dormante
    "gql_bill_payment_search_perms": ("billPayment", "query"),
    "gql_bill_payment_create_perms": ("billPayment", "create"),
    "gql_bill_payment_update_perms": ("billPayment", "update"),
    "gql_bill_payment_delete_perms": ("billPayment", "delete"),
    "gql_bill_payment_refund_perms": ("billPayment", "refund"),  # dormante
    "gql_bill_event_search_perms": ("billEvent", "query"),
    "gql_bill_event_create_perms": ("billEvent", "create"),  # dormante
    "gql_bill_event_update_perms": ("billEvent", "update"),  # dormante
    "gql_bill_event_delete_perms": ("billEvent", "delete"),  # dormante
    "gql_bill_event_create_message_perms": ("billEvent", "createMessage"),
    "gql_bill_event_delete_my_message_perms": ("billEvent", "deleteMyMessage"),
    "gql_bill_event_delete_all_message_perms": ("billEvent", "deleteAllMessage"),  # dormante
}

RIGHTS = RightsDeclaration(MODULE_NAME, DJANGO_PERMS, _PERM_CFG)

perms = RIGHTS.perms
django_perms = RIGHTS.django_perm_names
configured_perms = RIGHTS.configured
require = RIGHTS.require


DEFAULT_CONFIG = {
    "default_currency_code": "USD",


    # Functions of type Callable[[QuerySet, User], QuerySet], to be used as custom user filters for bills and invoices
    # To be specified as "module_name.submodule.function_name"
    "bill_user_filter_function": None,
    "invoice_user_filter_function": None,
    "bill_code_pattern": "BIL-[YY]-[SEQ:10]",
}

logger = logging.getLogger(__name__)


class InvoiceConfig(AppConfig, ConfigUtilMixin):
    name = MODULE_NAME

    default_currency_code = None
    # Rights: constants derived from DJANGO_PERMS, no longer overridable. They go
    # neither through DEFAULT_CFG nor through ready():
    # `ModuleConfiguration.get_or_default` now ignores any `_perms` key stored in the
    # database.
    gql_invoice_search_perms = RIGHTS.perms("invoice", "query")
    gql_invoice_create_perms = RIGHTS.perms("invoice", "create")
    gql_invoice_update_perms = RIGHTS.perms("invoice", "update")
    gql_invoice_delete_perms = RIGHTS.perms("invoice", "delete")
    gql_invoice_amend_perms = RIGHTS.perms("invoice", "amend")

    gql_invoice_payment_search_perms = RIGHTS.perms("invoicePayment", "query")
    gql_invoice_payment_create_perms = RIGHTS.perms("invoicePayment", "create")
    gql_invoice_payment_update_perms = RIGHTS.perms("invoicePayment", "update")
    gql_invoice_payment_delete_perms = RIGHTS.perms("invoicePayment", "delete")
    gql_invoice_payment_refund_perms = RIGHTS.perms("invoicePayment", "refund")

    gql_invoice_event_search_perms = RIGHTS.perms("invoiceEvent", "query")
    gql_invoice_event_create_perms = RIGHTS.perms("invoiceEvent", "create")
    gql_invoice_event_update_perms = RIGHTS.perms("invoiceEvent", "update")
    gql_invoice_event_delete_perms = RIGHTS.perms("invoiceEvent", "delete")
    gql_invoice_event_create_message_perms = RIGHTS.perms("invoiceEvent", "createMessage")
    gql_invoice_event_delete_my_message_perms = RIGHTS.perms("invoiceEvent", "deleteMyMessage")
    gql_invoice_event_delete_all_message_perms = RIGHTS.perms("invoiceEvent", "deleteAllMessage")

    gql_bill_search_perms = RIGHTS.perms("bill", "query")
    gql_bill_create_perms = RIGHTS.perms("bill", "create")
    gql_bill_update_perms = RIGHTS.perms("bill", "update")
    gql_bill_delete_perms = RIGHTS.perms("bill", "delete")
    gql_bill_amend_perms = RIGHTS.perms("bill", "amend")

    gql_bill_payment_search_perms = RIGHTS.perms("billPayment", "query")
    gql_bill_payment_create_perms = RIGHTS.perms("billPayment", "create")
    gql_bill_payment_update_perms = RIGHTS.perms("billPayment", "update")
    gql_bill_payment_delete_perms = RIGHTS.perms("billPayment", "delete")
    gql_bill_payment_refund_perms = RIGHTS.perms("billPayment", "refund")

    gql_bill_event_search_perms = RIGHTS.perms("billEvent", "query")
    gql_bill_event_create_perms = RIGHTS.perms("billEvent", "create")
    gql_bill_event_update_perms = RIGHTS.perms("billEvent", "update")
    gql_bill_event_delete_perms = RIGHTS.perms("billEvent", "delete")
    gql_bill_event_create_message_perms = RIGHTS.perms("billEvent", "createMessage")
    gql_bill_event_delete_my_message_perms = RIGHTS.perms("billEvent", "deleteMyMessage")
    gql_bill_event_delete_all_message_perms = RIGHTS.perms("billEvent", "deleteAllMessage")

    bill_user_filter = None
    invoice_user_filter = None
    bill_code_pattern = None
    bill_trigger_synced = False

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CONFIG)
        self._load_config_fields(cfg)
        if cfg['bill_user_filter_function']:
            self._load_config_function('bill_user_filter', cfg['bill_user_filter_function'])
        if cfg['invoice_user_filter_function']:
            self._load_config_function('invoice_user_filter', cfg['invoice_user_filter_function'])
        self._sync_bill_trigger()
        self._connect_migrate_signal()
        self._connect_config_signal()

    # ready() runs before migrations, so on a fresh database the table the trigger
    # attaches to does not exist yet; _connect_migrate_signal retries it then.
    @skip_without_database("bill code trigger sync", logger)
    def _sync_bill_trigger(self):
        InvoiceConfig.bill_trigger_synced = False
        from invoice.models import Bill
        from invoice.trigger_sync import sync_trigger
        sync_trigger(
            model=Bill,
            sequence_name='bill_code_seq',
            trigger_name='bill_code_trigger',
            code_column='Code',
            pattern=self.bill_code_pattern or DEFAULT_CONFIG['bill_code_pattern'],
            pg_function_name='set_bill_code',
        )
        InvoiceConfig.bill_trigger_synced = True

    def _connect_migrate_signal(self):
        rerun_after_migrate(self, self._sync_bill_trigger, "invoice.bill_code_trigger_post_migrate")

    def _connect_config_signal(self):
        from django.db.models.signals import post_save
        from core.models import ModuleConfiguration
        post_save.connect(
            self._on_config_change, sender=ModuleConfiguration,
            dispatch_uid='invoice.bill_code_trigger_sync',
        )

    @staticmethod
    def _on_config_change(sender, instance, **kwargs):
        import json
        if instance.module != MODULE_NAME or instance.layer != 'be':
            return
        try:
            cfg = json.loads(instance.config) if isinstance(instance.config, str) else instance.config
            pattern = cfg.get('bill_code_pattern') or DEFAULT_CONFIG['bill_code_pattern']
            from invoice.models import Bill
            from invoice.trigger_sync import sync_trigger, validate_pattern
            validate_pattern(pattern)
            InvoiceConfig.bill_code_pattern = pattern
            sync_trigger(
                model=Bill,
                sequence_name='bill_code_seq',
                trigger_name='bill_code_trigger',
                code_column='Code',
                pattern=pattern,
                pg_function_name='set_bill_code',
            )
            InvoiceConfig.bill_trigger_synced = True
            logger.info(f"Bill trigger updated after config change (pattern: {pattern})")
        except Exception as e:
            InvoiceConfig.bill_trigger_synced = False
            logger.error(f"Failed to sync bill trigger after config change: {e}", exc_info=True)
