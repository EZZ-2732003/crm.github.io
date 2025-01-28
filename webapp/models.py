from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from datetime import date
from decimal import Decimal
from django.utils.timezone import now
from django.db.models import Sum
from django.db import transaction


# Create your models here.
# category model

    
    
class patient(models.Model):
    name = models.CharField(max_length=250)
    phone = models.CharField(max_length=20)
    country=models.CharField(max_length=40,default='none')
    address = models.CharField(max_length=255, default='Default Address') 
    created_at = models.DateTimeField (auto_now_add = True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    how_did_you_know_us=models.CharField(max_length=100,default='none')

    def __str__(self):
        return self.name  
    class Meta :
            ordering = ['-created_at']
        
class Service(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # سعر الخدمة

    def __str__(self):
        return self.name        
        

from django.db import models
from django.utils import timezone

class Reserve(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    ]
    BRANCH_CHOICES = [
        ('EL_Mohandsen', 'EL_Mohandsen'),
        ('5th_sattelment', '5th_sattelment'),
        ('Naser_city', 'Naser_city'),
    ]
    TYPE_CHOICES = [
        ('old', 'old'),
        ('new', 'new'),
    ]
    SERVICE_CHOICES = [
        
        ('SKINBOOSTER', 'Skinbooster'),
        ('FILLER', 'Filler'),
        ('DISSOLVING_FILLER', 'Dissolving Filler'),
        ('BOTOX', 'Botox'),
        ('RETOUCH', 'Retouch'),
        ('CONSULTATION', 'Consultation'),
        ('DERMA_PEN', 'Derma Pen'),
        ('LIP_FILLER', 'Lip Filler'),
        ('MESOTHERAPY', 'Mesotherapy'),
    ]

    patient_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES, default='old')
    date = models.DateField(default=timezone.now)
    time = models.CharField(max_length=10)
    services = models.CharField(default=list, max_length=1000)  # استخدام JSONField لتخزين قائمة الخدمات
    notes = models.CharField(max_length=1000, default='notes')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    Branch = models.CharField(max_length=50, choices=BRANCH_CHOICES, default='Branch')

    def __str__(self):
        return str(self.patient_name)

    def add_phone(self, new_phone):
        """إضافة رقم جديد إذا لم يكن موجودًا بالفعل."""
        existing_numbers = self.phone.split(", ")  # تفكيك الأرقام الحالية
        if new_phone not in existing_numbers:
            existing_numbers.append(new_phone)
            self.phone = ", ".join(existing_numbers)  # إعادة تجميع الأرقام
            self.save()

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # تحقق من حالة الحجز قبل حفظ الكائن
        if self.status == 'completed' and not patient.objects.filter(name=self.patient_name).exists():
            # إنشاء مريض جديد فقط إذا لم يكن موجودًا بالفعل في قاعدة البيانات
            patient.objects.create(
                name=self.patient_name,
                phone=self.phone,
                address='Default Address',  # أو قم بتعديل هذا إذا كان هناك عنوان معين
                created_at=self.created_at,
                date_of_birth=None,  # قم بتعديل هذا إذا كان هناك تاريخ ميلاد متاح
            )
        super().save(*args, **kwargs)
        
class ReservationService(models.Model):
    reserve = models.ForeignKey(Reserve, on_delete=models.CASCADE, related_name="reservation_services")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.reserve} - {self.service}"   

  

class Companies(models.Model):
    company_name = models.CharField(max_length=255)
    company_address = models.CharField(max_length=500)
    company_phone = models.CharField(max_length=20)


    def __str__(self):
        return self.company_name

    def get_total_due(self):
        """إجمالي المدفوعات المتبقية على الشركة"""
        return self.total_due - self.total_paid

    def get_inventory(self):
        """جلب جميع العناصر التي تم استيرادها من هذه الشركة"""
        return self.inventory_items.all()



class Inventory(models.Model):
    item_name = models.CharField(max_length=300)
    item_quantity = models.IntegerField()  # الكمية الموجودة في المخزن
    item_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    item_cost = models.DecimalField(max_digits=10, decimal_places=2)  # تكلفة المنتج
    company_source = models.ForeignKey(Companies, on_delete=models.CASCADE, related_name='inventory_items')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item_name

    def reduce_quantity(self, quantity):
        """تقليل الكمية من المخزون عند الاستهلاك"""
        if self.item_quantity >= quantity:
            self.item_quantity -= quantity
            self.save()
        

    def increase_quantity(self, quantity):
        """زيادة الكمية عند الشراء"""
        self.item_quantity += quantity
        self.save()

class ReservationInventory(models.Model):
    reserve = models.ForeignKey(Reserve, on_delete=models.CASCADE, related_name="reservation_inventories")
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.reserve} - {self.inventory}"      

