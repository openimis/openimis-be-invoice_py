"""
Guard rails on invoice's rights declaration.

Same structure as `claim`, `product` and `contribution_plan`: `DJANGO_PERMS` by entity
then by action, `_PERM_CFG` deriving the config keys from it, and a `get_rights` on
each main model which is only an access point.

What is locked down here is the entity/action pair, not only the values:
  * an identifier in one place only (DJANGO_PERMS), hence no drift between the
    DEFAULT_CONFIG and the check;
  * a config key with no class attribute is never loaded by `_load_config_fields` and
    reading it raises AttributeError - the right becomes unenforceable;
  * `has_perms([])` returns True, so an empty list grants to everybody.

The module carries six entities, two symmetric families of three: the invoice issued
(1551xx / 1552xx / 1553xx) and the bill received (1561xx / 1562xx / 1563xx). No
identifier is shared between them, and the test below verifies it.
"""

import json
import os

from django.test import TestCase

from invoice.apps import (
    DJANGO_PERMS,
    InvoiceConfig,
    _PERM_CFG,
    configured_perms,
    django_perms,
    perms,
)
from invoice.models import (
    Bill,
    BillEvent,
    BillItem,
    BillPayment,
    DetailPaymentInvoice,
    Invoice,
    InvoiceEvent,
    InvoiceLineItem,
    InvoicePayment,
    PaymentInvoice,
)

# The identifiers as deployed. Changing one is incompatible with the existing roles:
# this test has to be updated *and* the new right granted.
EXPECTED_RIGHTS = {
    "gql_invoice_search_perms": ["155101"],
    "gql_invoice_create_perms": ["155102"],
    "gql_invoice_update_perms": ["155103"],
    "gql_invoice_delete_perms": ["155104"],
    "gql_invoice_amend_perms": ["155109"],
    "gql_invoice_payment_search_perms": ["155201"],
    "gql_invoice_payment_create_perms": ["155202"],
    "gql_invoice_payment_update_perms": ["155203"],
    "gql_invoice_payment_delete_perms": ["155204"],
    "gql_invoice_payment_refund_perms": ["155206"],
    "gql_invoice_event_search_perms": ["155301"],
    "gql_invoice_event_create_perms": ["155302"],
    "gql_invoice_event_update_perms": ["155303"],
    "gql_invoice_event_delete_perms": ["155304"],
    "gql_invoice_event_create_message_perms": ["155306"],
    "gql_invoice_event_delete_my_message_perms": ["155307"],
    "gql_invoice_event_delete_all_message_perms": ["155308"],
    "gql_bill_search_perms": ["156101"],
    "gql_bill_create_perms": ["156102"],
    "gql_bill_update_perms": ["156103"],
    "gql_bill_delete_perms": ["156104"],
    "gql_bill_amend_perms": ["156109"],
    "gql_bill_payment_search_perms": ["156201"],
    "gql_bill_payment_create_perms": ["156202"],
    "gql_bill_payment_update_perms": ["156203"],
    "gql_bill_payment_delete_perms": ["156204"],
    "gql_bill_payment_refund_perms": ["156206"],
    "gql_bill_event_search_perms": ["156301"],
    "gql_bill_event_create_perms": ["156302"],
    "gql_bill_event_update_perms": ["156303"],
    "gql_bill_event_delete_perms": ["156304"],
    "gql_bill_event_create_message_perms": ["156306"],
    "gql_bill_event_delete_my_message_perms": ["156307"],
    "gql_bill_event_delete_all_message_perms": ["156308"],
}

# The `permissions_map.json` entries that carry these identifiers. The historical name
# in the openIMIS catalogue is not the django name declared in DJANGO_PERMS: what has to
# stay stable is the integer.
EXPECTED_MAP_ENTRIES = {
    "invoice.invoice_search": "155101",
    "invoice.invoice_create": "155102",
    "invoice.invoice_update": "155103",
    "invoice.invoice_delete": "155104",
    "invoice.invoice_amend": "155109",
    "invoice.invoice_payment_search": "155201",
    "invoice.invoice_payment_create": "155202",
    "invoice.invoice_payment_update": "155203",
    "invoice.invoice_payment_delete": "155204",
    "invoice.invoice_payment_refund": "155206",
    "invoice.invoice_event_search": "155301",
    "invoice.invoice_event_create": "155302",
    "invoice.invoice_event_update": "155303",
    "invoice.invoice_event_delete": "155304",
    "invoice.invoice_event_create_message": "155306",
    "invoice.invoice_event_delete_my_message": "155307",
    "invoice.invoice_event_delete_all_message": "155308",
    "invoice.bill_search": "156101",
    "invoice.bill_create": "156102",
    "invoice.bill_update": "156103",
    "invoice.bill_delete": "156104",
    "invoice.bill_amend": "156109",
    "invoice.bill_payment_search": "156201",
    "invoice.bill_payment_create": "156202",
    "invoice.bill_payment_update": "156203",
    "invoice.bill_payment_delete": "156204",
    "invoice.bill_payment_refund": "156206",
    "invoice.bill_event_search": "156301",
    "invoice.bill_event_create": "156302",
    "invoice.bill_event_update": "156303",
    "invoice.bill_event_delete": "156304",
    "invoice.bill_event_create_message": "156306",
    "invoice.bill_event_delete_my_message": "156307",
    "invoice.bill_event_delete_all_message": "156308",
}

