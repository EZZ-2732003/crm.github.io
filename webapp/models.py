from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from datetime import date
from decimal import Decimal
# Create your models here.
# category model

    
    
class patient(models.Model):
    name = models.CharField(max_length=250)
    phone = models.CharField(max_length=20)
    country=models.CharField(max_length=40,default='none')
    address = models.CharField(max_length=255, default='Default Address') 
    create_at = models.DateTimeField (auto_now_add = True)
    date_of_birth = models.DateField(null=True, blank=True)
    last_visit = models.DateField(null=True, blank=True)
    how_did_you_know_us=models.CharField(max_length=100,default='none')

    def __str__(self):
        return self.name  
    class Meta :
            ordering = ['-create_at']
        
class Service(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # سعر الخدمة

    def __str__(self):
        return self.name        
        

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
    patient_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES, default='old')
    date = models.DateField()
    time = models.CharField(max_length=10)
    
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
                create_at=self.create_at,
                date_of_birth=None,  # قم بتعديل هذا إذا كان هناك تاريخ ميلاد متاح
                last_visit=None  # قم بتعديل هذا إذا كان هناك تاريخ زيارة متاح
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
        else:
            raise ValueError('Insufficient stock for this product')

    def increase_quantity(self, quantity):
        """زيادة الكمية عند الشراء"""
        self.item_quantity += quantity
        self.save()







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
        ( 'E_WALLET', 'E_WALLET'),

    ]
    BRANCH_CHOICES = [
        ('EL_Mohandsen', 'EL_Mohandsen'),
        ('5th_sattelment', '5th_sattelment'),
        ('Naser_city', 'Naser_city'),
    ]

    patient = models.CharField(max_length=100)
    Branch=models.CharField(max_length=50,choices=BRANCH_CHOICES,default='Branch' )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    method = models.CharField(max_length=100, choices=METHOD_CHOICES, default='CASH')

    def __str__(self):
        return f"Payment {self.id} for {self.patient}"

    def get_total_service(self):
        """حساب إجمالي الخدمات"""
        return sum([ps.price_at_time_of_payment * ps.quantity for ps in self.paymentservice_set.all()])

    def get_total_products(self):
        """حساب إجمالي المنتجات"""
        return sum([pi.price_at_time_of_payment * pi.quantity for pi in self.paymentinventory_set.all()])

    def get_total_amount(self):
        """إجمالي المبلغ يشمل الخدمات والمنتجات"""
        return self.get_total_service() + self.get_total_products()



class PaymentService(models.Model):
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time_of_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # السعر وقت الدفع
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.quantity} x {self.service.name} for {self.payment}"

    def save(self, *args, **kwargs):
        # حفظ السعر في وقت إنشاء الفاتورة إذا لم يكن محفوظاً مسبقاً
        if not self.price_at_time_of_payment:
            self.price_at_time_of_payment = self.service.price
        super().save(*args, **kwargs)


class PaymentInventory(models.Model):
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time_of_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)   # السعر وقت الفاتورة
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.inventory.item_name} for {self.payment}"

    def save(self, *args, **kwargs):
        # حفظ السعر في وقت إنشاء الفاتورة إذا لم يكن محفوظاً مسبقاً
        if not self.price_at_time_of_payment:
            self.price_at_time_of_payment = self.inventory.item_price
        super().save(*args, **kwargs)
    def save(self, *args, **kwargs):
        """عند حفظ الاستهلاك، يتم تحديث الكمية في المخزون"""
        super().save(*args, **kwargs)
        self.inventory.reduce_quantity(self.quantity)
        
    
class offers(models.Model):
    offer_name =models.CharField(max_length=250)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text=("Enter the discount percentage (e.g., 10 for 10%)"))
    def __str__(self):
        return self.offer_name






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

    def save(self, *args, **kwargs):
        if not self.pk:  # إنشاء فاتورة جديدة
            if self.payment_method == 'Cash':
                self.total_paid = self.total_cost
                self.remaining_amount = 0
                self.is_fully_paid = True
            elif self.payment_method == 'Installments' and self.installments_count:
                self.remaining_amount = self.total_cost
                self.due_dates = self.generate_installment_due_dates()
        super().save(*args, **kwargs)

    def generate_installment_due_dates(self):
        """حساب مواعيد الدفع بناءً على عدد الأقساط"""
        due_dates = []
        today = datetime.now().date()
        for i in range(self.installments_count):
            due_date = today + timedelta(days=(30 * (i + 1)))
            due_dates.append(str(due_date))
        return due_dates

    def make_payment(self, amount, date=None):
        """تسجيل دفعة جديدة وتحديث حالة الفاتورة"""
        if self.is_fully_paid:
            raise ValueError("Invoice is already fully paid")

        if self.payments is None:
            self.payments = []

        self.total_paid += Decimal(amount)
        self.remaining_amount = self.total_cost - self.total_paid

        self.payments.append({
            'amount': str(amount),
            'date': date or str(datetime.now().date()),
        })

        if self.remaining_amount <= 0:
            self.is_fully_paid = True

        self.save()

    def get_installment_amount(self):
        """حساب قيمة كل قسط"""
        if self.payment_method == 'Installments' and self.installments_count:
            return self.total_cost / self.installments_count
        return None

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