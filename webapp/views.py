from itertools import count
import json
import django.contrib.auth.forms
from django.shortcuts import render , redirect, get_object_or_404
from.forms import * 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate , login , logout 
from django.contrib.auth.decorators import login_required
from.models import*
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q 
from django.http import JsonResponse
from django.contrib import messages 
from django.db.models import Sum, F, Count
from django.core.serializers import serialize
from django.utils.dateparse import parse_date, parse_time
from decimal import Decimal
from django.db.models import Prefetch
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login


# Create your views here.
def index (request):
    return render(request, 'web/index.html')




def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to the login URL pattern after registration
    else:
        form = UserCreationForm()
    
    context = {'form': form}
    return render(request, 'web/register.html', context)

def my_Login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                # تحديث أو إنشاء سجل النشاط
                activity, created = UserActivity.objects.get_or_create(user=user, date=timezone.now().date())
                activity.login_time = timezone.now()
                activity.is_active = True
                activity.save()

                return redirect('dashboard')  # إعادة التوجيه إلى لوحة التحكم
    else:
        form = AuthenticationForm()
    
    context = {'form': form}
    return render(request, 'web/login.html', context)



@login_required(login_url='login')
def dashboard(request):
    total_patients = patient.objects.count()
    today = timezone.now().date()
    appointments_today = Reserve.objects.filter(date=today).count()
    recent_appointments = Reserve.objects.order_by('-date', '-time')[:5]
    context= {
        'total_patients': total_patients,
        'appointments_today': appointments_today,
        'recent_appointments': recent_appointments
    }
    return render(request, 'web/dashboard.html',context=context)



@login_required(login_url='login')
def patients (request):
    records=patient.objects.all()
    query = request.GET.get('q')  
    if query:
        
        records = patient.objects.filter(name__icontains=query) | patient.objects.filter(phone__icontains=query)
    else:
        
        records = patient.objects.all()
    return render(request, 'web/patients.html',context={'records':records})




def edit_patient(request, record_id):
    patient_record = get_object_or_404(patient, id=record_id)
    
    if request.method == 'POST':
        form = patient_form_edit(request.POST, instance=patient_record)
        if form.is_valid():
            form.save()
            return redirect('view_patient', record_id=patient_record.id)  
    else:
        form = patient_form_edit(instance=patient_record)
    
    context = {
        'form': form,
        'record': patient_record
    }
    
    return render(request, 'web/edit_patient.html', context=context)



def delete_patient(request, patient_id):
    
    Patient = get_object_or_404(patient, id=patient_id)
    
    if request.method == 'POST':
        
        Patient.delete()
        return redirect(reverse('patients'))  
    

    return render(request, 'confirm_delete.html', {'patient': patient})


@login_required(login_url='login')

def view_patient(request, record_id):
    # الحصول على كائن المريض
    patient_record = get_object_or_404(patient, id=record_id)

    # استرجاع السجلات المرتبطة
    medical_history = Medical_History.objects.filter(patient=patient_record)
    reservations = Reserve.objects.filter(patient_name=patient_record.name)
    payments = Payment.objects.filter(patient=patient_record.name)

    # إنشاء الفورمات
    medical_history_form = MedicalHistoryForm(request.POST or None)
    reserve_form = ReserveForm(request.POST or None)
    payment_form = PaymentForm(request.POST or None)

    # معالجة النموذج المرسل
    if request.method == 'POST':
        # إضافة سجل طبي جديد
        if 'add_medical_history' in request.POST and medical_history_form.is_valid():
            medical_history_entry = medical_history_form.save(commit=False)
            medical_history_entry.patient = patient_record
            medical_history_entry.save()
            messages.success(request, "Medical history added successfully.")
            return redirect('view_patient', record_id=record_id)

        # إضافة حجز جديد
        # إضافة حجز جديد
        if 'add_reservation' in request.POST and reserve_form.is_valid():
            # حفظ الحجز
            reserve = reserve_form.save(commit=False)
            reserve.patient_name = patient_record.name
            reserve.phone = patient_record.phone
            reserve.save()
            
            # حفظ الخدمات المرتبطة باستخدام النموذج الوسيط
            selected_services = reserve_form.cleaned_data.get('selected_services', [])
            for service in selected_services:
                ReservationService.objects.create(reserve=reserve, service=service)
            
            # رسالة تأكيد
            messages.success(request, "Reservation added successfully.")
            return redirect('view_patient', record_id=record_id)


        # إضافة فاتورة جديدة
        if 'add_payment' in request.POST and payment_form.is_valid():
            payment = payment_form.save(commit=False)
            payment.patient = patient_record.name
            payment.save()
            messages.success(request, "Payment added successfully.")
            return redirect('view_patient', record_id=record_id)

    # تمرير البيانات إلى القالب
    context = {
        'record': patient_record,
        'medical_history': medical_history,
        'reservations': reservations,
        'payments': payments,
        'medical_history_form': medical_history_form,
        'reserve_form': reserve_form,
        'payment_form': payment_form,
    }

    return render(request, 'web/view_patient.html', context)



