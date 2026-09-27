from django.conf import settings
from django.db import models
from graphql import ResolveInfo

from core.models import HistoryModelManager


class GenericInvoiceManager(HistoryModelManager):
    def filter(self, *args, **kwargs):
        keys = [x for x in kwargs if "itemsvc" in x]
        for key in keys:
            new_key = key.replace("itemsvc", self.model.model_prefix)
            kwargs[new_key] = kwargs.pop(key)
        return super(GenericInvoiceManager, self).filter(*args, **kwargs)


class GenericInvoiceQuerysetMixin:
    """Soft-delete filtering; row security itself is the model's `row_scope`.

    This sits ahead of the shared bases in the MRO, so it must hand the
    queryset on rather than return it: swallowing it here left every invoice
    model's declared scope unapplied.
    """

    @classmethod
    def get_queryset(cls, queryset, user):
        queryset = cls.filter_queryset(queryset)
        if isinstance(user, ResolveInfo):
            user = user.context.user
        if settings.ROW_SECURITY and user is not None and user.is_anonymous:
            return queryset.none()
        return super().get_queryset(queryset, user)
