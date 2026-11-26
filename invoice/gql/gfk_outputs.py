"""
The GenericForeignKey outputs (subject, thirdparty, line) of the invoice lists,
loaded for the whole page at once by core.gfk (OP-3343).
"""
from core.gfk import prefetch_gfk

from invoice.utils import underscore_to_camel

# Targets whose output reads a relation as well: loaded with it.
TARGET_RELATED = {
    "insuree.Family": ("head_insuree",),
    "claim_batch.BatchRun": ("location",),
}


def prefetch_gfk_outputs(queryset, info, *gfk_names):
    return prefetch_gfk(queryset, *gfk_names, info=info, related=TARGET_RELATED)


def target_dict(obj):
    """The target's fields, camelCased, without changing the (possibly shared) instance."""
    return {underscore_to_camel(k): v for k, v in obj.__dict__.items() if k != '_state'}