@login_required(login_url='login')
def add_patient (request):
    form= patient_form()
    if request.method=='POST':
        form=patient_form(request.POST)
        if form.is_valid():
            form.save()
            return redirect('patients')
    else:
        form = patient_form()   
        
    context= {
        'form':form
                }     
    return render(request, 'web/add_patient.html', context=context)




def Appointments(request):
    query = request.GET.get('q')  # البحث بناءً على الاسم أو الهاتف

    # جلب السجلات بناءً على البحث أو عرض كل السجلات
    if query:
        records = Reserve.objects.filter(
            Q(patient_name__icontains=query) |  # البحث في اسم المريض
            Q(phone__icontains=query)          # البحث في رقم الهاتف
        ).prefetch_related(
            Prefetch('reservation_services', queryset=ReservationService.objects.select_related('service'))
        )
    else:
        records = Reserve.objects.prefetch_related(
            Prefetch('reservation_services', queryset=ReservationService.objects.select_related('service'))
        ).all()

    # معالجة الوقت وعرضه بتنسيق 12 ساعة
    for record in records:
        if isinstance(record.time, str):  # إذا كان الوقت مخزن كـ CharField
            try:
                # إزالة أي أجزاء إضافية غير متوقعة
                record.time = record.time.split(':')[0] + ':' + record.time.split(':')[1]
                time_obj = datetime.strptime(record.time, '%H:%M').time()
                record.formatted_time = time_obj.strftime('%I:%M %p')  # تنسيق 12 ساعة
            except ValueError:
                record.formatted_time = record.time  # في حال لم يكن التنسيق صحيحًا
        else:
            record.formatted_time = record.time.strftime('%I:%M %p')  # إذا كان وقتًا فعليًا

        # إضافة الخدمات المرتبطة إلى كل حجز
        record.services_list = [reserve_service.service.name for reserve_service in record.reservation_services.all()]

    # تمرير البيانات إلى القالب
    return render(request, 'web/Appointments.html', context={'records': records})


def view_reservation(request, pk):
    """عرض تفاصيل الحجز"""
    reservation = get_object_or_404(Reserve, pk=pk)

    # معالجة الوقت وعرضه بتنسيق 12 ساعة
    if isinstance(reservation.time, str):  # إذا كان الوقت مخزن كـ CharField
        try:
            # إزالة أي أجزاء إضافية غير متوقعة
            reservation.time = reservation.time.split(':')[0] + ':' + reservation.time.split(':')[1]
            time_obj = datetime.strptime(reservation.time, '%H:%M').time()
            reservation.formatted_time = time_obj.strftime('%I:%M %p')  # تنسيق 12 ساعة
        except ValueError:
            reservation.formatted_time = reservation.time  # في حال لم يكن التنسيق صحيحًا
    else:
        reservation.formatted_time = reservation.time.strftime('%I:%M %p')  # إذا كان وقتًا فعليًا

    return render(request, 'web/view_reservation.html', {'reservation': reservation})


def edit_reservation(request, pk):
    """تعديل الحجز مع تحديث الخدمات المترابطة"""
    reservation = get_object_or_404(Reserve, pk=pk)  # جلب الحجز باستخدام المفتاح الأساسي

    # جلب الخدمات المرتبطة حاليًا بالحجز
    existing_services = reservation.reservation_services.all().values_list('service_id', flat=True)

    if request.method == 'POST':
        form = ReserveForm(request.POST, instance=reservation)  # تمرير الحجز الحالي إلى النموذج
        if form.is_valid():
            updated_reservation = form.save()  # حفظ بيانات الحجز الرئيسية

            # تحديث الخدمات المرتبطة
            selected_services = form.cleaned_data['selected_services']  # الخدمات المختارة في النموذج
            current_service_ids = set(existing_services)  # الخدمات الحالية
            new_service_ids = set(service.id for service in selected_services)  # الخدمات الجديدة

            # إضافة خدمات جديدة
            for service_id in new_service_ids - current_service_ids:
                ReservationService.objects.create(reserve=updated_reservation, service_id=service_id)

            # حذف الخدمات غير المختارة
            for service_id in current_service_ids - new_service_ids:
                ReservationService.objects.filter(reserve=updated_reservation, service_id=service_id).delete()

            return redirect('view_reservation', pk=reservation.pk)  # إعادة التوجيه إلى صفحة عرض الحجز
    else:
        # تمرير الخدمات الحالية إلى النموذج
        form = ReserveForm(instance=reservation)
        form.fields['selected_services'].initial = existing_services

    return render(request, 'web/edit_reservation.html', {'form': form, 'reservation': reservation})

