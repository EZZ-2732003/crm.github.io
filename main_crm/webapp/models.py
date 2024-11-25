from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
# Create your models here.
# category model
class Category(models.Model):
    name = models.CharField(max_length=100)
    creat_at = models.DateTimeField (auto_now_add = True)
    
    def __str__(self): 
        return self.name
    
    #client model
class Record(models.Model):
    name = models.CharField(max_length=250)
    phone = models.IntegerField()
    address = models.CharField(max_length=255, default='Default Address')
    creat_at = models.DateTimeField (auto_now_add = True)
    def __str__(self): 
        return self.name
    
    
class patient(models.Model):
    name = models.CharField(max_length=250)
    phone = models.IntegerField()
    address = models.CharField(max_length=255, default='Default Address') 
    create_at = models.DateTimeField (auto_now_add = True)
    date_of_birth = models.DateField(null=True, blank=True)
    last_visit = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name  
    class Meta :
            ordering = ['-create_at']
        
        
        

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
    SERVICE_CHOICES = [
        ('Service', 'Service'),
        ('Consultation', 'Consultation'),
        ('Retouch', 'Retouch'),
    ]
    name = models.ForeignKey(patient, on_delete=models.CASCADE)
    
    phone = models.IntegerField()
    date = models.DateField()
    time = models.TimeField()
    service=models.CharField(max_length=50,choices=SERVICE_CHOICES,default='Service type' )
    create_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    Branch=models.CharField(max_length=50,choices=BRANCH_CHOICES,default='Branch' )
    def __str__(self):
        return str(self.name)
    class Meta :
            ordering = ['-create_at']


class Companies(models.Model):
    company_name = models.CharField(max_length=255)
    company_address = models.CharField(max_length=500)
    company_phone = models.CharField(max_length=20)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # إجمالي المدفوعات
    total_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)   # إجمالي المتبقي

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
    item_price = models.DecimalField(max_digits=10, decimal_places=2)  # سعر البيع
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



class Service(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # سعر الخدمة

    def __str__(self):
        return self.name



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

    patient = models.CharField(max_length=20)
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
        
    


from django.db import models
from datetime import datetime
import json
from decimal import Decimal



class Invoice(models.Model):
    PAYMENT_METHODS = [
        ('Immediate', 'Immediate Payment'),
        ('Deferred', 'Deferred Payment'),
    ]
    company = models.ForeignKey(Companies, on_delete=models.CASCADE, related_name='invoices')
    item = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='invoices')
    quantity_purchased = models.IntegerField()
    quantity_used = models.IntegerField(default=0)  # الكمية المستخدمة
    purchase_date = models.DateField(auto_now_add=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='Immediate')  # طريقة الدفع
    is_fully_paid = models.BooleanField(default=False)  # حالة الدفع الكلي
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # المبلغ المدفوع
    due_dates = models.JSONField(null=True, blank=True)  # مواعيد الدفعات
    payments = models.JSONField(null=True, blank=True)  # قيم الدفعات

    def __str__(self):
        return f"Invoice for {self.quantity_purchased} of {self.item.item_name} from {self.company.company_name}"

    def save(self, *args, **kwargs):
        """زيادة المخزون عند شراء منتجات جديدة"""
        if not self.pk:  # في حالة إنشاء الفاتورة للمرة الأولى
            self.item.increase_quantity(self.quantity_purchased)
        super().save(*args, **kwargs)

    def use_item(self, quantity_used):
        """تقليل الكمية المستخدمة من الفاتورة"""
        if self.quantity_used + quantity_used > self.quantity_purchased:
            raise ValueError("Cannot use more than purchased quantity")
        self.quantity_used += quantity_used
        self.item.reduce_quantity(quantity_used)
        self.save()

    def make_payment(self, amount, date=None):
        """تسجيل دفعة جديدة وتحديث حالة الفاتورة"""
        if self.is_fully_paid:
            raise ValueError("Invoice is already fully paid")
        if self.payments is None:
            self.payments = []
        if self.due_dates is None:
            self.due_dates = []
        self.total_paid += Decimal(amount)  # تأكد من استخدام decimal.Decimal
        self.payments.append({
            'amount': str(amount),  # تحويل المبلغ إلى نص لضمان التوافق
            'date': date or str(datetime.now().date())  # إضافة التاريخ تلقائيًا
        })
        # إذا تم سداد المبلغ بالكامل
        if self.total_paid >= self.total_cost:
            self.is_fully_paid = True
        self.save()

    def add_due_date(self, date):
        """إضافة موعد جديد للدفع في حالة الدفع الأجل"""
        if self.due_dates is None:
            self.due_dates = []
        self.due_dates.append(date)
        self.save()

        


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