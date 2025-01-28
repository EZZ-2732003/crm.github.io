import json
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms.widgets import PasswordInput , TextInput
from .models import*
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from .models import Reserve
from django_select2.forms import Select2Widget



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
        fields =  fields = ['name','country', 'date_of_birth', 'phone','address', 'how_did_you_know_us' ]
        
class patient_form_edit(forms.ModelForm):
    class Meta: 
        model = patient
        fields =  fields = ['name','country', 'date_of_birth', 'phone','address', 'how_did_you_know_us' ]
    




class ReserveForm(forms.ModelForm):
    services = forms.CharField(
        widget=forms.HiddenInput(attrs={'data-role': 'services-input'}),
        required=True
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
        fields = ['patient_name', 'phone', 'type', 'date', 'time', 'Branch','services', 'notes']  # بدون حقل الخدمات

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
        fields = ['item_name', 'item_quantity', 'item_cost','item_price', 'company_source']
        
        
        
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'price']
        
from django import forms
from django.forms import inlineformset_factory
from .models import Payment, PaymentService, PaymentInventory

class PaymentForm(forms.ModelForm):
    """Form for creating and updating Payment instances."""
    date = forms.DateField(
        widget=forms.TextInput(attrs={
            'class': 'form-control flatpickr-date',
            'placeholder': 'Select date'
        }),
        label='Date'
    )

    class Meta:
        model = Payment
        fields = ['patient', 'Branch', 'method', 'type', 'date']
        widgets = {
            'patient': forms.TextInput(attrs={'class': 'form-control'}),
            'Branch': forms.Select(attrs={'class': 'form-control'}),
            'method': forms.Select(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'})
        }
        

# Form for adding or editing PaymentService entries
class PaymentServiceForm(forms.ModelForm):
    class Meta:
        model = PaymentService
        fields = ['service', 'quantity', ]
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'price_at_time_of_payment': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        help_texts = {
            'price_at_time_of_payment': 'Enter the price of the service at the time of payment.',
        }

# Form for adding or editing PaymentInventory entries
class PaymentInventoryForm(forms.ModelForm):
    class Meta:
        model = PaymentInventory
        fields = ['inventory', 'quantity', ]
        widgets = {
            'inventory': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'price_at_time_of_payment': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        help_texts = {
            'price_at_time_of_payment': 'Enter the price of the inventory item at the time of payment.',
        }

# Inline formset for PaymentService
PaymentServiceFormSet = inlineformset_factory(
    Payment, PaymentService,
    form=PaymentServiceForm,
    extra=1, can_delete=True
)

# Inline formset for PaymentInventory
PaymentInventoryFormSet = inlineformset_factory(
    Payment, PaymentInventory,
    form=PaymentInventoryForm,
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


class OfferForm(forms.ModelForm):
    class Meta:
        model = offers
        fields = ['name', 'valid_from', 'valid_to']

    valid_from = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'date-picker', 'placeholder': 'Select start date'}),
        required=True
    )
    valid_to = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'date-picker', 'placeholder': 'Select end date'}),
        required=True
    )

class OfferServiceForm(forms.ModelForm):
    class Meta:
        model = OfferService
        fields = ['service', 'discount_percentage', 'discount_amount']

    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        widget=Select2Widget(attrs={'placeholder': 'Search for a service...'}),
        required=True
    )
    discount_percentage = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter discount %'})
    )
    discount_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter discount amount'})
    )


class OfferInventoryForm(forms.ModelForm):
    class Meta:
        model = OfferInventory
        fields = ['inventory', 'discount_percentage', 'discount_amount']

    inventory = forms.ModelChoiceField(
        queryset=Inventory.objects.all(),
        widget=Select2Widget(attrs={'placeholder': 'Search for an inventory item...'}),
        required=True
    )
    discount_percentage = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter discount %'})
    )
    discount_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter discount amount'})
    )


# Inline formsets for adding multiple services or inventory items
OfferServiceFormSet = inlineformset_factory(
    offers, OfferService, form=OfferServiceForm, extra=1, can_delete=True
)

OfferInventoryFormSet = inlineformset_factory(
    offers, OfferInventory, form=OfferInventoryForm, extra=1, can_delete=True
)


class FinanceForm(forms.ModelForm):
    class Meta:
        model = Finance
        fields = ['transaction_type', 'amount', 'description', 'related_payment', 'related_invoice']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'related_payment': forms.Select(attrs={'class': 'form-control'}),
            'related_invoice': forms.Select(attrs={'class': 'form-control'}),
        }

class UsedItemForm(forms.ModelForm):
    class Meta:
        model = UsedItem
        fields = ['inventory_item', 'quantity_used', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the queryset for inventory_item if needed
        self.fields['inventory_item'].queryset = Inventory.objects.filter(item_quantity__gt=0)        