@login_required(login_url='login')
def Schedule_Appointment(request):
    if request.method == 'POST':
        form = ReserveForm(request.POST)
        if form.is_valid():
            # حفظ الحجز
            reserve = form.save()

            # حفظ الخدمات المرتبطة باستخدام النموذج الوسيط
            selected_services = form.cleaned_data['selected_services']
            for service in selected_services:
                ReservationService.objects.create(reserve=reserve, service=service)

            return redirect('Appointments')
    else:
        form = ReserveForm()

    context = {'form': form}
    return render(request, 'web/Schedule_Appointment.html', context)







def update_appointment_status(request, appointment_id, status):
    record = get_object_or_404(Reserve, id=appointment_id)
    record.status = status
    record.save()

    # إذا كانت الحالة 'completed' وكان المريض غير موجود في قاعدة بيانات المرضى
    if status == 'completed' and not patient.objects.filter(name=record.patient_name).exists():
        patient.objects.create(
            name=record.patient_name,
            phone=record.phone,
            address='Default Address',  # يمكنك تحديث هذا إذا كان لديك عنوان محدد
            create_at=record.create_at,
            date_of_birth=None,  # قم بتحديثه إذا كان لديك تاريخ ميلاد للمريض
            last_visit=None  # قم بتحديثه إذا كان لديك تاريخ الزيارة الأخير
        )
    
    return redirect('Appointments')









def my_Logout(request):
    if request.user.is_authenticated:
        # تحديث سجل النشاط
        activity = UserActivity.objects.filter(user=request.user, date=timezone.now().date()).first()
        if activity:
            activity.logout_time = timezone.now()
            activity.is_active = False
            activity.save()

    logout(request)
    return redirect('login')


# Create Medical History
def add_medical_history(request):
    if request.method == 'POST':
        form = MedicalHistoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('patients')  # Redirect to medical history list after saving
    else:
        form = MedicalHistoryForm()
    return render(request, 'web/add_medical_history.html', {'form': form})



# Create Company
def create_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('companies')  # Redirect to company list after saving
    else:
        form = CompanyForm()
    return render(request, 'web/add_company.html', {'form': form})



# Create Service
def create_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('service_list')  # Redirect to service list after saving
    else:
        form = ServiceForm()
    return render(request, 'create_service.html', {'form': form})

 #Create Payment
def create_payment(request):
    if request.method == 'POST':
        payment_form = PaymentForm(request.POST)
        payment_service_formset = PaymentServiceFormSet(request.POST, prefix='services')
        payment_inventory_formset = PaymentInventoryFormSet(request.POST, prefix='inventory')

        if payment_form.is_valid() and payment_service_formset.is_valid() and payment_inventory_formset.is_valid():
            payment = payment_form.save()

            # حفظ الخدمات
            for service_form in payment_service_formset:
                service_instance = service_form.save(commit=False)
                service_instance.payment = payment
                
                # استخدام cleaned_data للحصول على السعر
                service_instance.price_at_time_of_payment = service_form.cleaned_data['price_at_time_of_payment']  # حفظ السعر
                service_instance.save()

            # حفظ المنتجات
            for inventory_form in payment_inventory_formset:
                inventory_instance = inventory_form.save(commit=False)
                inventory_instance.payment = payment
                
                # استخدام cleaned_data للحصول على السعر
                inventory_instance.price_at_time_of_payment = inventory_form.cleaned_data['price_at_time_of_payment']  # حفظ السعر
                inventory_instance.save()

            # حساب الإجمالي
            # ...

            return render(request, 'web/payment_summary.html', {
                'payment': payment,
                # ...
            })
    else:
        payment_form = PaymentForm()
        payment_service_formset = PaymentServiceFormSet(prefix='services')
        payment_inventory_formset = PaymentInventoryFormSet(prefix='inventory')

    return render(request, 'web/create_bill.html', {
        'payment_form': payment_form,
        'payment_service_formset': payment_service_formset,
        'payment_inventory_formset': payment_inventory_formset,
    })
    
