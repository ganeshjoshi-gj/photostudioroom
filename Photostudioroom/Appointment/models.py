from enum import auto
from django import db
from django.db import models
from django.db.models.base import Model
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db.models.expressions import F
from django.db.models.fields import AutoField
from django.template.loader import render_to_string
from django.http.response import BadHeaderError,HttpResponse 
# Create your models here.



class User(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_contributor = models.BooleanField(default=False)


class State_Details(models.Model):
    state_id = models.AutoField(primary_key=True)
    state_name = models.CharField(max_length=30)

    class Meta:
        db_table = "State_Details"
        verbose_name_plural = "State_Details"

    def __str__(self):
        return (self.state_name)


class City_Details(models.Model):
    city_id = models.AutoField(primary_key=True)
    state_id = models.ForeignKey(State_Details, on_delete=models.CASCADE,db_column='state_id')
    city_name = models.CharField(max_length=30)

    class Meta:
        db_table = "City_Details"
        verbose_name_plural = "City_Details"

    def __str__(self):
        return (self.city_name)


class Area_Details(models.Model):
    area_id = models.AutoField(primary_key=True)
    city_id = models.ForeignKey(City_Details, on_delete=models.CASCADE,db_column='city_id')
    area_name = models.CharField(max_length=30)

    class Meta:
        db_table = "Area_Details"
        verbose_name_plural = "Area_Details"

    def __str__(self):
        return (self.area_name)


class Address(models.Model):
    address_id = models.AutoField(primary_key=True)
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200)
    area = models.ForeignKey(Area_Details, on_delete=models.CASCADE,db_column='area')
    city = models.ForeignKey(City_Details, on_delete=models.CASCADE,db_column='city')
    state = models.ForeignKey(State_Details, on_delete=models.CASCADE,db_column='state')
    contact_1 = models.CharField(max_length=15)
    contact_2 = models.CharField(max_length=15, blank=True, default="NA")
    saved_address_name = models.CharField(max_length=20,blank=True,null=True,default=None)
    class Meta:
        db_table = "Address"
        verbose_name_plural = "Address"

    def __str__(self):
        return str(self.address_id)


class User_Details(models.Model):

    def user_based_upload_to(instance,filename):
        return "stockimages/profile/photos{}/{}".format(instance.user_id, filename) #will return ...photos/user_name/filename.extension

    user_id = models.AutoField(primary_key=True)
    userobj = models.OneToOneField(User, on_delete=models.CASCADE)
    address_id = models.ForeignKey(Address, on_delete=models.CASCADE,blank=True,null=True,default=None,db_column='address_id')
    profile_photo = models.ImageField(upload_to=user_based_upload_to,default="stockimages/profile/photos/default-profile-photo.png")
    date_created = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "User_Details"
        verbose_name_plural = "User_Details"

    def __str__(self):
        return str(self.userobj)


class Photographer(models.Model):
    photographer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    contact_no = models.CharField(max_length=15)
    speciality = models.CharField(max_length=20)

    class Meta:
        db_table = "Photographer"
        verbose_name_plural = "Photographer"

    def __str__(self):
        return str(self.photographer_id)

    


class Event_Types(models.Model):
    event_id = models.AutoField(primary_key=True)
    event_name = models.CharField(max_length=50)
    estimated_price = models.DecimalField(max_digits=8,decimal_places=2,null=True,blank=True,default=None)

    class Meta:
        db_table = "Event_Types"
        verbose_name_plural = "Event_Types"
        
    def __str__(self):
        return (self.event_name)

class Location_Details(models.Model):
    location_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=30)

    class Meta:
        db_table = "Location_Details"
        verbose_name_plural = "Location_Details"
        
    def __str__(self):
        return (self.location_name)

class Event_Location_Details(models.Model):
    event_id = models.ForeignKey(Event_Types, on_delete=models.CASCADE,db_column='event_id',null=True,blank=True,default=None)
    location_id = models.ForeignKey(Location_Details, on_delete=models.CASCADE,db_column='location_id',null=True,blank=True,default=None)


    class Meta:
        db_table = "Event_Location_Details"
        verbose_name_plural = "Event Location Details"
        
     
        

    def __str__(self):
        return str(self.event_id) + " - " + str(self.location_id)


