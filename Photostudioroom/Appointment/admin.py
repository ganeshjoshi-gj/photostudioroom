from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Address, Images,State_Details,City_Details,Area_Details,User_Details,Photographer,Appointment,Order,Order_Details,Payment_Details,Payment,Contributor_Payment_Details,Event_Types,Location_Details,Categories,User,Cart,Cart_Details,Like_Details,Event_Location_Details
# Register your models here.

admin.site.register(Address)
admin.site.register(State_Details)
admin.site.register(City_Details)
admin.site.register(Area_Details)
admin.site.register(User_Details)
admin.site.register(Photographer)
admin.site.register(Appointment)
admin.site.register(Images)
admin.site.register(Order)
admin.site.register(Order_Details)
admin.site.register(Payment_Details)
admin.site.register(Payment)
admin.site.register(Contributor_Payment_Details)
admin.site.register(Event_Types)
admin.site.register(Location_Details)
admin.site.register(Categories)
admin.site.register(User,UserAdmin)
admin.site.register(Cart)
admin.site.register(Cart_Details)
admin.site.register(Event_Location_Details)
