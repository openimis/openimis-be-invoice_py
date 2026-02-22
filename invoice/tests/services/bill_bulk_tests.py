import uuid
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from core.models import User
from core.test_helpers import LogInHelper
from invoice.models import Bill, BillItem
from invoice.services import BillService

class BillBulkTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = LogInHelper().get_or_create_user_api(username='admin_bulk')

    def test_bulk_create_bills_success(self):
        """Verify that bulk_create_bills correctly persists multiple Bill instances."""
        bill_instances = []
        
        for i in range(5):
            bill_instances.append(Bill(
                id=uuid.uuid4(),
                subject_type=None,
                subject_id=None,
                code=f"BULK_BILL_{i}",
                status=Bill.Status.VALIDATED,
                user_created=self.user,
                user_updated=self.user,
                version=1
            ))
            
        created_bills = BillService.bulk_create_bills(bill_instances)
        self.assertEqual(len(created_bills), 5)
        self.assertEqual(Bill.objects.filter(code__startswith="BULK_BILL_").count(), 5)

    def test_bulk_create_bill_items_success(self):
        """Verify that bulk_create_bill_items correctly persists multiple BillItem instances."""
        bill = Bill.objects.create(
            code="PARENT_BILL",
            subject_type=None,
            subject_id=None,
            status=Bill.Status.VALIDATED,
            user_created=self.user,
            user_updated=self.user,
            version=1
        )
        
        item_instances = []
        for i in range(10):
            item_instances.append(BillItem(
                id=uuid.uuid4(),
                bill=bill,
                code=f"ITEM_{i}",
                amount_total=100.0,
                user_created=self.user,
                user_updated=self.user,
                version=1
            ))
            
        created_items = BillService.bulk_create_bill_items(item_instances)
        self.assertEqual(len(created_items), 10)
        self.assertEqual(BillItem.objects.filter(bill=bill).count(), 10)
