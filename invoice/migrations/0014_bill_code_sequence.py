from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0013_alter_bill_code_ext_alter_bill_code_tp_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE SEQUENCE IF NOT EXISTS bill_code_seq;",
            reverse_sql="DROP SEQUENCE IF EXISTS bill_code_seq;",
        ),
        migrations.RunSQL(
            sql="""
            DO $$
            DECLARE max_val BIGINT;
            BEGIN
                SELECT COALESCE(MAX(
                    CASE WHEN "Code" ~ '^[0-9]+$' THEN "Code"::BIGINT
                         WHEN "Code" ~ '-([0-9]+)$' THEN (regexp_match("Code", '-([0-9]+)$'))[1]::BIGINT
                         ELSE 0 END
                ), 0) INTO max_val FROM "tblBill";
                IF max_val > 0 THEN PERFORM setval('bill_code_seq', max_val); END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION set_bill_code()
            RETURNS TRIGGER AS $$
            BEGIN
                IF NEW."Code" IS NULL OR NEW."Code" = '' THEN
                    NEW."Code" := 'BIL-' || to_char(now(), 'YY') || '-'
                                  || lpad(nextval('bill_code_seq')::text, 10, '0');
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS bill_code_trigger ON "tblBill";
            CREATE TRIGGER bill_code_trigger
                BEFORE INSERT ON "tblBill"
                FOR EACH ROW EXECUTE FUNCTION set_bill_code();
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS bill_code_trigger ON "tblBill";
            DROP FUNCTION IF EXISTS set_bill_code();
            """,
        ),
    ]