def payment_detail(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    services = payment.paymentservice_set.all()
    inventories = payment.paymentinventory_set.all()
    
    return render(request, 'web/view_bill.html', {
        'payment': payment,
        'services': services,
        'inventories': inventories,
    })    
    
def edit_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        payment_form = PaymentForm(request.POST, instance=payment)
        payment_service_formset = PaymentServiceFormSet(request.POST, instance=payment, prefix='services')
        payment_inventory_formset = PaymentInventoryFormSet(request.POST, instance=payment, prefix='inventory')

        if payment_form.is_valid() and payment_service_formset.is_valid() and payment_inventory_formset.is_valid():
            payment = payment_form.save()

            # حفظ الخدمات
            for service_form in payment_service_formset:
                service_instance = service_form.save(commit=False)
                service_instance.payment = payment
                service_instance.price_at_time_of_payment = service_form.cleaned_data['price_at_time_of_payment']
                service_instance.save()

            # حفظ المنتجات
            for inventory_form in payment_inventory_formset:
                inventory_instance = inventory_form.save(commit=False)
                inventory_instance.payment = payment
                inventory_instance.price_at_time_of_payment = inventory_form.cleaned_data['price_at_time_of_payment']
                inventory_instance.save()

            return redirect('payment_detail', payment_id=payment.id)
    else:
        payment_form = PaymentForm(instance=payment)
        payment_service_formset = PaymentServiceFormSet(instance=payment, prefix='services')
        payment_inventory_formset = PaymentInventoryFormSet(instance=payment, prefix='inventory')

    return render(request, 'web/edit_bill.html', {
        'payment_form': payment_form,
        'payment_service_formset': payment_service_formset,
        'payment_inventory_formset': payment_inventory_formset,
    })

# Create Invoice
def create_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        payment_method = request.POST.get('payment_method')  # الحصول على طريقة الدفع
        
        if payment_method == 'Deferred':  # إذا كانت طريقة الدفع مؤجلة
            due_dates = request.POST.get('due_dates')
            payments = request.POST.get('payments')
            
            # التحقق من أن المستخدم أدخل مواعيد المدفوعات والمبالغ
            if not due_dates or not payments:
                messages.error(request, "Please provide due dates and payment amounts for deferred payment.")
                return render(request, 'create_invoice.html', {'form': form})
        
        if form.is_valid():
            invoice = form.save(commit=False)
            
            if payment_method == 'Deferred':  # إذا كانت الفاتورة دفع آجل
                due_dates_list = json.loads(due_dates)  # تحويل القيم إلى قائمة
                payments_list = json.loads(payments)
                
                # هنا يمكنك إضافة منطق لحفظ مواعيد المدفوعات والأقساط
                # مثال: يمكنك إنشاء موديل آخر لحفظ كل دفعة مع تاريخها
                
            invoice.save()
            messages.success(request, "Invoice has been created successfully!")
            return redirect('invoice_list')
    else:
        form = InvoiceForm()
    
    return render(request, 'create_invoice.html', {'form': form})



# List Companies
def company_list(request):
    companies = Companies.objects.all()
    return render(request, 'web/Company_list.html', {'companies': companies})

# List Inventory
def inventory_view(request, item_id=None):
    # جلب قيمة البحث إذا كانت موجودة
    query = request.GET.get('q')

    # جلب قائمة العناصر الموجودة في المخزون مع إمكانية البحث
    if query:
        # تصفية النتائج بناءً على البحث في اسم العنصر أو اسم الشركة المرتبطة
        inventory = Inventory.objects.filter(
            Q(item_name__icontains=query) | Q(company_source__company_name__icontains=query)
        )
    else:
        inventory = Inventory.objects.all()

    # التعديل: إذا كان هناك item_id موجود، جلب العنصر المطلوب تعديله
    if item_id:
        inventory_item = get_object_or_404(Inventory, id=item_id)
        if request.method == 'POST':
            form = InventoryForm(request.POST, instance=inventory_item)
            if form.is_valid():
                form.save()
                return redirect('inventory')  # إعادة توجيه بعد التعديل
        else:
            form = InventoryForm(instance=inventory_item)
    else:
        # التعامل مع إضافة عنصر جديد
        if request.method == 'POST':
            form = InventoryForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('inventory')  # إعادة توجيه بعد الحفظ
        else:
            form = InventoryForm()

    # تمرير قائمة المخزون، النموذج، وقيمة البحث إلى القالب
    return render(request, 'web/inventory.html', {'inventory': inventory, 'form': form, 'query': query})

#edit inventory
def update_inventory_item(request, item_id):
    # جلب المنتج المحدد بناءً على item_id
    inventory_item = get_object_or_404(Inventory, id=item_id)

    # إذا كانت الطلبية POST، نريد تعديل المنتج
    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=inventory_item)
        if form.is_valid():
            form.save()  # حفظ التعديلات
            return redirect('inventory')  # إعادة توجيه إلى قائمة المخزون بعد التعديل
    else:
        # في حالة GET، نريد عرض البيانات الحالية في النموذج
        form = InventoryForm(instance=inventory_item)

    return render(request, 'web/edit_inventory.html', {'form': form, 'inventory_item': inventory_item})

