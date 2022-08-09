import logging

from django.db import migrations

from core.utils import insert_role_right_for_system

logger = logging.getLogger(__name__)


def add_rights(apps, schema_editor):
    insert_role_right_for_system(4, 155101)  # Invoice search
    insert_role_right_for_system(4, 155102)  # Invoice create
    insert_role_right_for_system(4, 155103)  # Invoice update
    insert_role_right_for_system(4, 155104)  # Invoice delete
    insert_role_right_for_system(4, 155109)  # Invoice amend
    insert_role_right_for_system(4, 155201)  # Invoice payment search
    insert_role_right_for_system(4, 155202)  # Invoice payment create
    insert_role_right_for_system(4, 155203)  # Invoice payment update
    insert_role_right_for_system(4, 155204)  # Invoice payment delete
    insert_role_right_for_system(4, 155206)  # Invoice payment refund
    insert_role_right_for_system(4, 155301)  # Invoice Event search
    insert_role_right_for_system(4, 155302)  # Invoice Event create
    insert_role_right_for_system(4, 155303)  # Invoice Event update
    insert_role_right_for_system(4, 155304)  # Invoice Event delete
    insert_role_right_for_system(4, 155306)  # Invoice Event message
    insert_role_right_for_system(4, 155307)  # Invoice Event delete my message
    insert_role_right_for_system(4, 155308)  # Invoice Event delete all messages
    insert_role_right_for_system(4, 156101)  # Bill search
    insert_role_right_for_system(4, 156102)  # Bill create
    insert_role_right_for_system(4, 156103)  # Bill update
    insert_role_right_for_system(4, 156104)  # Bill delete
    insert_role_right_for_system(4, 156109)  # Bill amend
    insert_role_right_for_system(4, 156201)  # Bill Payment search
    insert_role_right_for_system(4, 156202)  # Bill Payment create
    insert_role_right_for_system(4, 156203)  # Bill Payment update
    insert_role_right_for_system(4, 156204)  # Bill Payment delete
    insert_role_right_for_system(4, 156206)  # Bill Payment refund
    insert_role_right_for_system(4, 156301)  # Bill Event search
    insert_role_right_for_system(4, 156302)  # Bill Event create
    insert_role_right_for_system(4, 156303)  # Bill Event update
    insert_role_right_for_system(4, 156304)  # Bill Event delete
    insert_role_right_for_system(4, 156306)  # Bill Event create message
    insert_role_right_for_system(4, 156307)  # Bill Event delete my message
    insert_role_right_for_system(4, 156308)  # Bill Event delete all messages


class Migration(migrations.Migration):
    dependencies = [
        ('invoice', '0004_invoice_bill_roles_for_admin')
    ]

    operations = [
        migrations.RunPython(add_rights),
    ]