class Appointment(models.Model):

    pay_st_choices = (("FPD", "Full Payment Done"),
                      ("BPD", "Booking Payment Done"), ("PD", "Payment Due"))
    service_choices = (("Photo", "Photography"),
                      ("Video", "Videography"), ("Both", "Videography + Photography"))
    gear_choices = (("Cameras", "Cameras"),
                      ("C+D", "Cameras + Drone"))
    video_duration_choices = (("1-2", "1-2 Minutes"),
                      ("2-3", "2-3 Minutes"),
                      ("3-4", "3-4 Minutes"),
                      ("4-5", "4-5 Minutes"),
                      ("5-6", "5-6 Minutes"),
                      ("6-7", "6-7 Minutes"),
                      ("7-8", "7-8 Minutes"))
    appoint_id = models.AutoField(primary_key=True)
    photographer_id = models.ForeignKey(Photographer, on_delete=models.CASCADE,db_column='photographer_id',null=True,blank=True,default=None)
    user_id = models.ForeignKey(User_Details, on_delete=models.CASCADE,db_column='user_id') #Customer
    address_id = models.ForeignKey(Address, on_delete=models.CASCADE,db_column='address_id',null=True,blank=True,default=None)
    date = models.DateField()
    time = models.TimeField()
    location = models.ForeignKey(Location_Details, on_delete=models.CASCADE,db_column='location')
    event = models.ForeignKey(Event_Types, on_delete=models.CASCADE,db_column='event')
    #PhotoQuantity For Non-Package Events
    photo_quantity = models.IntegerField(null=True,blank=True,default=None)
    #Service Option For Pre-Wedding and Wedding Only
    service = models.CharField(max_length=30,blank=True,null=True,default=None,choices=service_choices)
    #Event Days For Package Events Only Like Pre-Wedding and Wedding
    #eventdays = models.IntegerField(blank=True,null=True,default=None)
    #If Videography or Both is Selected Then Gears is Available
    gears = models.CharField(max_length=20,blank=True,null=True,default=None,choices=gear_choices)
    booking_payment = models.DecimalField(max_digits=8,decimal_places=2,null=True,blank=True,default=0)
    total_payment = models.DecimalField(max_digits=8,decimal_places=2,null=True,blank=True,default=0)
    remaining_payment = models.DecimalField(max_digits=8,decimal_places=2,null=True,blank=True,default=0)
    #If Pre-Wedding is Selected and Videography or Both Has Selected Then Video Duration will be Available
    #video_duration = models.CharField(max_length=15,blank=True,null=True,default=None,choices=video_duration_choices)
    # True if appointment is Not Cancelled, false otherwise
    edited_on = models.DateField(null=True,blank=True,default=None)
    cancelled_on = models.DateField(null=True,blank=True,default=None)
    appoint_status = models.BooleanField(blank=True, default=True)
    payment_status = models.CharField(
        max_length=30, blank=True, default=None, choices=pay_st_choices)

    class Meta:
        db_table = "Appointment"
        verbose_name_plural = "Appointment"
        get_latest_by = ['date']
     
        

    def __str__(self):
        return str(self.appoint_id)

    def save(self,*args, **kwargs):
        origappoint = None
        if self.pk is not None:
            try:
                origappoint = Appointment.objects.get(appoint_id=self.appoint_id)
                print(origappoint.photographer_id)
            except Exception as e:
                print("Error in Appointment Model Overridden Save Method: ",e)

        super(Appointment, self).save(*args, **kwargs) 
        print(self.photographer_id)
        
        
        if self.pk is not None:
            try:
                print("photographer id previous in appointments models",origappoint.photographer_id)           
                print("Event in Models: ",self.event.event_name)
                print("Data Type of Event in Models: ",type(self.event.event_name))
                
                if origappoint.photographer_id == None:  #If Photographer is not selected
                    if self.photographer_id != None and self.event.event_name != "Wedding" and self.event.event_name != "Pre-Wedding": #and photographer details is changed then send mail
                        subject = "Photographer Has Been Assigned For Photoshoot"
                        email_text = "email/appointment/AppointPhotographerDetails.txt"
                        email_html = "email/appointment/AppointPhotographerDetails.html"
                        c = {
                            "email":self.user_id.userobj.email,
                            'domain':'127.0.0.1:8000',
                            'site_name': 'Photostudioroom',
                            "user": self.user_id.userobj,
                            "firstname":self.user_id.userobj.first_name,
                            "lastname":self.user_id.userobj.last_name,
                            "appoint":self,
                            "photographer":self.photographer_id,
                            "address":self.address_id,
                            "isnew":True,
                            'protocol': 'http',
                            }
                        email = render_to_string(email_text, c)
                        email_html = render_to_string(email_html, c)
                        email_from = "Photostudioroom <psr.gj26.github@gmail.com>"
                        try:
                            send_mail(subject, email, email_from , [self.user_id.userobj.email], fail_silently=False,html_message=email_html)
                        except BadHeaderError:
                            return HttpResponse('Invalid header found.')

                else: #else it means photographer is already selected
                    if self.photographer_id != origappoint.photographer_id and self.event.event_name != "Wedding" and self.event.event_name != "Pre-Wedding": #if photographer is changed then send a mail
                        subject = "Photographer Has Been Reassigned For Photoshoot"
                        email_text = "email/appointment/AppointPhotographerDetails.txt"
                        email_html = "email/appointment/AppointPhotographerDetails.html"
                        c = {
                            "email":self.user_id.userobj.email,
                            'domain':'127.0.0.1:8000',
                            'site_name': 'Photostudioroom',
                            "user": self.user_id.userobj,
                            "firstname":self.user_id.userobj.first_name,
                            "lastname":self.user_id.userobj.last_name,
                            "appoint":self,
                            "photographer":self.photographer_id,
                            "address":self.address_id,
                            "isnew":False,
                            'protocol': 'http',
                            }
                        email = render_to_string(email_text, c)
                        email_html = render_to_string(email_html, c)
                        email_from = "Photostudioroom <psr.gj26.github@gmail.com>"
                        try:
                            send_mail(subject, email, email_from , [self.user_id.userobj.email], fail_silently=False,html_message=email_html)
                        except BadHeaderError:
                            return HttpResponse('Invalid header found.')
   
            except Exception as e:
                print("Error in Appointment Model While Sending Mail in Save(): ",e)
    
    

