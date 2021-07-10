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
from django.urls.conf import include, re_path
from Photostudioroom import settings, views
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views #import this

admin.site.site_header = "PSR Admin"
admin.site.site_title = "Photostudioroom Admin Portal"
admin.site.index_title = "Welcome to PSR Portal"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index,name="Home"),
    path('adminhome/', views.showAdminHome,name="showAdminHome"),
    path('adminhome/result/<str:success>', views.showAdminHome,name="showAdminHome"),
    path('adminhome/<int:contid>', views.showContWiseData,name="showContWiseData"),
    path('adminhome/<int:contid>/payment/<int:totalpayment>', views.loadPaymentPageForContPayment,name="loadPaymentPageForContPayment"),
    path('adminhome/<int:contid>/payment/<int:totalpayment>/authenticate/<str:username>',views.paymentForContAuto,name="paymentForContAuto"),
    
    path('base', views.temp,name="temp"),
    path('login/',views.login_page,name="loginpage"),
    path('login/<str:nextpage>',views.login_page,name="temp_loginwnext"),
    path('logout',views.logout_page,name="temp_logout"),
    path('register',views.register_home,name="register_home"),
    path('register-customer',views.register_cust,name="register_cust"),
    path('register-contributor',views.register_cont,name="register_cont"),
    path('check-user-name',views.checkUsername,name="checkUsername"),
    path('forgotpassword',views.forgotPassword,name="forgotPassword"),
    path('help',views.help,name="help"),
    
    #path('accounts/', include('django.contrib.auth.urls')),
    #path('password_reset/done/', views.resetDone, name='password_reset_done'),
    #path('reset/<uidb64>/<token>/', views.resetConfirm, name='password_reset_confirm'),
    #path('reset/done/', views.resetComplete,name='password_reset_complete'),



    
    
    
    path('temp',views.temp,name="temp"),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='passwordreset/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/<str:username>', views.resetConfirm, name='password_reset_confirm'),
    path('reset/confirm', views.resetConfirm, name='password_reset_confirm'),
    path('reset/done/',views.resetComplete, name='password_reset_complete'),
    
    path('about',views.about,name="about"),
    path('appointment/',include("Appointment.urls")),
    path('stockimages/',include("StockImages.urls")),

    #Profile
    path('profile',views.showProfile,name="Profile"),
    path('profile?status=',views.showProfile,name="ProfileWithStatus"),

    #Update
    path('updatepersonal',views.updatePersonal,name="UpdatePersonal"),
    path('updateaddress',views.updateAddress,name="UpdateAddress"),
    path('updatepassword',views.updatePassword,name="UpdatePassword"),
    path('uploadprofilephoto',views.uploadprofilephototemp,name="UploadProfilePhoto"),

    #Ajax
    path('load-cities/', views.load_cities, name='ajax_load_cities'), 
    path('load-areas/', views.load_areas, name='ajax_load_areas'), 
    
    #Email Formatting Testing - TEMP
    path('testemail', views.testEmailFormat, name='testEmail'), 
    


] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