# delete item inventory
def delete_inventory_item(request, item_id):
    # جلب المنتج بناءً على item_id
    inventory_item = get_object_or_404(Inventory, id=item_id)

    # إذا كان الطلب POST، نقوم بحذف المنتج
    if request.method == 'POST':
        inventory_item.delete()  # حذف العنصر
        return redirect('inventory')  # إعادة التوجيه إلى قائمة المخزون

    # إذا كان الطلب GET، نعرض صفحة تأكيد الحذف
    return render(request, 'web/delete_inventory_confirm.html', {'inventory_item': inventory_item})
# List Services

# List Payments
def payment_list(request):
    query = request.GET.get('q')  # قيمة البحث من البارامتر
    branch_filter = request.GET.get('branch')  # الحصول على الفرع المطلوب من البارامتر
    
    # بدء البحث الأساسي
    payments = Payment.objects.all()
    
    # تصفية النتائج بناءً على اسم المريض إذا كان هناك بحث
    if query:
        payments = payments.filter(Q(patient__icontains=query))
    
    # تصفية النتائج حسب الفرع إذا تم تحديده
    if branch_filter and branch_filter in dict(Payment.BRANCH_CHOICES).keys():
        payments = payments.filter(Branch=branch_filter)

    return render(request, 'web/billing.html', {'payments': payments, 'selected_branch': branch_filter})
def update_payment_status(request, payment_id, new_status):
    # جلب الفاتورة المطلوبة بناءً على الـ ID الخاص بها
    payment = get_object_or_404(Payment, id=payment_id)

    # التحقق من أن الحالة الجديدة هي واحدة من القيم المسموحة
    if new_status in ['Paid', 'Cancelled']:
        # تحديث حالة الفاتورة بالحالة الجديدة
        payment.status = new_status
        payment.save()  # حفظ التعديلات
        return redirect('payment_list')  # إعادة التوجيه إلى صفحة عرض الفواتير
    
    # إذا كانت الحالة غير مسموحة، يمكن عرض رسالة خطأ أو إعادة التوجيه
    return redirect('payment_list')

def delete_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    payment.delete()
    messages.success(request, f"Payment {payment_id} has been deleted successfully.")
    return redirect('payment_list')  # إعادة التوجيه إلى قائمة الفواتير

def edit_payment(request, payment_id):
    # جلب الفاتورة المطلوبة
    payment = get_object_or_404(Payment, id=payment_id)

    if request.method == 'POST':
        # تعبئة البيانات المدخلة في الفورم
        form = PaymentForm(request.POST, instance=payment)
        
        if form.is_valid():
            # حفظ التعديلات
            form.save()
            return redirect('payments')  # إعادة التوجيه إلى صفحة الفواتير بعد التعديل
    else:
        # عرض الفورم مع البيانات الحالية للفاتورة
        form = PaymentForm(instance=payment)
    
    return render(request, 'web/edit_bill.html', {'form': form, 'payment': payment})


# List Payment Services
#def payment_service_list(request):
    payment_services = PaymentService.objects.all()
    return render(request, 'payment_service_list.html', {'payment_services': payment_services})

# List Payment Inventory
#def payment_inventory_list(request):
    payment_inventories = PaymentInventory.objects.all()
    return render(request, 'payment_inventory_list.html', {'payment_inventories': payment_inventories})

# List Invoices
def invoice_list(request):
    invoices = Invoice.objects.all()
    return render(request, 'web/invoice_list.html', {'invoices': invoices})


# Create Invoice
def create_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('invoice_list')  # Redirect to invoice list after saving
    else:
        form = InvoiceForm()
    return render(request, 'web/create_invoice.html', {'form': form})


def invoice_detail_view(request, id):
    invoice = get_object_or_404(Invoice, id=id)
    total_due = invoice.total_cost - invoice.total_paid
    return render(request, 'web/invoice_detail.html', {'invoice': invoice, 'total_due': total_due})


