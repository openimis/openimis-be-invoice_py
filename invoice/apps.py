import logging

from django.apps import AppConfig

MODULE_NAME = 'invoice'

DEFAULT_CONFIG = {
    "default_currency_code": "USD"
}

logger = logging.getLogger(__name__)


class InvoicePaymentConfig(AppConfig):
    name = MODULE_NAME

    default_currency_code = None

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CONFIG)
        self._configure_perms(cfg)

    def _configure_perms(self, cfg):
        InvoicePaymentConfig.default_currency_code = cfg["default_currency_code"]
