from django.test import TestCase
from .models import Invoice, Inventory, Companies


class InvoiceTestCase(TestCase):
    def setUp(self):
        self.company = Companies.objects.create(company_name="Test Company")
        self.item = Inventory.objects.create(item_name="Test Item", item_quantity=100,  item_cost=30, company_source=self.company)
        self.invoice = Invoice.objects.create(
            company=self.company,
            item=self.item,
            quantity_purchased=10,
            total_cost=500,
            payment_method='Installments',
            installments_count=5
        )
    
    def test_installments_due_dates(self):
        self.assertEqual(len(self.invoice.due_dates), 5)
    
    def test_make_payment(self):
        self.invoice.make_payment(100)
        self.assertEqual(self.invoice.total_paid, 100)
        self.assertEqual(self.invoice.remaining_amount, 400)