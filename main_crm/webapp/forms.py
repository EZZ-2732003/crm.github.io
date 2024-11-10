from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms.widgets import PasswordInput , TextInput
from .models import*
from django.forms import inlineformset_factory


# register user

class CreateUserForm(UserCreationForm):
    
    class meta :
        model = User
        fields = ['username','password1','password2']
        
        
        
class loginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())
    
class patient_form(forms.ModelForm):
    class Meta: 
        model = patient
        fields =  fields = ['name', 'date_of_birth', 'phone','address', 'last_visit' ]
        
class patient_form_edit(forms.ModelForm):
    class Meta: 
        model = patient
        fields =  fields = ['name', 'date_of_birth', 'phone','address', 'last_visit' ]
    




class ReserveForm(forms.ModelForm):
    patient_name = forms.CharField(max_length=100, label='Patient Name')

    class Meta:
        model = Reserve
        fields = ['patient_name', 'phone', 'date', 'time', 'service' ,'Branch']

    def save(self, commit=True):
        
        patient_name = self.cleaned_data.get('patient_name')
        
        phone = self.cleaned_data.get('phone')  

        
        patient_instance, created = patient.objects.get_or_create(
            name=patient_name, 
            defaults={'phone': phone}  
        )

      
        if not created and patient_instance.phone != phone:
            patient_instance.phone = phone
            patient_instance.save()

        
        reserve_instance = super(ReserveForm, self).save(commit=False)
        reserve_instance.name = patient_instance

        if commit:
            reserve_instance.save()

        return reserve_instance


        


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Companies
        fields = ['company_name', 'company_address', 'company_phone', 'total_paid', 'total_due']


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['item_name', 'item_quantity', 'item_price', 'item_cost', 'company_source']
        
        
        
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'price']
        
from django import forms
from django.forms import inlineformset_factory
from .models import Payment, PaymentService, PaymentInventory

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['patient','Branch', 'status', 'method']

# لإنشاء عدة إدخالات للخدمات
class PaymentServiceForm(forms.ModelForm):
    class Meta:
        model = PaymentService
        fields = ['service', 'quantity', 'price_at_time_of_payment']  # إضافة الحقل للسعر

class PaymentInventoryForm(forms.ModelForm):
    class Meta:
        model = PaymentInventory
        fields = ['inventory', 'quantity', 'price_at_time_of_payment']  # إضافة الحقل للسعر

# لإنشاء عدة إدخالات للخدمات
PaymentServiceFormSet = inlineformset_factory(
    Payment, PaymentService, 
    form=PaymentServiceForm,  # استخدام النموذج المعدل
    extra=1, can_delete=True
)

# لإنشاء عدة إدخالات للمنتجات
PaymentInventoryFormSet = inlineformset_factory(
    Payment, PaymentInventory, 
    form=PaymentInventoryForm,  # استخدام النموذج المعدل
    extra=1, can_delete=True
)



#class PaymentServiceForm(forms.ModelForm):
  #  class Meta:
       # model = PaymentService
      #  fields = [ 'service', 'quantity']
        
        
        
        
        
#class PaymentInventoryForm(forms.ModelForm):
   # class Meta:
    #    model = PaymentInventory
     #   fields = [ 'inventory', 'quantity']            
        
        
        
class InvoiceForm(forms.ModelForm):
    payment_method = forms.ChoiceField(choices=Invoice.PAYMENT_METHODS, label="Payment Method", required=False)
    due_dates = forms.CharField(widget=forms.HiddenInput(), required=False)  # ستملأها باستخدام JavaScript
    payments = forms.CharField(widget=forms.HiddenInput(), required=False)   # ستملأها باستخدام JavaScript

    class Meta:
        model = Invoice
        fields = ['company', 'item', 'quantity_purchased', 'total_cost', 'payment_method']

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get("payment_method")
        
        # إذا تم اختيار الدفع الآجل، تحقق مما إذا كانت البيانات المدخلة موجودة أم لا
        due_dates = cleaned_data.get("due_dates")
        payments = cleaned_data.get("payments")

        # إذا كانت الحقول فارغة، فقط تجاهلها ولا تعرض أي خطأ
        if payment_method == 'Deferred':
            if not due_dates or not payments:
                cleaned_data['due_dates'] = ''  # تأكد أن الحقل فارغ وليس به قيمة افتراضية
                cleaned_data['payments'] = ''
        
        return cleaned_data
        
        
class MedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = Medical_History
        fields = ['medical_notes']  # تأكد من عدم إدراج المريض هنا، سيتم تعيينه في الفيو                                 
        
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'price']        