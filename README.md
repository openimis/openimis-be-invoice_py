# openimis-be-invoice_py

OpenIMIS backend module for invoices, bills, and payments.

## Bill Code Auto-Generation

`Bill.code` is auto-assigned by a database trigger and sequence (migration `0014_bill_code_sequence`). The trigger only fires when `code` is `NULL` or empty, so explicitly supplied codes are preserved.

### Code format

```
BIL-YY-XXXXXXXXXX
```

- `YY` — two-digit year of insertion (e.g. `25` for 2025)
- `XXXXXXXXXX` — zero-padded 10-digit monotonically increasing sequence number (e.g. `0000000042`)

Example: `BIL-25-0000000042`

### How it works

| Database | Mechanism |
|----------|-----------|
| PostgreSQL | `BEFORE INSERT` trigger on `tblBill`; calls `nextval('bill_code_seq')` |
| MSSQL | `INSTEAD OF INSERT` trigger on `tblBill`; uses `NEXT VALUE FOR bill_code_seq` to assign codes inline |

On first apply, the migration advances the sequence past the current maximum to avoid collisions.

### Migration

`invoice/migrations/0014_bill_code_sequence.py` — uses `RunPython` with vendor detection (`schema_editor.connection.vendor`).

To reverse: `python manage.py migrate invoice 0013`

### Maintainer note: MSSQL trigger column list

The MSSQL `INSTEAD OF INSERT` trigger explicitly lists every column of `tblBill` in its `INSERT ... SELECT` statement. This is intentional — an `AFTER INSERT` + `UPDATE` approach would double the write I/O for bulk inserts (critical for payroll generation with 100k+ rows).

**When adding or removing columns on `Bill` (or its abstract base `GenericInvoice`)**, you must create a new migration that recreates the trigger with the updated column list. Failure to do so will cause inserts to fail or silently drop values for new columns on MSSQL.
