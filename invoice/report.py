from invoice.reports import bill_detail
from invoice.reports.bill_detail import bill_detail_query

report_definitions = [
    {
        "name": "bill_detail",
        "engine": 0,
        "default_report": bill_detail.template,
        "description": "Bill detail",
        "module": "invoice",
        "python_query": bill_detail_query,
        "permission": ["131217"],
    },
]
