from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms.widgets import PasswordInput , TextInput
from .models import*
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from .models import Reserve



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
        fields =  fields = ['name','country', 'date_of_birth', 'phone','address', 'last_visit','how_did_you_know_us' ]
        
class patient_form_edit(forms.ModelForm):
    class Meta: 
        model = patient
        fields =  fields = ['name','country', 'date_of_birth', 'phone','address', 'last_visit','how_did_you_know_us' ]
    




class ReserveForm(forms.ModelForm):
    # قائمة بالخدمات كـ Checkbox أو SelectMultiple
    selected_services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.CheckboxSelectMultiple(),  # واجهة لعرض الخيارات كـ مربعات اختيار
        required=True,
        label="Select Services"
    )

    date = forms.DateField(
        widget=forms.TextInput(attrs={
            'class': 'form-control flatpickr-date',
            'placeholder': 'Select date'
        }),
        label='Date'
    )
    time = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control flatpickr-time',
            'placeholder': 'Select time (e.g., 10:30 AM)'
        }),
        label='Time'
    )

    class Meta:
        model = Reserve
        fields = ['patient_name', 'phone', 'type', 'date', 'time', 'Branch', 'notes','selected_services']  # بدون حقل الخدمات

    def clean_time(self):
        time_input = self.cleaned_data['time']
        try:
            parsed_time = datetime.strptime(time_input, '%I:%M %p')
            return parsed_time.time()
        except ValueError:
            raise forms.ValidationError("Invalid time format. Please use the format 'hh:mm AM/PM'.")
        


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Companies
        fields = ['company_name', 'company_address', 'company_phone']


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['item_name', 'item_quantity', 'item_cost', 'company_source']
        
        
        
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
    class Meta:
        model = Invoice
        fields = ['company', 'item', 'quantity_purchased', 'total_cost', 
                  'payment_method', 'installments_count']
        
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        installments_count = cleaned_data.get('installments_count')

        if payment_method == 'Installments' and (not installments_count or installments_count <= 0):
            self.add_error('installments_count', 'Installments count must be greater than 0 for installment payment.')
        return cleaned_data
        
        
class MedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = Medical_History
        fields = ['medical_notes']  # تأكد من عدم إدراج المريض هنا، سيتم تعيينه في الفيو                                 
        
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'price']        

class OffersForm(forms.ModelForm):
    class Meta:
        model=offers
        fields = ['offer_name','discount_percentage']        