class Categories(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=30)

    class Meta:
        db_table = "Categories"
        verbose_name_plural = "Categories"
        
    def __str__(self):
        return (self.category_name)

class Images(models.Model):
    def user_based_upload_to(instance,filename):
        return "stockimages/uploads/{}/{}".format(instance.user_id, filename)
    def user_based_upload_to_thumb(instance,filename):
        filename = "thumb" + filename
        return "stockimages/thumbnails/{}/{}".format(instance.user_id, filename)

    image_st_choices = (("A","Approved"),("R","Rejected"),("P","Pending"))

    image_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User_Details,on_delete=models.CASCADE,db_column='user_id') #Contributor
    image_name = models.CharField(max_length=30,blank=True,null=True,default=None)
    category = models.ForeignKey(Categories,on_delete=models.CASCADE,db_column='category',blank=True,null=True,default=None)
    price = models.DecimalField(max_digits=8,decimal_places=0,blank=True,null=True,default=None)
    size = models.CharField(max_length=10,blank=True,null=True,default=None)
    image_format = models.CharField(max_length=10,blank=True,null=True,default=None)
    resolution = models.CharField(max_length=20,blank=True,null=True,default=None)
    description = models.CharField(max_length=100,blank=True,null=True,default=None)
    image_thumb = models.ImageField(upload_to=user_based_upload_to_thumb,default="")
    image_upload = models.ImageField(upload_to=user_based_upload_to,default="")
    tags = models.CharField(max_length=200,blank=True,null=True,default=None)
    downloads = models.IntegerField(blank=True,null=True,default=0)
    views = models.IntegerField(blank=True,null=True,default=0)
    likes = models.IntegerField(blank=True,null=True,default=0)
    status = models.CharField(max_length=15,choices=image_st_choices,default="P")
    fordeveloper = models.CharField(max_length=50,blank=True,null=True,default=None) #Used When Uploading Image Check Docstring in fillDetailsUploadImageForm View.
    total_earnings = models.DecimalField(max_digits=8,decimal_places=0,blank=True,null=True,default=0)
    total_unpaid_earnings = models.DecimalField(max_digits=8,decimal_places=0,blank=True,null=True,default=0)
    date_added = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "Images"
        verbose_name_plural = "Images"
        

    def __str__(self):
        return str(self.image_name)

    def save(self,*args, **kwargs):
        orig = None
        if self.pk is not None:
            try:
                orig = Images.objects.get(image_id=self.pk)
                print(orig.status)
            except Exception as e:
                print("Error in Images Model Overridden Save Method: ",e)
            
        super(Images, self).save(*args, **kwargs) 
        print(self.status)
        

        if self.pk is not None:
            
            try:
                if orig.status != self.status: #If Status is Changed Then Send Mail
                    if self.status == "A":
                            subject = 'Thank You For Requesting Image Approval On Photostudioroom'
                            email_text = "email/stockimages/contributor/imageapproved.txt"
                            email_html = "email/stockimages/contributor/imageapproved.html"
                            c = {
                                "email":self.user_id.userobj.email,
                                'domain':'127.0.0.1:8000',
                                'site_name': 'Photostudioroom',
                                "user": self.user_id.userobj,
                                "firstname":self.user_id.userobj.first_name,
                                "lastname":self.user_id.userobj.last_name,
                                'protocol': 'http',
                                }
                            email = render_to_string(email_text, c)
                            email_html = render_to_string(email_html, c)
                            email_from = "Photostudioroom <psr.gj26.github@gmail.com>"
                            try:
                                send_mail(subject, email, email_from , [self.user_id.userobj.email], fail_silently=False,html_message=email_html)
                            except BadHeaderError:
                                return HttpResponse('Invalid header found.')
                        
                    elif self.status == "R":
                            subject = 'Thank You For Requesting Image Approval On Photostudioroom'
                            email_text = "email/stockimages/contributor/imagerejected.txt"
                            email_html = "email/stockimages/contributor/imagerejected.html"
                            c = {
                                "email":self.user_id.userobj.email,
                                'domain':'127.0.0.1:8000',
                                'site_name': 'Photostudioroom',
                                "user": self.user_id.userobj,
                                "firstname":self.user_id.userobj.first_name,
                                "lastname":self.user_id.userobj.last_name,
                                'protocol': 'http',
                                }
                            email = render_to_string(email_text, c)
                            email_html = render_to_string(email_html, c)
                            email_from = "Photostudioroom <psr.gj26.github@gmail.com>"
                            try:
                                send_mail(subject, email, email_from , [self.user_id.userobj.email], fail_silently=False,html_message=email_html)
                            except BadHeaderError:
                                return HttpResponse('Invalid header found.')
            except Exception as e:
                print("Error In Images Model: ",e)
                    

   
