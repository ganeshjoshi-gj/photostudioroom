"""Photostudioroom URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from Appointment import views
from Photostudioroom import views as psrviews

urlpatterns = [
    path('', views.appointmentHome,name="Appointment"),
    path('packages', views.showPackages,name="showPackages"),
    path('appointment-form', views.appointmentForm,name="AppointmentForm"),
    path('editappointment-form/<int:appoint_id>', views.editAppointment,name="editAppointment"),
    path('appointment-form/cancel/<int:appoint_id>', views.deleteAppointment,name="deleteAppointment"),
    path('submitappointment-form', views.appointmentForm,name="SubmitAppointmentForm"),
    path('check-saved-address-name',views.checkSavedAddressName,name="checkSavedAddressName"),
    path('get-saved-address',views.sendSavedAddress,name="sendSavedAddress"),
    #Payment
    
    path('payment/authenticate',views.appointpaymentload,name="AppointPaymentCheck"),
    path('payment/<int:bookingamount>',views.appointpaymentpage,name="AppointPayment"),

    #Ajax
    path('getestimatedprice/',views.getEstimatedPrice, name='get_estimated_price'), 
    path('load-cities/', psrviews.load_cities, name='ajax_load_cities'), 
    path('load-areas/', psrviews.load_areas, name='ajax_load_areas'),

    path('load-places/', views.load_places, name='ajax_load_places'),
]
