from abc import ABC

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from invoice_payment.models import Invoice


class BaseModelValidation(ABC):
    """
    Base validation class, by default all operations are unconditionally allowed.
    Validation methods should raise ValidationError in case of any data inconsistencies.
    """

    @classmethod
    def validate_create(cls, user, **data):
        pass

    @classmethod
    def validate_update(cls, user, **data):
        pass

    @classmethod
    def validate_delete(cls, user, **data):
        pass