class Like_Details(models.Model):
    user_id = models.ForeignKey(User_Details,on_delete=models.CASCADE,db_column='user_id')
    image_id = models.ForeignKey(Images,on_delete=models.CASCADE,db_column='image_id')

    class Meta:
        db_table = "Like_Details"
        verbose_name_plural = "Like Details"
        
    def __str__(self):
        return (str(self.image_id)  + " _ " + str(self.user_id))


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User_Details,on_delete=models.CASCADE,db_column='user_id') #Customer
    order_date = models.DateField(auto_now_add=True)
    order_time = models.TimeField(auto_now_add=True)
    Total_Amount = models.DecimalField(max_digits=8,decimal_places=2)
    InCart = models.BooleanField()

    class Meta:
        db_table = "Order"
        verbose_name_plural = "Order"
        
    def __str__(self):
        return str(self.order_id)

    #Operations
   

class Order_Details(models.Model):
    order_id = models.ForeignKey(Order,on_delete=models.CASCADE,db_column='order_id')
    image_id = models.ForeignKey(Images,on_delete=models.CASCADE,db_column='image_id')

    class Meta:
        db_table = "Order_Details"
        verbose_name_plural = "Order Details"
        
    def __str__(self):
        return (str(self.order_id)  + " _ " + str(self.image_id))

class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User_Details,on_delete=models.CASCADE,db_column='user_id') #Customer

    class Meta:
        db_table = "Cart"
        verbose_name_plural = "Cart"
        
    def __str__(self):
        return (str(self.cart_id)  + " _ " + str(self.user_id))

class Cart_Details(models.Model):
    cart_id = models.ForeignKey(Cart,on_delete=models.CASCADE,db_column='cart_id')
    image_id = models.ForeignKey(Images,on_delete=models.CASCADE,db_column='image_id')
    class Meta:
        db_table = "Cart_Details"
        verbose_name_plural = "Cart Details"
        
    def __str__(self):
        return (str(self.cart_id)  + " _ " + str(self.image_id))