# Keys declared but which no call site reads, in this module as elsewhere in the
# assembly. Kept because the identifiers are already granted to deployed roles; listed
# here so that adding a reader, or removing the key, is a visible decision.
DORMANT_KEYS = {
    "gql_invoice_amend_perms",
    "gql_invoice_payment_refund_perms",
    "gql_invoice_event_create_perms",
    "gql_invoice_event_update_perms",
    "gql_invoice_event_delete_perms",
    "gql_invoice_event_delete_all_message_perms",
    "gql_bill_amend_perms",
    "gql_bill_payment_refund_perms",
    "gql_bill_event_create_perms",
    "gql_bill_event_update_perms",
    "gql_bill_event_delete_perms",
    "gql_bill_event_delete_all_message_perms",
}

MODEL_BY_ENTITY = {
    "invoice": Invoice,
    "invoicePayment": InvoicePayment,
    "invoiceEvent": InvoiceEvent,
    "bill": Bill,
    "billPayment": BillPayment,
    "billEvent": BillEvent,
}

# Sub-resource -> owning FK -> expected parent model.
SUB_RESOURCES = {
    InvoiceLineItem: ("invoice", Invoice),
    BillItem: ("bill", Bill),
    DetailPaymentInvoice: ("payment", PaymentInvoice),
}


def _permissions_map():
    """`permissions_map.json` lives in the assembly, not in the package."""
    from django.conf import settings

    candidates = [
        os.path.join(str(settings.BASE_DIR), "permissions_map.json"),
        os.path.join(os.path.dirname(str(settings.BASE_DIR)), "permissions_map.json"),
    ]
    for path in candidates:
        if os.path.exists(path):
            with open(path) as handle:
                return json.load(handle)
    return None