class offers(models.Model):
    name = models.CharField(max_length=250)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    services = models.ManyToManyField(Service, through='OfferService')
    inventory = models.ManyToManyField(Inventory, through='OfferInventory')

    def is_active(self):
        now = timezone.now()
        return self.valid_from <= now <= self.valid_to

    def __str__(self):
        return self.name


class OfferService(models.Model):
    offer = models.ForeignKey(offers, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


class OfferInventory(models.Model):
    offer = models.ForeignKey(offers, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)



class Payment(models.Model):
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Cancelled', 'Cancelled'),
    ]
    METHOD_CHOICES = [
        ('INSTAPAY', 'INSTAPAY'),
        ('CASH', 'CASH'),
        ('CREDIT CARD', 'CREDIT CARD'),
        ('E_WALLET', 'E_WALLET'),
    ]
    BRANCH_CHOICES = [
        ('EL_Mohandsen', 'EL_Mohandsen'),
        ('5th_sattelment', '5th_sattelment'),
        ('Naser_city', 'Naser_city'),
    ]
    TYPE_CHOICES = [
        ('Pay', 'Pay'),
        ('Refund', 'Refund'),
    ]

    patient = models.CharField(max_length=100)
    Branch = models.CharField(max_length=50, choices=BRANCH_CHOICES, default='Branch')
    date = models.DateField(null=True, blank=True, default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    method = models.CharField(max_length=100, choices=METHOD_CHOICES, default='CASH')
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='Pay')
    services = models.ManyToManyField(Service, through='PaymentService')
    inventory = models.ManyToManyField(Inventory, through='PaymentInventory')


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.id} for {self.patient}"

    def get_total_service(self):
        """Calculate total cost of services."""
        return sum([ps.price_at_time_of_payment * ps.quantity for ps in self.paymentservice_set.all()])

    def get_total_products(self):
        """Calculate total cost of products."""
        return sum([pi.price_at_time_of_payment * pi.quantity for pi in self.paymentinventory_set.all()])

    def get_total_amount(self):
        """Total amount includes services and products."""
        return self.get_total_service() + self.get_total_products()

    def get_discount_amount(self):
        """Calculate the discount based on the offer."""
        if self.offer and self.offer.is_valid():
            if self.offer.discount_percentage:
                return (self.get_total_amount() * self.offer.discount_percentage) / 100
            elif self.offer.discount_amount:
                return min(self.get_total_amount(), self.offer.discount_amount)
        return 0

    def get_total_after_discount(self):
        """Calculate the total amount after applying the discount."""
        return self.get_total_amount() - self.get_discount_amount()

    def save(self, *args, **kwargs):
        """Override save to account for discounts and create financial transactions."""
        super().save(*args, **kwargs)
        if self.status == 'Paid':
            # Create or update Finance entries
            transaction_type = 'Income' if self.type == 'Pay' else 'Refund'
            finance_entry, created = Finance.objects.get_or_create(
                related_payment=self,
                defaults={
                    'transaction_type': transaction_type,
                    'amount': self.get_total_amount(),
                    'description': f"Payment {self.id}  for {self.patient}",
                    'date': self.date,
                }
            )
            if not created:
                # Update existing Finance entry
                finance_entry.amount = self.get_total_amount()
                finance_entry.description = f"Payment {self.id} for {self.patient}"
                finance_entry.save()


class PaymentService(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time_of_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.service.name} for {self.payment}"

    def save(self, *args, **kwargs):
        # Save the service price as static data
        if not self.price_at_time_of_payment:
            self.price_at_time_of_payment = self.service.price
        super().save(*args, **kwargs)


class PaymentInventory(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time_of_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.inventory.item_name} for {self.payment}"

    def save(self, *args, **kwargs):
        # Save the inventory item price as static data
        if not self.price_at_time_of_payment:
            self.price_at_time_of_payment = self.inventory.item_price
        super().save(*args, **kwargs)
        self.inventory.reduce_quantity(self.quantity)
    