def add_payment_view(request, id):
    invoice = get_object_or_404(Invoice, id=id)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            try:
                amount = Decimal(amount)  # تحويل المبلغ إلى decimal.Decimal
                invoice.make_payment(amount)
                messages.success(request, "Payment has been added successfully!")
            except ValueError:
                messages.error(request, "Invalid amount.")
        else:
            messages.error(request, "Please provide a valid amount.")
        return redirect('invoice_detail', id=id)
    return render(request, 'invoice_detail.html', {'invoice': invoice})


def delete_invoice_view(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice.delete()
        messages.success(request, "Invoice has been deleted successfully!")
        return redirect('invoice_list')
    return render(request, 'confirm_delete.html', {'invoice': invoice})



# List Medical History
def medical_history_list(request):
    medical_histories = Medical_History.objects.all()
    return render(request, 'medical_history_list.html', {'medical_histories': medical_histories})


def get_service_price(request):
    service_id = request.GET.get('service_id')
    if service_id:
        service = Service.objects.get(pk=service_id)
        return JsonResponse({'price': service.price})
    return JsonResponse({'price': 0})

def get_inventory_price(request):
    inventory_id = request.GET.get('inventory_id')
    if inventory_id:
        inventory = Inventory.objects.get(pk=inventory_id)
        return JsonResponse({'price': inventory.item_price})
    return JsonResponse({'price': 0})




#HCM SYSTEM
def user_activity_view(request):
    activities = UserActivity.objects.all()  # جلب جميع سجلات النشاط
    return render(request, 'web/user_activity.html', {'activities': activities})




def edit_company(request, company_id):
    company = get_object_or_404(Companies, id=company_id)
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect('company_detail', company_id=company.id)
    else:
        form = CompanyForm(instance=company)
    return render(request, 'web/edit_company.html', {'form': form})

def company_detail(request, company_id):
    company = get_object_or_404(Companies, id=company_id)
    items = Inventory.objects.filter(company_source=company)
    invoice = Invoice.objects.filter(company=company)
    return render(request, 'web/company_detail.html', {'company': company,'items':items,'invoice':invoice})


def delete_company(request, company_id):
    Patient = get_object_or_404(Companies, id=company_id)
    
    if request.method == 'POST':
        
        Patient.delete()
        return redirect(reverse('companies'))  
    

    return render(request, 'confirm_delete.html', {'Companies': Companies})



def statistics_view(request):
    # جلب البيانات من الـ GET لتحديد الفترات الزمنية
    time_frame = request.GET.get('time_frame', 'all')  # الخيارات: اليوم، الأسبوع، الشهر، السنة
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    
    # معالجة الفترات الزمنية
    now = datetime.now()
    if time_frame == 'day':
        start_date = now - timedelta(days=1)
    elif time_frame == 'week':
        start_date = now - timedelta(weeks=1)
    elif time_frame == 'month':
        start_date = now - timedelta(days=30)
    elif time_frame == 'year':
        start_date = now - timedelta(days=365)
    
    # فلترة البيانات بناءً على الفترات الزمنية
    if start_date and end_date:
        reserves_filter = Reserve.objects.filter(date__range=[start_date, end_date])
        invoices_filter = Invoice.objects.filter(created_at__range=[start_date, end_date])
    else:
        reserves_filter = Reserve.objects.all()
        invoices_filter = Invoice.objects.all()

    # إحصائيات الشركات
    total_companies = Companies.objects.count()

    # إحصائيات المخزون
    total_inventory_items = Inventory.objects.count()
    total_quantity_in_stock = Inventory.objects.aggregate(
        total_quantity=Sum('item_quantity')
    )['total_quantity'] or 0
    total_stock_value = Inventory.objects.aggregate(
        stock_value=Sum(F('item_quantity') * F('item_cost'))
    )['stock_value'] or 0

    # إحصائيات الفواتير
    total_invoices = invoices_filter.count()
    total_quantity_purchased = invoices_filter.aggregate(
        total_purchased=Sum('quantity_purchased')
    )['total_purchased'] or 0
    total_quantity_used = invoices_filter.aggregate(
        total_used=Sum('quantity_used')
    )['total_used'] or 0

    # إحصائيات المدفوعات
    total_payments = Payment.objects.count()
    total_paid_services = PaymentService.objects.aggregate(
        total_paid_services=Sum(F('quantity') * F('price_at_time_of_payment'))
    )['total_paid_services'] or 0
    total_paid_inventory = PaymentInventory.objects.aggregate(
        total_paid_inventory=Sum(F('quantity') * F('price_at_time_of_payment'))
    )['total_paid_inventory'] or 0
    total_paid = total_paid_services + total_paid_inventory

    # إحصائيات المرضى
    total_patients = patient.objects.count()
    total_visits = patient.objects.aggregate(
        total_visits=Count('last_visit')
    )['total_visits'] or 0

    # إحصائيات الحجوزات
    total_reserves = reserves_filter.count()
    completed_reserves = reserves_filter.filter(status='completed').count()
    pending_reserves = reserves_filter.filter(status='pending').count()
    cancelled_reserves = reserves_filter.filter(status='cancelled').count()

    # إحصائيات الحجوزات حسب الفروع
    branches = ['Naser_city', '5th_sattelment', 'EL_Mohandsen']
    completed_reserves_by_branch = {
        branch: reserves_filter.filter(Branch=branch, status='completed').count() for branch in branches
    }
    pending_reserves_by_branch = {
        branch: reserves_filter.filter(Branch=branch, status='pending').count() for branch in branches
    }
    cancelled_reserves_by_branch = {
        branch: reserves_filter.filter(Branch=branch, status='cancelled').count() for branch in branches
    }

    # تفاصيل المخزون
    inventory_details = Inventory.objects.all()

    # إعداد البيانات للإحصائيات
    context = {
        'total_companies': total_companies,
        'total_inventory_items': total_inventory_items,
        'total_quantity_in_stock': total_quantity_in_stock,
        'total_stock_value': total_stock_value,
        'total_invoices': total_invoices,
        'total_quantity_purchased': total_quantity_purchased,
        'total_quantity_used': total_quantity_used,
        'total_payments': total_payments,
        'total_paid': total_paid,
        'total_patients': total_patients,
        'total_visits': total_visits,
        'total_reserves': total_reserves,
        'completed_reserves': completed_reserves,
        'pending_reserves': pending_reserves,
        'cancelled_reserves': cancelled_reserves,
        'completed_reserves_by_branch': completed_reserves_by_branch,
        'pending_reserves_by_branch': pending_reserves_by_branch,
        'cancelled_reserves_by_branch': cancelled_reserves_by_branch,
        'inventory_details': inventory_details,
    }

    return render(request, 'web/statistics.html', context)



def calendar_appointments(request):
    # جلب جميع المواعيد من الموديل
    appointments = Reserve.objects.all().select_related('name')  # لتضمين بيانات صاحب الموعد

    # تحويل البيانات لتنسيق JSON المطلوب من FullCalendar
    events = []
    for appointment in appointments:
        events.append({
            'title': f"{appointment.name.name} - {appointment.service}",
            'start': f"{appointment.date}T{appointment.time}",
            'status': appointment.status,
            'branch': appointment.Branch,
            'phone': appointment.phone,
        })

    return JsonResponse(events, safe=False)



def service_list(request):
    query = request.GET.get('q')  # الحصول على مصطلح البحث من الطلب (GET)
    
    if query:
        # تصفية الخدمات بناءً على مصطلح البحث
        services = Service.objects.filter(name__icontains=query)  # البحث يكون غير حساس لحالة الأحرف
    else:
        services = Service.objects.all()

    return render(request, 'web/service_list.html', {'services': services, 'query': query})
# إضافة خدمة جديدة
def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Service has been added successfully!")
            return redirect('service_list')
    else:
        form = ServiceForm()
    return render(request, 'web/add_service.html', {'form': form})

# تعديل خدمة موجودة
def service_update(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Service has been updated successfully!")
            return redirect('service_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'web/add_service.html', {'form': form})

# حذف خدمة
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, "Service has been deleted successfully!")
        return redirect('service_list')
    return render(request, 'web/service_list.html', {'service': service})



def branch(request):
    return render(request, 'web/Branches.html')

def ElMohandseen_branch(request):
    # جلب الحجوزات الخاصة بفرع المهندسين
    reservations = Reserve.objects.filter(Branch='EL_Mohandsen')
    
    # جلب الفواتير الخاصة بفرع المهندسين
    invoices = Payment.objects.filter(Branch='EL_Mohandsen')
    
  


    # حساب الكميات المستهلكة من المخزون لفرع المهندسين
    inventory_usage = PaymentInventory.objects.filter(payment__Branch='EL_Mohandsen').values(
        'inventory__item_name'
    ).annotate(total_quantity_used=Sum('quantity'))

    # حساب الكميات المستهلكة من الخدمات لفرع المهندسين
    service_usage = PaymentService.objects.filter(payment__Branch='EL_Mohandsen').values(
        'service__name'
    ).annotate(total_quantity_used=Sum('quantity'))

    context = {
        'reservations': reservations,
        'invoices': invoices,
        'inventory_usage': inventory_usage,
        'service_usage': service_usage,
    }
    
    return render(request, 'web/ElMohandseen_branch.html', context)
    


def fifeth_sattelmant_branch(request):
    
    reservations = Reserve.objects.filter(Branch='5th_sattelment')
    

    invoices = Payment.objects.filter(Branch='5th_sattelment')
    

    inventory_usage = PaymentInventory.objects.filter(payment__Branch='5th_sattelment').values(
        'inventory__item_name'
    ).annotate(total_quantity_used=Sum('quantity'))

    
    service_usage = PaymentService.objects.filter(payment__Branch='5th_sattelment').values(
        'service__name'
    ).annotate(total_quantity_used=Sum('quantity'))

    context = {
        'reservations': reservations,
        'invoices': invoices,
        'inventory_usage': inventory_usage,
        'service_usage': service_usage,
    }
    return render(request, 'web/fifeth_sattelmant_branch.html',context)



def naser_city_branch(request):
    
    reservations = Reserve.objects.filter(Branch='Naser_city')
    

    invoices = Payment.objects.filter(Branch='Naser_city')
    

    inventory_usage = PaymentInventory.objects.filter(payment__Branch='Naser_city').values(
        'inventory__item_name'
    ).annotate(total_quantity_used=Sum('quantity'))

    
    service_usage = PaymentService.objects.filter(payment__Branch='Naser_city').values(
        'service__name'
    ).annotate(total_quantity_used=Sum('quantity'))

    context = {
        'reservations': reservations,
        'invoices': invoices,
        'inventory_usage': inventory_usage,
        'service_usage': service_usage,
    }

    return render(request, 'web/naser_city_branch.html', context)




def tasks(request):
    today = date.today()
    today_reservations = Reserve.objects.filter(date=today)
    future_reservations = Reserve.objects.filter(date__gt=today)

    # معالجة الوقت وعرضه بتنسيق 12 ساعة لكل حجز في today_reservations
    for reservation in today_reservations:
        if isinstance(reservation.time, str):  # إذا كان الوقت مخزن كـ CharField
            try:
                # إزالة أي أجزاء إضافية غير متوقعة
                reservation.time = reservation.time.split(':')[0] + ':' + reservation.time.split(':')[1]
                time_obj = datetime.strptime(reservation.time, '%H:%M').time()
                reservation.formatted_time = time_obj.strftime('%I:%M %p')  # تنسيق 12 ساعة
            except ValueError:
                reservation.formatted_time = reservation.time  # في حال لم يكن التنسيق صحيحًا
        else:
            reservation.formatted_time = reservation.time.strftime('%I:%M %p')  # إذا كان وقتًا فعليًا

    # معالجة الوقت وعرضه بتنسيق 12 ساعة لكل حجز في future_reservations
    for reservation in future_reservations:
        if isinstance(reservation.time, str):  # إذا كان الوقت مخزن كـ CharField
            try:
                # إزالة أي أجزاء إضافية غير متوقعة
                reservation.time = reservation.time.split(':')[0] + ':' + reservation.time.split(':')[1]
                time_obj = datetime.strptime(reservation.time, '%H:%M').time()
                reservation.formatted_time = time_obj.strftime('%I:%M %p')  # تنسيق 12 ساعة
            except ValueError:
                reservation.formatted_time = reservation.time  # في حال لم يكن التنسيق صحيحًا
        else:
            reservation.formatted_time = reservation.time.strftime('%I:%M %p')  # إذا كان وقتًا فعليًا

    context = {
        'today_reservations': today_reservations,
        'future_reservations': future_reservations,
    }
    return render(request, 'web/tasks.html', context)


def offer(request):
    offer = offers.objects.all()  # استخدام اسم النموذج الصحيح
    if request.method == 'POST':
        form = OffersForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Offer added successfully!")
            return redirect('offers_list')  # استبدل 'offers_list' باسم الصفحة التي تريد إعادة التوجيه إليها
        else:
            messages.error(request, "There was an error. Please try again.")
    else:
        form = OffersForm()

    context = {
        'offers': offer,
        'form': form  # إضافة النموذج إلى السياق لعرضه في القالب
    }
    return render(request, 'web/offer.html', context)


        


# View to delete an offer
def offer_delete(request, pk):
    offer = get_object_or_404(offers, pk=pk)
    if request.method == 'POST':
        offer.delete()
        return redirect('offers_list')  # استبدل 'offers_list' باسم العرض المناسب
    return render(request, 'offers/offer_confirm_delete.html', {'offer': offer})