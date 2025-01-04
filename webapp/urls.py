from django.urls import path
from . import views

urlpatterns = [
    path('', views.index,name='home'),
    path('register/', views.register, name='register'),
    path('my-login', views.my_Login,name='login'),
    path ('dashboard', views.dashboard, name='dashboard'),
    path('logout/', views.my_Logout, name='logout'),
    path('patients', views.patients,name='patients'),
    path('Appointments',views.Appointments,name='Appointments'),
    path('reservation/<int:pk>/', views.view_reservation, name='view_reservation'),
    
   
    path('view_patient/<int:record_id>/', views.view_patient , name='view_patient') ,
    path('add_patient', views.add_patient, name='add_patient'),
    path('Schedule_Appointment', views.Schedule_Appointment,name='Schedule_Appointment'),
    path('Appointments/<int:appointment_id>/<str:status>/', views.update_appointment_status, name='update_appointment_status'),
    path('reservation/edit/<int:pk>/', views.edit_reservation, name='edit_reservation'),
    path('patients/delete/<int:patient_id>/', views.delete_patient, name='delete_patient'),
    path('patients/<int:record_id>/edit/', views.edit_patient, name='edit_patient'),
    # Company URLs
    path('company/create/', views.create_company, name='add_company'),
    path('companies/', views.company_list, name='companies'),
    path('company/<int:company_id>/edit/', views.edit_company, name='edit_company'),
    path('company/<int:company_id>/', views.company_detail, name='company_detail'),
    path('company/<int:company_id>/delete/', views.delete_company, name='delete_company'),

    # Inventory URLs
   # تعديل URL واحد لعرض المخزون وإضافة عنصر جديد
    path('inventory/', views.inventory_view, name='inventory'),
    path('inventory/update/<int:item_id>/', views.update_inventory_item, name='update_inventory'),
    path('inventory/delete/<int:item_id>/', views.delete_inventory_item, name='delete_inventory'),

    # Service URLs
    path('service/create/', views.create_service, name='create_service'),
    path('services/', views.service_list, name='service_list'),

    # Payment URLs
    path('payment/create/', views.create_payment, name='create_payment'),
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/<int:payment_id>/update_status/<str:new_status>/', views.update_payment_status, name='update_payment_status'),
    path('payments/<int:payment_id>/view/', views.payment_detail, name='view_payment'),
    path('payments/<int:payment_id>/edit/', views.edit_payment, name='edit_payment'),
    path('payments/<int:payment_id>/delete/', views.delete_payment, name='delete_payment'),

    # Payment Service URLs
  #  path('payment_service/create/', views.create_payment_service, name='create_payment_service'),
  #  path('payment_services/', views.payment_service_list, name='payment_service_list'),

    # Payment Inventory URLs
  #  path('payment_inventory/create/', views.create_payment_inventory, name='create_payment_inventory'),
   # path('payment_inventories/', views.payment_inventory_list, name='payment_inventory_list'),

    # Invoice URLs
    path('invoice/create/', views.create_invoice, name='create_invoice'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoice/<int:id>/', views.invoice_detail_view, name='invoice_detail'),
    path('invoice/<int:id>/add_payment/', views.add_payment_view, name='add_payment'),
    path('invoice/delete/<int:pk>/', views.delete_invoice_view, name='delete_invoice'),


    # Medical History URLs
    path('medical_history/create/', views.add_medical_history, name='add_medical_history'),
    path('medical_histories/', views.medical_history_list, name='medical_history_list'),
    
    
    path('get-service-price/', views.get_service_price, name='get_service_price'),
    path('get-inventory-price/', views.get_inventory_price, name='get_inventory_price'),
    
    #HCM 
    path('user-activity/', views.user_activity_view, name='user_activity'),
    
    path('statistics/', views.statistics_view, name='statistics'),
    
    path('services/', views.service_list, name='service_list'),
    path('services/create/', views.service_create, name='service_create'),
    path('services/update/<int:pk>/', views.service_update, name='service_update'),
    path('services/delete/<int:pk>/', views.service_delete, name='service_delete'),
    
    #Branches
    path('branches/',views.branch, name='branches'),
    path('ElMohandseen_branch',views.ElMohandseen_branch, name='ElMohandseen_branch'),
    path('fifeth_sattelmant_branch', views.fifeth_sattelmant_branch, name='fifeth_sattelmant_branch'),
    path('naser_city_branch', views.naser_city_branch, name='naser_city_branch'),
    path('tasks/',views.tasks,name='tasks'),
    path('offers/',views.offer,name='offers_list'),
    
   
    path('offers/delete/<int:pk>/', views.offer_delete, name='offer_delete'),
    path('create_offer', views.create_offer, name='create_offer'),
    path('finances/', views.finance_list, name='finance_list'),
]