class Invoice(models.Model):
    PAYMENT_METHODS = [
        ('Cash', 'Cash Payment'),
        ('Installments', 'Installment Payment'),
    ]
    company = models.ForeignKey(Companies, on_delete=models.CASCADE, related_name='invoices')
    item = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='invoices')
    quantity_purchased = models.IntegerField()
    quantity_used = models.IntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHODS, default='Cash')
    is_fully_paid = models.BooleanField(default=False)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    installments_count = models.IntegerField(null=True, blank=True)
    due_dates = models.JSONField(null=True, blank=True)
    payments = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Invoice for {self.quantity_purchased} of {self.item.item_name} from {self.company.company_name}"

    @transaction.atomic
    def save(self, *args, **kwargs):
        is_new_invoice = not self.pk  # Check if this is a new invoice

        # Call the parent save method
        super().save(*args, **kwargs)

        if is_new_invoice:  # Only execute this logic for new invoices
            # Update inventory stock
            self.item.increase_quantity(self.quantity_purchased)

            if self.payment_method == 'Cash':
                self.total_paid = self.total_cost
                self.remaining_amount = 0
                self.is_fully_paid = True

                # Create a Finance record for cash payment
                Finance.objects.create(
                    transaction_type='Expense',
                    amount=self.total_cost,
                    description=f"Cash payment for Invoice #{self.id}",
                    related_invoice=self,
                    created_at=self.created_at
                )
            elif self.payment_method == 'Installments' and self.installments_count:
                self.remaining_amount = self.total_cost
                self.due_dates = self.generate_installment_due_dates()

                # Optionally create an initial Finance record for installment setup
                Finance.objects.create(
                    transaction_type='Expense',
                    amount=0,  # No upfront payment
                    description=f"Installment setup for Invoice #{self.id}",
                    related_invoice=self,
                    created_at=self.created_at
                )

            # Save the updated fields for cash payment or installment setup
            super().save(update_fields=['total_paid', 'remaining_amount', 'is_fully_paid', 'due_dates'])


    def generate_installment_due_dates(self):
        """Generate due dates based on the number of installments."""
        due_dates = []
        today = datetime.now().date()
        for i in range(self.installments_count):
            due_date = today + timedelta(days=(30 * (i + 1)))
            due_dates.append(str(due_date))
        return due_dates

    @transaction.atomic
    def make_payment(self, amount, date=None):
        """Record a new payment and update the invoice status."""
        if self.is_fully_paid:
            raise ValueError("Invoice is already fully paid")

        if self.payments is None:
            self.payments = []

        # Update financial details
        self.total_paid += Decimal(amount)
        self.remaining_amount = self.total_cost - self.total_paid

        # Log the payment
        self.payments.append({
            'amount': str(amount),
            'date': date or str(datetime.now().date()),
        })

        # Mark invoice as fully paid if necessary
        if self.remaining_amount <= 0:
            self.is_fully_paid = True

        self.save()

        # Create Finance record for the payment
        Finance.objects.create(
            transaction_type='Expense',
            amount=Decimal(amount),
            description=f"Payment for Invoice #{self.id}",
            related_invoice=self,
            created_at=date or datetime.now().date()
        )

    def get_installment_amount(self):
        """Calculate the installment amount."""
        if self.payment_method == 'Installments' and self.installments_count:
            return self.total_cost / self.installments_count
        return None
    


class Finance(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('Income', 'Income'),
        ('Expense', 'Expense'),
        ('Refund', 'Refund'),
    ]
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)  # المبلغ
    description = models.TextField(null=True, blank=True)  # وصف المعاملة
    related_payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='financial_transactions')
    related_invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='financial_transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.transaction_type}: {self.amount} on {self.created_at.date()}"

    class Meta:
        ordering = ['-created_at']
    
    @property
    def total_income(cls):
        return cls.objects.filter(transaction_type='Income').aggregate(total=Sum('amount'))['total'] or 0

    @property
    def total_expense(cls):
        return cls.objects.filter(transaction_type='Expense').aggregate(total=Sum('amount'))['total'] or 0

    @property
    def total_refund(cls):
        return cls.objects.filter(transaction_type='Refund').aggregate(total=Sum('amount'))['total'] or 0

    @property
    def net_profit(cls):
        return cls.total_income - cls.total_expense - cls.total_refund


class Medical_History(models.Model):
    patient = models.ForeignKey(patient, on_delete=models.CASCADE)
    medical_notes = models.CharField(max_length=1000)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.patient.name



class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(null=True, blank=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)  # حالة المستخدم (نشط/غير نشط)
    date = models.DateField(auto_now_add=True)  # تاريخ اليوم

    def __str__(self):
        return f"{self.user.username} - {self.date}"
    

class UsedItem(models.Model):
    inventory_item = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='used_items')
    quantity_used = models.IntegerField()  # الكمية المستخدمة
    date_used = models.DateTimeField(default=timezone.now)  # تاريخ الاستخدام
    notes = models.TextField(blank=True, null=True)  # ملاحظات إضافية (اختياري)

    def __str__(self):
        return f"{self.quantity_used} of {self.inventory_item.item_name} used on {self.date_used}"

    def save(self, *args, **kwargs):
        # تقليل الكمية من المخزون عند حفظ العنصر المستخدم
        self.inventory_item.reduce_quantity(self.quantity_used)
        super().save(*args, **kwargs)    