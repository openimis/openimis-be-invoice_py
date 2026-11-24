"""
Loading the GenericForeignKey outputs (subject, thirdparty, line) of a whole page
at once, instead of one query per row (OP-3343).
"""
from django.apps import apps
from django.contrib.contenttypes.prefetch import GenericPrefetch
from graphql.language import FragmentSpreadNode

from invoice.utils import underscore_to_camel

# Targets whose output reads a relation as well: loaded with it, per content type.
_TARGET_RELATIONS = {
    ("insuree", "Family"): ("head_insuree",),
    ("claim_batch", "BatchRun"): ("location",),
}


def _requested_fields(info):
    names = set()

    def walk(selection_set):
        for selection in selection_set.selections if selection_set else ():
            if isinstance(selection, FragmentSpreadNode):
                walk(info.fragments[selection.name.value].selection_set)
                continue
            if getattr(selection, "name", None):
                names.add(selection.name.value)
            walk(selection.selection_set)

    for field_node in info.field_nodes:
        walk(field_node.selection_set)
    return names


def _target_querysets():
    querysets = []
    for (app_label, model_name), relations in _TARGET_RELATIONS.items():
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            continue
        # _base_manager, as the GenericForeignKey itself uses: no row is hidden.
        querysets.append(model._base_manager.select_related(*relations))
    return querysets


def prefetch_gfk_outputs(queryset, info, *gfk_names):
    """Prefetch the requested GenericForeignKeys of the page and select their types."""
    requested = _requested_fields(info)
    for name in gfk_names:
        camel = underscore_to_camel(name)
        if name in requested or camel in requested:
            queryset = queryset.prefetch_related(GenericPrefetch(name, _target_querysets()))
        if requested & {camel, f"{camel}Type", f"{camel}TypeName"}:
            queryset = queryset.select_related(f"{name}_type")
    return queryset


def target_dict(obj):
    """The target's fields, camelCased, without changing the (possibly shared) instance."""
    return {underscore_to_camel(k): v for k, v in obj.__dict__.items() if k != '_state'}
