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
from StockImages import views

urlpatterns = [
    path('', views.stockImagesHome,name="StockHome"),
    path('search',views.search,name="Search"),
    path('category=<str:category>',views.categories,name="Categories"),
    path('cart',views.cart,name="AddToCart"),
    path('view-cart',views.showCart,name="ShowCart"),
    path('remove-cart',views.removeCart,name="RemoveCart"),
    #path('show-cart',views.showCart,name="showCart"),
    #path('show-cart=<str:psr>',views.showCart,name="showCart"),
    

    #Payment
    path('payment',views.stockpaymentpage,name="StockPayment"),
    path('payment/image/<str:image>',views.stockpaymentpage,name="StockPayment"),
    path('payment/auth/<str:imageparam>',views.stockpaymentload,name="StockPaymentCheckDirectPurchase"),
    path('payment/authenticate',views.stockpaymentload,name="StockPaymentCheckAddToCart"),

    #contributor
    path('contributor/dashboard',views.showDashboard,name="dashboard"),
    path('contributor/dashboard/earnings',views.showEarnings,name="showEarnings"),
    path('contributor/uploadimage',views.uploadImageForm,name="uploadimage"),
    path('contributor/uploadimage/filldetails',views.fillDetailsUploadImageForm,name="fillDetailsUploadImageForm"),
    path('contributor/uploadimage/upload-image',views.uploadImageFromCont,name="uploadimageFromCont"),
    path('contributor/showimage/<int:imageid>',views.showImageForCont,name="showImageForCont"),
    
    #contributor - update images from dashboard
    path('contributor/editimage/<int:imageid>',views.updateImageDetails,name="updateImageDetails"),
    path('contributor/deleteimage/<int:imageid>',views.deleteImageForCont,name="deleteImageForCont"),

    
    


    #temp
    
    path('watermark',views.wm,name="temp"),
]