class Payment_Details(models.Model):
    pay_details_id = models.AutoField(primary_key=True)
    card_no = models.CharField(max_length=50) #Card No / UPI Id
    card_holder_name = models.CharField(max_length=50,blank=True,default=None) #Blank if UPI is Used
    expiry_date = models.DateField(blank=True,default=None) #Blank if UPI is Used

    class Meta:
        db_table = "Payment_Details"
        verbose_name_plural = "Payment_Details"
        
    def __str__(self):
        return str(self.pay_details_id)

class Payment(models.Model): #Merged Booking_Payment,Image_Payment & Contributor_Payment Table

    pay_mode_choices = (("DC","Debit Card"),("CC","Credit Card"),("U","UPI"))

    pay_id = models.AutoField(primary_key=True)
    pay_details_id = models.ForeignKey(Payment_Details,on_delete=models.CASCADE,db_column='pay_details_id')
    user_id = models.ForeignKey(User_Details,on_delete=models.CASCADE,db_column='user_id') #Any
    appoint_id = models.ForeignKey(Appointment,on_delete=models.CASCADE,db_column='appoint_id',null=True,blank=True,default=None) #Null if Payment Of Image
    order_id = models.ForeignKey(Order,on_delete=models.CASCADE,db_column='order_id',null=True,blank=True,default=None) #Null if Payment of Appointment Booking
    payment_date_time = models.DateField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=8,decimal_places=2)
    payment_mode = models.CharField(max_length=20,choices=pay_mode_choices)
    description = models.CharField(max_length=100,null=True,blank=True,default=None)
    payment_status = models.CharField(max_length=10,null=True,blank=True,default="Due") #Payment Done or Due

    class Meta:
        db_table = "Payment"
        verbose_name_plural = "Payment"
        
    def __str__(self):
        return str(self.pay_id)


class Contributor_Payment(models.Model):
    cont_pay_id = models,AutoField(primary_key=True)
    user_id = models.ForeignKey(User_Details, on_delete=models.CASCADE,db_column='user_id')
    pay_details_id = models.ForeignKey(Payment_Details,on_delete=models.CASCADE,db_column='pay_details_id')
    total_amount = models.DecimalField(max_digits=8,decimal_places=2,null=True,blank=True,default=0)
    payment_datetime = models.DateField(auto_now_add=True)
    
    class Meta:
        db_table = "Contributor_Payment"
        verbose_name_plural = "Contributor Payment"
        
    def __str__(self):
        return (str(self.pay_details_id))


class Contributor_Payment_Details(models.Model):
    cont_pay_id = models.ForeignKey(Contributor_Payment,on_delete=models.CASCADE,db_column='cont_pay_id',default=None)
    image_id = models.ForeignKey(Images,on_delete=models.CASCADE,db_column='image_id',null=True,blank=True,default=None)
    downloads_when_paid = models.IntegerField(blank=True,null=True,default=0)
    payment_status = models.BooleanField(default=False,null=True,blank=True)
    
    class Meta:
        db_table = "Contributor_Payment_Details"
        verbose_name_plural = "Contributor_Payment_Details"
        
    def __str__(self):
        return (str(self.cont_pay_id) + " _ " + str(self.image_id))


class Remaining_Contributor_Payment(models.Model):
    rem_cont_pay_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User_Details, on_delete=models.CASCADE,db_column='user_id')
    total_amount = models.DecimalField(max_digits=8,decimal_places=0,null=True,blank=True,default=0)
    addedon = models.DateField(auto_now_add=True)
    
    class Meta:
        db_table = "Remaining_Contributor_Payment"
        verbose_name_plural = "Remaining Contributor Payment"
        
    def __str__(self):
        return (str(self.rem_cont_pay_id))


class Remaining_Contributor_Payment_Details(models.Model):
    rem_cont_pay_id = models.ForeignKey(Remaining_Contributor_Payment,on_delete=models.CASCADE,db_column='rem_cont_pay_id',default=None)
    image_id = models.ForeignKey(Images,on_delete=models.CASCADE,db_column='image_id',null=True,blank=True,default=None)
    downloads_when_purchased = models.IntegerField(blank=True,null=True,default=0)
    amount = models.DecimalField(max_digits=8,decimal_places=0,null=True,blank=True,default=0)
    payment_status = models.BooleanField(default=False,null=True,blank=True)
    
    class Meta:
        db_table = "Remaining_Contributor_Payment_Details"
        verbose_name_plural = "Remaining Contributor Payment Details"
        
    def __str__(self):
        return (str(self.rem_cont_pay_id) + " _ " + str(self.image_id))











    