class InvoicePermissionDeclarationTestCase(TestCase):
    def test_right_ids_unchanged(self):
        self.assertEqual(
            {key: getattr(InvoiceConfig, key) for key in EXPECTED_RIGHTS},
            EXPECTED_RIGHTS,
        )

    def test_every_config_key_is_pinned(self):
        """All 34 of the module's keys are pinned above."""
        self.assertEqual(set(_PERM_CFG), set(EXPECTED_RIGHTS))

    def test_perm_cfg_covers_every_declared_action(self):
        declared = {
            (entity, action)
            for entity, actions in DJANGO_PERMS.items()
            for action in actions
        }
        self.assertEqual(set(_PERM_CFG.values()), declared)

    def test_perm_cfg_matches_config_attributes(self):
        """`_load_config_fields` ignores the keys with no class attribute."""
        missing = [key for key in _PERM_CFG if not hasattr(InvoiceConfig, key)]
        self.assertEqual(missing, [])

    def test_no_right_list_is_empty(self):
        empty = [key for key in _PERM_CFG if not getattr(InvoiceConfig, key)]
        self.assertEqual(empty, [])

    def test_attributes_carry_the_declared_right(self):
        for key, (entity, action) in _PERM_CFG.items():
            with self.subTest(key=key):
                self.assertEqual(getattr(InvoiceConfig, key), perms(entity, action))

    def test_the_six_entities_share_no_right_id(self):
        """Six objets metier distincts, six blocs d'identifiants disjoints."""
        seen = {}
        for entity, actions in DJANGO_PERMS.items():
            for action, (_, right_id) in actions.items():
                seen.setdefault(right_id, []).append(f"{entity}.{action}")
        shared = {right: who for right, who in seen.items() if len(who) > 1}
        self.assertEqual(shared, {})

    def test_django_permission_names_are_unique(self):
        seen = {}
        for entity, actions in DJANGO_PERMS.items():
            for action, (name, _) in actions.items():
                seen.setdefault(name, []).append(f"{entity}.{action}")
        shared = {name: who for name, who in seen.items() if len(who) > 1}
        self.assertEqual(shared, {})

    def test_django_permission_names_use_the_real_app_label(self):
        """
        Bill and PaymentInvoice live in `invoice/models.py`: their app_label is
        "invoice", not the name of their table.
        """
        for entity, model in MODEL_BY_ENTITY.items():
            for action in DJANGO_PERMS[entity]:
                with self.subTest(entity=entity, action=action):
                    name = django_perms(entity, action)[0]
                    self.assertTrue(name.startswith(f"{model._meta.app_label}."))
                    self.assertTrue(name.endswith(f"_{model._meta.model_name}"))

    def test_unknown_entity_or_action_raises(self):
        with self.assertRaises(KeyError):
            perms("nosuchentity", "query")
        with self.assertRaises(KeyError):
            perms("invoice", "nosuchaction")
        with self.assertRaises(KeyError):
            django_perms("bill", "nosuchaction")

    def test_dormant_keys_are_still_declared(self):
        """
        Nobody reads them; they must carry their identifier all the same, and not [],
        otherwise the day a check does read them it will grant the action to everybody.
        """
        for key in DORMANT_KEYS:
            with self.subTest(key=key):
                self.assertIn(key, _PERM_CFG)
                self.assertEqual(getattr(InvoiceConfig, key), EXPECTED_RIGHTS[key])

    def test_ids_match_permissions_map(self):
        mapping = _permissions_map()
        if mapping is None:
            self.skipTest("permissions_map.json absent de cet assemblage")
        actual = {name: mapping.get(name) for name in EXPECTED_MAP_ENTRIES}
        self.assertEqual(actual, EXPECTED_MAP_ENTRIES)

    # --- the access point through the model -------------------------------
    def test_each_model_exposes_every_action_of_its_entity(self):
        for entity, model in MODEL_BY_ENTITY.items():
            for action in DJANGO_PERMS[entity]:
                with self.subTest(entity=entity, action=action):
                    self.assertEqual(
                        model.get_rights(action), configured_perms(entity, action)
                    )
                    self.assertTrue(model.get_rights(action))

    def test_model_returns_none_for_an_undeclared_action(self):
        """None means "no rule": the caller must fail closed."""
        for model in MODEL_BY_ENTITY.values():
            with self.subTest(model=model.__name__):
                self.assertIsNone(model.get_rights("nosuchaction"))

    def test_model_reads_the_configured_value_not_the_declared_default(self):
        original = InvoiceConfig.gql_invoice_search_perms
        try:
            InvoiceConfig.gql_invoice_search_perms = ["999999"]
            self.assertEqual(Invoice.get_rights("query"), ["999999"])
            self.assertEqual(perms("invoice", "query"), ["155101"])
        finally:
            InvoiceConfig.gql_invoice_search_perms = original

    # --- the owned borrowing ------------------------------------------------
    def test_payment_invoice_borrows_the_invoice_payment_rights(self):
        """
        The `PaymentInvoice` / `DetailPaymentInvoice` tables have no block of their
        own: the GQL already checks them with 155201-155204. The borrowing is tested so
        that it stays a visible decision rather than an oversight.
        """
        for action in ("query", "create", "update", "delete", "refund"):
            with self.subTest(action=action):
                self.assertEqual(
                    PaymentInvoice.get_rights(action),
                    configured_perms("invoicePayment", action),
                )

    # --- the sub-resources -------------------------------------------------
    def test_sub_resources_delegate_to_their_owner(self):
        """
        Each has two relations and a single owner: the line takes the right of the
        document it belongs to, not that of the object it references.
        """
        from core.rights_scope import scope_parent_of

        for model, (field_name, parent) in SUB_RESOURCES.items():
            with self.subTest(model=model.__name__):
                self.assertEqual(model.scope_parent, field_name)
                self.assertIs(scope_parent_of(model), parent)
                self.assertFalse("get_rights" in model.__dict__)

    def test_payments_and_events_are_not_sub_resources(self):
        """
        They have an FK to their invoice but a block of rights of their own: attaching
        them to the document would grant the payment to whoever can read the invoice.
        """
        for model in (InvoicePayment, InvoiceEvent, BillPayment, BillEvent):
            with self.subTest(model=model.__name__):
                self.assertFalse(getattr(model, "scope_parent", None))
