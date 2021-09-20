from abc import ABC

from core.models import HistoryModel
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from typing import Type

from invoice_payment.models import Invoice


class BaseModelValidation(ABC):
    """
    Base validation class, by default all operations are unconditionally allowed.
    Validation methods should raise ValidationError in case of any data inconsistencies.
    """
    @property
    def OBJECT_TYPE(self) -> Type[HistoryModel]:
        """
        Django ORM model. It's expected that it'll be inheriting from HistoryModel.
        """
        raise NotImplementedError("Class has to define OBJECT_TYPE for service.")

    @classmethod
    def validate_create(cls, user, **data):
        pass

    @classmethod
    def validate_update(cls, user, **data):
        pass

    @classmethod
    def validate_delete(cls, user, **data):
        pass


class UniqueCodeValidationMixin:
    CODE_DUPLICATE_MSG = _("Object code %(code)s is not unique.")

    @classmethod
    def validate_unique_code_name(cls, code, excluded_id=None):
        if not cls._unique_code_name(code, excluded_id):
            raise ValidationError(cls.CODE_DUPLICATE_MSG % {'code': code})

    @classmethod
    def _unique_code_name(cls, code, excluded_id=None):
        query = cls.OBJECT_TYPE.objects.filter(code=code)
        if excluded_id:
            query = query.exclude(id=excluded_id)

        return not query.exists()


class TaxAnalysisFormatValidationMixin:
    INVALID_TAX_ANALYSIS_JSON_FORMAT_NO_KEYS = _("Invalid tax_analysis format, 'total' and 'lines' keys are required.")

    INVALID_TAX_ANALYSIS_JSON_FORMAT_LINES_KEYS = _("tax_analysis.lines is not in list format.")

    INVALID_TAX_ANALYSIS_JSON_FORMAT_LINES_FORMAT = _("tax_analysis.lines content is not a dict.")

    @classmethod
    def validate_tax_analysis_format(cls, tax: dict):
        if tax and not cls._has_required_keys(tax):
            raise ValidationError(cls.INVALID_TAX_ANALYSIS_JSON_FORMAT_NO_KEYS)

        lines = tax['lines']
        if not isinstance(lines, list):
            raise ValidationError(cls.INVALID_TAX_ANALYSIS_JSON_FORMAT_LINES_KEYS)

        for line in lines:
            if not isinstance(line, dict):
                raise ValidationError(cls.INVALID_TAX_ANALYSIS_JSON_FORMAT_LINES_FORMAT)

    @classmethod
    def _has_required_keys(cls, tax: dict):
        keys = tax.keys()
        if 'total' not in keys or 'lines' not in keys:
            return False
        return True



class ObjectExistsValidationMixin:
    INVALID_UPDATE_ID_MSG = _("Invoice for id  %(id)s does not exists")

    @classmethod
    def validate_object_exists(cls, id_):
        existing = cls.OBJECT_TYPE.objects.filter(id=id_).first()
        if not existing:
            raise ValidationError(cls.INVALID_UPDATE_ID_MSG % {'id': id_})


class BaseInvoiceValidation(BaseModelValidation, UniqueCodeValidationMixin,
                            TaxAnalysisFormatValidationMixin, ObjectExistsValidationMixin, ABC):

    @classmethod
    def validate_create(cls, user, **data):
        cls.validate_unique_code_name(data.get('code', None))
        cls.validate_tax_analysis_format(data.get('tax_analysis', None))

    @classmethod
    def validate_update(cls, user, **data):
        cls.validate_object_exists(data.get('id', None))
        code = data.get('code', None)
        id_ = data.get('id', None)

        if code:
            cls.validate_unique_code_name(code, id_)

        cls.validate_tax_analysis_format(data.get('tax_analysis', None))
