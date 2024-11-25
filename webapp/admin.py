from django.contrib import admin
from.models import *

# Register your models here.
@admin.register(Category)
class  CategoryAdmin(admin.ModelAdmin):
    pass
@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    pass

@admin.register(patient)
class patientAdmin(admin.ModelAdmin):
    pass 

@admin.register(Reserve)
class ReserveAdmin(admin.ModelAdmin):
    pass


# تسجيل نموذج Companies
class CompaniesAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'company_address', 'company_phone', 'total_paid', 'total_due')
    search_fields = ('company_name', 'company_phone')
    list_filter = ('total_due',)

# تسجيل نموذج Inventory
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'item_quantity', 'item_price', 'item_cost', 'company_source', 'created_at')
    search_fields = ('item_name', 'company_source__company_name')
    list_filter = ('company_source', 'created_at')

# تسجيل نموذج Service
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)

# تسجيل نموذج PaymentService كـ Inline لتضمينه في Payment
class PaymentServiceInline(admin.TabularInline):
    model = PaymentService
    extra = 1

# تسجيل نموذج PaymentInventory كـ Inline لتضمينه في Payment
class PaymentInventoryInline(admin.TabularInline):
    model = PaymentInventory
    extra = 1

# تسجيل نموذج Payment مع Inline للخدمات والمنتجات
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'created_at', 'status', 'method', 'get_total_amount')
    search_fields = ('patient__name',)
    list_filter = ('status', 'method')
    inlines = [PaymentServiceInline, PaymentInventoryInline]  # تضمين النماذج الفرعية للخدمات والمنتجات

# تسجيل نموذج Invoice
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('company', 'item', 'quantity_purchased', 'quantity_used', 'purchase_date', 'total_cost')
    search_fields = ('company__company_name', 'item__item_name')
    list_filter = ('company', 'purchase_date')

# تسجيل نموذج Medical_History
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ('patient', 'medical_notes')
    search_fields = ('patient__name',)



# تسجيل النماذج في لوحة تحكم Django
admin.site.register(Companies, CompaniesAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Medical_History, MedicalHistoryAdmin)
admin.site.register(UserActivity)

