import datetime
import json
from django.db.models.expressions import F
from django.http.response import BadHeaderError, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from .models import *
from Photostudioroom.views import login_page, temp
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
# Create your views here.

#Main Appointment Page
def appointmentHome(request):
    return render(request,"appointment/appointment.html",{'isappointactive':'class=active id=active'}) #isappointactive for nav bar to set orange bg in navbar,id as active to get orange color back when scroll up 

#Appointment Form Page
def appointmentForm(request):
    
    print("\n\nWe are in appointmentForm")
    curuser = None
    eventtype = None
    place = None
    selectedevent = None
    booking_amount = 0
    remaining_amount = 0
    if not request.user.is_authenticated:
        print("Not Logged in So Redirecting to Login - in appointmentForm View")
        return redirect('/login/appointment-form')
    else:
        try:
            curuser = request.user  # Getting Current Logged in User
            curuser = User_Details.objects.get(userobj=curuser)
        except TypeError as e:
            print("Error in appointForm while getting user details, Error: ", e)
    isestimated = None
    print("appointmentForm View Called")
    estimatedamount = None
    if request.method == "POST" and not request.is_ajax(): #If Data is Submitted and it is not From AJAX(it means form is submitted)
        print("\n\nMethod is POST in appointmentForm")
        isestimated = "true"
        #Getting Data From Form
        place = None
        service = None
        gears = None
        #eventdays = None
        #videoduration = None
        photosquantity = None
        estimatedamount = None
        
        eventtype = request.POST["selectevent"]
        try:
            place = request.POST["selectplace"]
        except Exception as e:
            print("Place Not Found")
        date = request.POST["date"]
        time = request.POST["time"]
        try:
            service = request.POST["services"]
        except Exception as e:
            print("Services Not Found")
        try:
            gears = request.POST["gears"]
        except Exception as e:
            print("Gears Not Found")
        """
        try:
            eventdays = request.POST["eventdays"]
        except Exception as e:
            print("EventDays Not Found")
        
        try:
            videoduration = request.POST["videodur"]
        except Exception as e:
            print("VideoDuration Not Found")
        """
        try:
            photosquantity = request.POST["photosquantity"]
        except Exception as e:
            print("PhotosQuantity Not Found")
        
        print(f".............Details Entered In AppointmentForm.............\nEvent: {eventtype}\nPlace: {place}\nDate: {date}\nTime: {time}\nService: {service}\nGears: {gears}\nPhotos Quantity: {photosquantity}")
        
        
        #address
        line1 = request.POST["addressline1"]
        line2 = request.POST["addressline2"]
        state = request.POST.get('selectstate', False);
        city = request.POST.get('selectcity', False);
        area = request.POST.get('selectarea', False);
        phone1 = request.POST["phone_number"]
        phone2 = request.POST["phone_number2"]
        savedaddress = request.POST["savedaddressname"]
        print("Saved Address: ",savedaddress) 
        try:
            #Trying to Get Event_Types and Location_Details Object
            eventtype = Event_Types.objects.get(event_id=eventtype)
            place = Location_Details.objects.get(location_id=place)
            selectedevent = eventtype.event_id
        except Exception as e:
            print("Got error in getting eventtype and place in appointmentform: ",e)

        try:
            print(area)
            if area != False and city != False and state != False: #If area,city and state is not False(means not null)
                #Then get its Objects
                areaobj = Area_Details.objects.get(area_id=area)
                cityobj = City_Details.objects.get(city_id=city)
                stateobj = State_Details.objects.get(state_id=state)
            else: #If it is null
                #Get addressobject of current user then fetch area,city and state
                addressobj = Address.objects.get(address_id=curuser.address_id.address_id)
                areaobj = Area_Details.objects.get(area_id=addressobj.area.area_id)
                cityobj = City_Details.objects.get(city_id=addressobj.city.city_id)
                stateobj = State_Details.objects.get(state_id=addressobj.state.state_id) 
            #NOw Trying to Get Address Object with Above Details
            address = Address.objects.get(address_line1=line1,address_line2=line2,area=areaobj,city=cityobj,state=stateobj,contact_1=phone1,contact_2=phone2)
        except Exception as e: #If Got Any Error
            print(e)
            print("\n\nError in getting address in appointmentForm")
            try:
                print("\n\nTrying to create new address in appointmentForm")
                if area != False and city != False and state != False:
                    areaobj = Area_Details.objects.get(area_id=area)
                    cityobj = City_Details.objects.get(city_id=city)
                    stateobj = State_Details.objects.get(state_id=state)
                else:
                
                    addressobj = Address.objects.get(address_id=curuser.address_id.address_id)
                    areaobj = Area_Details.objects.get(area_id=addressobj.area.area_id)
                    cityobj = City_Details.objects.get(city_id=addressobj.city.city_id)
                    stateobj = State_Details.objects.get(state_id=addressobj.state.state_id)
                #Create New Address For Appointment
                address = Address.objects.create(address_line1=line1,address_line2=line2,area=areaobj,city=cityobj,state=stateobj,contact_1=phone1,contact_2=phone2)
            except Exception as e:
                
                print("\n\nError in creating new address in appointmentForm: ",e)
            else:
                if len(savedaddress) > 0:
                    #Checking if savedaddress name is already used by the current user
                    tempaddressids = []
                    tempalreadyavailable = False
                    #Getting Appointments and then getting addresses from it
                    try:
                        tempappoints = Appointment.objects.filter(user_id=curuser.user_id)
                    except Exception as e:
                        print("Error While Getting TempAppoints in appointmentForm(): ",e)
                    else:
                        for tempappoint in tempappoints:
                            if tempappoint.address_id != None:
                                tempaddressids.append(tempappoint.address_id.address_id)

                        try:
                            tempaddresses = Address.objects.in_bulk(tempaddressids)
                        except Exception as e:
                            print("Error While Getting tempaddresses in appointmentForm(): ",e)
                        else:
                            for key,value in tempaddresses.items():
                                if value.saved_address_name == savedaddress:
                                    tempalreadyavailable = True
                    #Getting Address From The UserDetails Table
                    try:
                        tempaddress = Address.objects.get(address_id=curuser.address_id.address_id)
                    except Exception as e:
                        print("Error While Getting Address Object From The Cursuser in appoointmentForm: ",e)
                    else:
                        if tempaddress.saved_address_name == savedaddress:
                            tempalreadyavailable = True
                    
                    #If Name is Not Already Available Then Save it
                    if not tempalreadyavailable:
                        address.saved_address_name = savedaddress
                print("\n\naddress created saving it in appointmentForm")
                try:
                    address.save()
                except Exception as e:
                    print("Error While Saving address obj in appointmentForm(): ",e)
        


        try:
            print("\nTrying to Create appoint object in appointmentForm")

            #Photoquantity is Not None, It Means User is Booking Per Photo Events
            if photosquantity != None:
                """
                This will create Appointment For
                -Outdoor Photoshoot
                -Product Photography
                -Baby Shower
                -Fashion
                -Advertising
                It Means Other Than Pre-Wedding and Wedding
                """
                print("This is Per Photo Booking")
                #Getting Estimated Amount According to Entered Details
                estimatedamount = getEstimatedPrice(eventtype.event_name,place.location_name,photosquantity)
                print(estimatedamount)
                
                try:
                    estimatedamount = int(estimatedamount)
                    booking_amount = estimatedamount * 20 / 100
                    remaining_amount = estimatedamount - booking_amount
                except Exception as e:
                    print("Error While Calculating Booking Amount in appointmentForm: ",e)

                appoint = Appointment.objects.create(user_id=curuser,address_id=address,date=date,time=time,location=place,event=eventtype,photo_quantity=photosquantity,total_payment=estimatedamount,booking_payment=booking_amount,remaining_payment=remaining_amount,payment_status="Due")
                print("Created Appointment Object in Per Photo in appointmentForm()")
                
            else: #Package 
                booking_amount = 500
                print("This is Package Booking")
                if gears != None:
                    print("Videography is there in the package")
                    
                    appoint = Appointment.objects.create(user_id=curuser,date=date,time=time,location=place,event=eventtype,service=service,booking_payment=booking_amount,gears=gears,payment_status="Due")
                    print("Created Appointment Object in Package in videography in appointmentForm()")
                else:
                    """
                    This will create Appointment For
                    -Pre-Wedding and Wedding in Which Only Photography is Needed
                    """
                    print("Only Photography is selected")
                    appoint = Appointment.objects.create(user_id=curuser,date=date,time=time,location=place,event=eventtype,service=service,booking_payment=booking_amount,payment_status="Due")
                    print("Created Appointment Object in Package in Photography Only in appointmentForm()")
        except Exception as e:
            
            print("\n\nError to create appoint obj in appointmentForm: ",e)
        else:
            print("\n\nAppoint obj created now saving it in appointmentForm")
            appoint.save()
    
    curuser = None
    userdet = None
    address = None
    eventtypes = None
    states = None
    
    if request.user.is_authenticated:
        try:
            curuser = User.objects.get(id=request.user.id)
            curuser = User_Details.objects.get(userobj=curuser)
            try:
                #Get Address Object
                address = Address.objects.get(address_id=int(str(curuser.address_id)))
            except Exception as e:
                print("\n\nError in getting address obj in appointmentForm Line 134: ",e)
            #Getting All The Events,states and places
            eventtypes = Event_Types.objects.all()
            states = State_Details.objects.all()
            
        except Exception as e:
            print("\n\nError in getting user obj in appointmentForm Line 140 : ",e)

    #Send Saved Addresses
    tempaddressids = []
    tempalreadyavailable = False
    savedaddressnames = []
    #Getting Appointments and then getting addresses from it
    try:
        tempappoints = Appointment.objects.filter(user_id=curuser.user_id)
    except Exception as e:
        print("Error While Getting TempAppoints in appointmentForm(): ",e)
    else:
        for tempappoint in tempappoints:
            if tempappoint.address_id != None:
                tempaddressids.append(tempappoint.address_id.address_id)

        try:
            tempaddresses = Address.objects.in_bulk(tempaddressids)
        except Exception as e:
            print("Error While Getting tempaddresses in appointmentForm(): ",e)
        else:
            for key,value in tempaddresses.items():
                if value.saved_address_name != None:
                    savedaddressnames.append(value.saved_address_name)
                    
    #Getting Address From The UserDetails Table
    try:
        tempaddress = Address.objects.get(address_id=curuser.address_id.address_id)
    except Exception as e:
        print("Error While Getting Address Object From The Cursuser in appoointmentForm: ",e)
    else:
        if tempaddress.saved_address_name != None:
            savedaddressnames.append(tempaddress.saved_address_name)
        


    #Sending 500 Counter For Per Photo Selection
    fivehundredphotos = []
    for i in range(5,501,5):
    
        fivehundredphotos.append(i)
    print(savedaddressnames)
    try:
        booking_amount = int(booking_amount)
    except Exception as e:
        print(e)
    return render(request,"appointment/appointmentform.html",{"curuser":curuser,"address":address,"eventtypes":eventtypes,"states":states,'isestimated':isestimated,'estimatedamount':estimatedamount,"bookingamount":booking_amount,'fivehundredphotos':fivehundredphotos,'selectedevent':selectedevent,"savedaddresses":savedaddressnames})
    
    
#To Check if Saved Address Name is Already Used
def checkSavedAddressName(request):
    curuser = None
    try:
        curuser = User.objects.get(id=request.user.id)
        curuser = User_Details.objects.get(userobj=curuser)
    except Exception as e:
        print("Error While Getting User Obj in checkSavedAddressName(): ",e)
    
    if request.is_ajax and request.method == "GET":
        savedaddress = request.GET.get("savedaddressname", None)
        tempaddressids = []
        tempalreadyavailable = False
        #Getting Appointments and then getting addresses from it
        try:
            tempappoints = Appointment.objects.filter(user_id=curuser.user_id)
            print(tempappoints)
            print(type(tempappoints))
        except Exception as e:
            print("Error While Getting TempAppoints in checkSavedAddressName(): ",e)
        else:
            print(tempappoints)
            print(type(tempappoints))
            if tempappoints != None:
                for tempappoint in tempappoints:
                    print(type(tempappoint.address_id))
                    print(tempappoint.address_id)
                    if tempappoint.address_id != None:
                        tempaddressids.append(tempappoint.address_id.address_id)

                try:
                    tempaddresses = Address.objects.in_bulk(tempaddressids)
                except Exception as e:
                    print("Error While Getting tempaddresses in checkSavedAddressName(): ",e)
                else:
                    print(tempaddresses)
                    
                    for key,value in tempaddresses.items():
                        if value.saved_address_name == savedaddress:
                            tempalreadyavailable = True
                            
                        #Getting Address From The UserDetails Table
                    try:
                        tempaddress = Address.objects.get(address_id=curuser.address_id.address_id)
                    except Exception as e:
                        print("Error While Getting Address Object From The Cursuser in checkSavedAddressName: ",e)
                    else:
                        if tempaddress.saved_address_name == savedaddress:
                            tempalreadyavailable = True
                        
                        #If Name is Not Already Available Then Save it
                    if not tempalreadyavailable:
                        # if savedaddressname not found, then user can create a new address with this savedname
                        return JsonResponse({"valid":True}, status = 200)
                    else:
                        return JsonResponse({"valid":False}, status = 200)
            else:
                return JsonResponse({"valid":True}, status = 200)
        return JsonResponse({}, status = 400)


#To Send Address Details According to Selected Saved Address
def sendSavedAddress(request):
    curuser = None
    try:
        curuser = User.objects.get(id=request.user.id)
        curuser = User_Details.objects.get(userobj=curuser)
    except Exception as e:
        print("Error While Getting User Obj in checkSavedAddressName(): ",e)
    
    if request.is_ajax and request.method == "GET":
        savedaddress = request.GET.get("savedaddressname", None)
        tempaddressids = []
        sendaddress = None
        
        #Getting Appointments and then getting addresses from it
        try:
            tempappoints = Appointment.objects.filter(user_id=curuser.user_id)
            print(tempappoints)
            print(type(tempappoints))
        except Exception as e:
            print("Error While Getting TempAppoints in checkSavedAddressName(): ",e)
        else:
            print(tempappoints)
            print(type(tempappoints))
            if tempappoints != None:
                for tempappoint in tempappoints:
                    print(type(tempappoint.address_id))
                    print(tempappoint.address_id)
                    if tempappoint.address_id != None:
                        tempaddressids.append(tempappoint.address_id.address_id)

                try:
                    tempaddresses = Address.objects.in_bulk(tempaddressids)
                except Exception as e:
                    print("Error While Getting tempaddresses in checkSavedAddressName(): ",e)
                else:
                    print(tempaddresses)
                    
                    for key,value in tempaddresses.items():
                        if value.saved_address_name == savedaddress:
                            sendaddress = value
                            
                        #Getting Address From The UserDetails Table
                    try:
                        tempaddress = Address.objects.get(address_id=curuser.address_id.address_id)
                    except Exception as e:
                        print("Error While Getting Address Object From The Cursuser in checkSavedAddressName: ",e)
                    else:
                        if tempaddress.saved_address_name == savedaddress:
                            sendaddress = value
                        
                    
                        #If Name is Not Already Available Then Save it
                    if sendaddress != None:
                        try:
                            try:
                                area =Area_Details.objects.filter(area_id=sendaddress.area.area_id)
                            except Exception as e:
                                print(e)
                            try:
                                city =City_Details.objects.filter(city_id=sendaddress.city.city_id)
                            except Exception as e:
                                print(e)
                            try:
                                state =State_Details.objects.filter(state_id=sendaddress.state.state_id)
                            except Exception as e:
                                print(e)
                        except Exception as e:
                            print(e)
                        else:
                            from django.core import serializers
                            line1 = sendaddress.address_line1
                            line2 = sendaddress.address_line2
                            contact1 = sendaddress.contact_1
                            contact2 = sendaddress.contact_2
                            obj_json = serializers.serialize('json', area )
                            obj_list = json.loads( obj_json )
                            area = json.dumps( obj_list )
                            obj_json = serializers.serialize('json', city )
                            obj_list = json.loads( obj_json )
                            city = json.dumps( obj_list )
                            obj_json = serializers.serialize('json', state )
                            obj_list = json.loads( obj_json )
                            state = json.dumps( obj_list )
                            # if savedaddressname not found, then user can create a new address with this savedname
                            return JsonResponse({"valid":True,"line1":line1,"line2":line2,"area":area,"city":city,"state":state,"contact_1":contact1,"contact_2":contact2}, status = 200)
                        return JsonResponse({}, status = 400)
                    else:
                        return JsonResponse({}, status = 400)
            else:
                return JsonResponse({"valid":True}, status = 200)
        return JsonResponse({}, status = 400)


#To Calculate Estimated Price For Appointment According to Given Details
def getEstimatedPrice(eventtype,place,photosquantity):
    print("\n\nWe are in getEstimatedPrice")
    print("eventtype =",type(eventtype))
    print("place =",place)
    print("Photos Quantity =",photosquantity)
    
    OUTDOOR_PRICE_PER_PHOTO = 20
    FASHION_PRICE_PER_PHOTO = 20
    PRODUCT_PRICE_PER_PHOTO = 30
    ADVERTISE_PRICE_PER_PHOTO = 30
    BABYSHOWER_PRICE_PER_PHOTO = 40 


    try:
        photosquantity = int(photosquantity)
    except Exception as e:
        print("Unable to convert photosquantity to int in getEstimatedPrice View: ",e)
    #Our Algorithm to Decide Estimated Amount
    #Sea Side/Beach/Riverfront

    if eventtype == "Outdoor/Portrait Photoshoot":
        print("in eventtype if")
        if place == "Sea Side/Beach/Riverfront":
            return (OUTDOOR_PRICE_PER_PHOTO + 5) * photosquantity
        else:
            return OUTDOOR_PRICE_PER_PHOTO * photosquantity


    elif eventtype == "Product Photography":
        print("in eventtype if")
        if place == "Studio":
            print("in place if")
            return PRODUCT_PRICE_PER_PHOTO * photosquantity

    elif eventtype == "Baby Shower":
        print("in eventtype if")
        if place == "Garden":
            print("in place if")
            return (BABYSHOWER_PRICE_PER_PHOTO + 5) * photosquantity
        elif place == "Home":
            return BABYSHOWER_PRICE_PER_PHOTO * photosquantity

    elif eventtype == "Fashion":
        if place == "Studio":
            return FASHION_PRICE_PER_PHOTO * photosquantity
        if place == "Garden":
            return (FASHION_PRICE_PER_PHOTO + 5) * photosquantity

    elif eventtype == "Advertising":
        print("in eventtype if")
        if place == "Studio":
            return ADVERTISE_PRICE_PER_PHOTO * photosquantity
        else:
            return (ADVERTISE_PRICE_PER_PHOTO + 5) * photosquantity
   

#This will Load Payment Page For Appointment Payment
def appointpaymentpage(request,bookingamount=None):
    print("\n\nWe are in appointpaymentpage")
    return render(request,"payment/appointpayment.html",{"bookingamount":bookingamount})

#This Will Save Payment Data to The Database
def appointpaymentload(request):
    print("\n\nWe are in appointpaymentload")
    curuser = None
    paymobj = None
    estimateamount = None
    booking_amount = None
    if request.user.is_authenticated:
        try:
            curuser = User.objects.get(id=request.user.id)
            curuser = User_Details.objects.get(userobj=curuser)
        except Exception as e:
            print("\n\nError in getting user obj in appointmentpaymentload: ",e)
    if request.method == "POST":
        print("\n\nPOST in appointpaymentload")
        #Getting Data From Form
        cardholdername = request.POST.get("card-holder")
        expmonth = request.POST.get("expmm")
        expyear = request.POST.get("expyy")
        cardnumber = request.POST.get("card-number")
        print(cardholdername,expmonth,expyear,cardnumber)
        expdate = expmonth + "/"+ expyear
        print(expdate)

        try:
            print("\n\nTrying to get paymentdetails obj in appointpaymentload")
            #Converting to Datetime Object
            expdateobj = datetime.datetime.strptime(expdate, '%m/%y').date()
            
            print(expdateobj)
            #Trying to Get Payment_Details obj if Already same Data is Available
            paydet = Payment_Details.objects.get(card_no=cardnumber,card_holder_name=cardholdername,expiry_date=expdateobj)
            
        except Exception as e:
            
            print("\n\npaymentdetails obj not found in appointpaymentload: ",e)
            try:
                print("\n\nSo trying to create payment details obj in appointpaymentload")
                paydet = Payment_Details.objects.create(card_no=cardnumber,card_holder_name=cardholdername,expiry_date=expdateobj)
            except Exception as e:
                print("\n\n unable to create payment details obj in appointpaymentload: ",e)
                
            else:
                print("\n\ncreated payment details obj now saving it in appointpaymentload")
                try:
                    paydet.save()
                except Exception as e:
                    print("\n\nError While Saving paymentdetails obj in appointmentpaymentload: ",e)
                else:
                    #Getting Latest Appointment Object(Which is currently being submitted)
                    appoint = Appointment.objects.filter(user_id=curuser).last()
                    appoint.payment_status = "BPD"
                    appoint.save()
        finally:
            print("\n\nWE are in finally in appointpaymentload")
            try:
                print("\n\n trying to get appoint obj in appointpaymentload")
                appoint = Appointment.objects.filter(user_id=curuser).last()
                
                if appoint.photo_quantity != None:
                    #Getting Estimated Amount
                    estimateamount = getEstimatedPrice(appoint.event,appoint.location,appoint.photo_quantity)
                    try:
                        booking_amount = int(estimateamount) * 20 / 100
                    except Exception as e:
                        print("Error While Calculating Booking Amount in appointmentload: ",e)
                    #Getting Payment Object
                else:
                    estimateamount = 0
                paymobj = Payment.objects.get(pay_details_id=paydet,user_id=curuser,appoint_id=appoint,total_amount=estimateamount,payment_mode="DC")
                
                appoint.payment_status = "BPD"
                appoint.save()
            except Exception as e:
                
                print("\n\ngot error in finding payment obj in appointpaymentload: ",e)
                try:
                    print("\n\nso creating payment obj in appointpaymentload")
                    #GEtting CUrrent Appoint Obj
                    appoint = Appointment.objects.filter(user_id=curuser).last()
                    print("appoint=",appoint.event)
                    print("appoint=",appoint.location)
                    
                    if appoint.photo_quantity != None:
                        #Getting Estimated AMount
                        estimateamount = getEstimatedPrice(str(appoint.event),str(appoint.location),str(appoint.photo_quantity))
                        print(estimateamount)
                        try:
                            booking_amount = int(estimateamount) * 20 / 100
                        except Exception as e:
                            print("Error While Calculating Booking Amount in appointmentload: ",e)
                    else:
                        estimateamount = 0

                    #Creating New Payment Object
                    paymobj = Payment.objects.create(pay_details_id=paydet,user_id=curuser,appoint_id=appoint,total_amount=estimateamount,payment_mode="DC",description="Appointment Booking Payment")
                except Exception as e:
                    print("\n\nunable to create payment obj in appointpaymentload: ",e)
                    
                else:
                    print("\n\ngot paymobj obj now saving it in appointpaymentload")
                    try:
                        #Saving Payment Object
                        paymobj.save()
                    except Exception as e:
                        print("\n\nunable to save payment obj in appointpaymentload: ",e)
                    else:
                        print("paymobj saved")
                        appoint.payment_status = "BPD"
                        appoint.save()
            finally:
                try:
                    appoint = Appointment.objects.filter(user_id=curuser).last()
                    print("Appointment Obj: ",appoint)
                    print("Appointment Photo Q: ",appoint.photo_quantity)
                    if appoint.photo_quantity != None:
                        print(type(appoint.photo_quantity))
                        print("We are in Per Photo Email Send")
                        print("Appointment Photo Q: ",appoint.photo_quantity)
                        subject = "Thank You For Booking Appointment For Photoshoot"
                        email_text = "email/appointment/AppointBooked.txt"
                        email_html = "email/appointment/AppointBooked.html"
                        c = {
                            "email":curuser.userobj.email,
                            'domain':'127.0.0.1:8000',
                            'site_name': 'Photostudioroom',
                            "user": curuser,
                            "firstname":curuser.userobj.first_name,
                            "lastname":curuser.userobj.last_name,
                            'protocol': 'http',
                            }
                        email = render_to_string(email_text, c)
                        email_html = render_to_string(email_html, c)
                        email_from = "Photostudioroom <psr.gj26.github@gmail.com>"
                        try:
                            send_mail(subject, email, email_from , [curuser.userobj.email], fail_silently=False,html_message=email_html)
                        except BadHeaderError:
                            return HttpResponse('Invalid header found.')
                    else:
                        print("We are in Packages Email Send")
                        print("Appointment Photo Q: ",appoint.photo_quantity)
                        subject = "Thank You For Booking Appointment For Discussion"
                        email_text = "email/appointment/AppointBookedPkg.txt"
                        email_html = "email/appointment/AppointBookedPkg.html"
                        c = {
                            "email":curuser.userobj.email,
                            'domain':'127.0.0.1:8000',
                            'site_name': 'Photostudioroom',
                            "user": curuser,
                            "firstname":curuser.userobj.first_name,
                            "lastname":curuser.userobj.last_name,
                            "id":appoint.appoint_id,
                            "date":appoint.date,
                            "time":appoint.time,
                            "event":appoint.event,
                            "place":appoint.location,
                            'protocol': 'http',
                            }
                        email = render_to_string(email_text, c)
                        email_html = render_to_string(email_html, c)
                        email_from = "Photostudioroom <psr.gj26.github@gmail.com>"
                        try:
                            send_mail(subject, email, email_from , [curuser.userobj.email], fail_silently=False,html_message=email_html)
                        except BadHeaderError:
                            return HttpResponse('Invalid header found.')
                except Exception as e:
                    print("Error While Sending Email in appointmentForm View: ",e)

                
                
        

    return render(request,"payment/appointpaymentloading.html")

#To Edit Appointment Details
def editAppointment(request,appoint_id=None):
    appoint = None
    address = None
    appointdate = None
    msg = None
    isaddresschanged = False
    isappointmentchanged = False
    eventtype = None

    try:
        curuser = request.user  # Getting Current Logged in User
        curuser = User_Details.objects.get(userobj=curuser)
    except TypeError as e:
        print("Error while getting user object in editAppointment , Error: ", e)
    #Edit Data By Taking New Data From the Form If request.method is POST

    if request.method == "POST":
        try:
            appoint = Appointment.objects.get(appoint_id=appoint_id,user_id=curuser.user_id)  # Getting Current Appointment Obj
            address = Address.objects.get(address_id=appoint.address_id.address_id)
        except Exception as e:
            print("Error while getting appointment object in editAppointment in POST , Error: ", e)
        else:

            place = None
            service = None
            gears = None
            #eventdays = None
            #videoduration = None
            photosquantity = None
            
            try:
                eventtype = request.POST["selectevent"]
            except Exception as e:
                print("Error in Event in editAppointment: ",e)
            try:
                place = request.POST["selectplace"]
            except Exception as e:
               print("Place Not Found")
            date = request.POST["date"]
            time = request.POST["time"]
            try:
                service = request.POST["services"]
            except Exception as e:
                print("Services Not Found")
            try:
                gears = request.POST["gears"]
            except Exception as e:
                print("Gears Not Found")
    
            try:
                photosquantity = request.POST["photosquantity"]
            except Exception as e:
                print("PhotosQuantity Not Found")
        
            print(f".............Details Entered In AppointmentForm.............\nEvent: {eventtype}\nPlace: {place}\nDate: {date}\nTime: {time}\nService: {service}\nGears: {gears}\nPhotos Quantity: {photosquantity}")

            #address
            line1 = request.POST["addressline1"]
            line2 = request.POST["addressline2"]
            state = request.POST.get('selectstate', False);
            city = request.POST.get('selectcity', False);
            area = request.POST.get('selectarea',False);
            phone1 = request.POST["phone_number"]
            phone2 = request.POST["phone_number2"]
            print(city)
            print(area)
            try:
                #Trying to Get Event_Types and Location_Details Object
                if eventtype != None:
                    eventtype = Event_Types.objects.get(event_id=eventtype)
                else:
                    eventtype = False
                if place != None:
                    place = Location_Details.objects.get(location_id=place)
                else:
                    place = False
                if area != False:
                    areaobj = Area_Details.objects.get(area_id=area)
                else:
                    areaobj = False
                if city != False:
                    cityobj = City_Details.objects.get(city_id=city)
                else:
                    cityobj = False
                if state != False:
                    stateobj = State_Details.objects.get(state_id=state)
                else:
                    stateobj = False
            except Exception as e:
                print("Got error in getting eventtype and place in editAppointment: ",e)

            #Changing Address
            try:
                
                #Edit Address
                address.address_line1 = line1
                address.address_line2 = line2
                if areaobj != False:
                    address.area = areaobj
                if cityobj != False:
                    address.city = cityobj
                if stateobj != False:
                    address.state = stateobj
                address.contact_1 = phone1
                address.contact_2 = phone2
            except Exception as e:
                print("Error while changing address in editAppointment: ",e)
            else:
                try:
                    address.save()
                except Exception as e:
                    print("Error in Saving Address in editAppointment: ",e)
                else:
                    isaddresschanged = True
                
                        

            try:
                print("\nTrying to Edit appoint object in editAppointment")
                print(type(photosquantity))
                try:
                    if photosquantity == "None":
                        photosquantity = None
                except Exception as e:
                    print("Unable to convert photosquantity to None in editappointment: ",e)
                #Photoquantity is Not None, It Means User is Booking Per Photo Events
                if photosquantity != None:
                    """
                    This will create Appointment For
                    -Outdoor Photoshoot
                    -Product Photography
                    -Baby Shower
                    -Fashion
                    -Advertising
                    It Means Other Than Pre-Wedding and Wedding
                    """
                    print("This is Per Photo Booking")

                    try:    

                        #Edit Appointment
                        appoint.date = date
                        appoint.time = time
                        if place != False:
                            appoint.location = place
                        if eventtype != False:
                            appoint.event = eventtype
                        appoint.photo_quantity = photosquantity
                    except Exception as e:
                        print("Error in Changing Appoint Data in editAppointment in Per Photo Part: ",e)
                    else:
                        
                    #Getting Estimated Amount According to Entered Details
                        estimatedamount = getEstimatedPrice(eventtype.event_name,place.location_name,photosquantity)
                        print(estimatedamount)
                        try:
                            estimatedamount = int(estimatedamount)
                            booking_amount = estimatedamount * 20 / 100
                            remaining_amount = estimatedamount - booking_amount
                        except Exception as e:
                            print("Error While Calculating Booking Amount in appointmentForm: ",e)

                        try:
                            appoint.total_payment = estimatedamount
                            appoint.booking_payment = booking_amount
                            appoint.remaining_payment = remaining_amount

                            #Getting Current Time and setting it as Edited_on
                            from datetime import datetime

                            # datetime object containing current date and time
                            currentdate = datetime.now()
 
                            print("Current Date =", currentdate)

                            appoint.edited_on = currentdate
                            try:
                                appoint.save()
                            except Exception as e:
                                print("Error While Saving Appointment in editAppointment: ",e)
                            try:
                                appoint = Appointment.objects.get(appoint_id=appoint_id,user_id=curuser.user_id)  # Getting Current Appointment Obj
                                
                            except Exception as e:
                                print("Error while getting appointment object in editAppointment in POST , Error: ", e)
                            else:
                                try:
                                    paymobj = Payment.objects.get(appoint_id=appoint.appoint_id)
                                except Exception as e:
                                    print("Error While Getting Payment Object in editAppointment: ",e)
                                else:
                                    paymobj.total_amount = estimatedamount
                                    try:
                                        paymobj.save()
                                    except Exception as e:
                                        print("Error While Saving Paymobj in editAppointment: ",e)


                        except Exception as e:
                            print("Error While Saving Appointment in editAppointment for Per Photo Booking: ",e)
                        else:
                            isappointmentchanged = True


                    try:
                        booking_amount = int(estimatedamount) * 20 / 100
                    except Exception as e:
                        print("Error While Calculating Booking Amount in appointmentload: ",e)
                else: #Package 
                    
                    print("This is Package Booking")
                    if gears != None:
                        print("Videography is there in the package")
                        try:    
                            
                            #Edit Appointment
                            appoint.date = date
                            appoint.time = time
                            if place != False:
                                appoint.location = place
                            if eventtype != False:
                                appoint.event = eventtype
                            if service != None:
                                appoint.service = service
                            if gears != None:
                                appoint.gears = gears
                        except Exception as e:
                            print("Error in Changing Appoint Data in editAppointment in Package Part: ",e)
                        else:
                            #Getting Current Time and setting it as Edited_on
                            from datetime import datetime

                            # datetime object containing current date and time
                            currentdate = datetime.now()
 
                            print("Current Date =", currentdate)
                            appoint.booking_payment = 500
                            appoint.edited_on = currentdate
                            try:
                                appoint.save()
                            except Exception as e:
                                print("Error While Saving Appointment in editAppointment in Package: ",e)
                            else:
                                isappointmentchanged = True
                            
                    else:
                        """
                        This will create Appointment For
                        -Pre-Wedding and Wedding in Which Only Photography is Needed
                        """
                        print("Only Photography is selected")
                        try:    
                            
                            #Edit Appointment
                            appoint.date = date
                            appoint.time = time
                            if place != False:
                                appoint.location = place
                            if eventtype != False:
                                appoint.event = eventtype
                            if service != None:
                                appoint.service = service
                            
                        except Exception as e:
                            print("Error in Changing Appoint Data in editAppointment in Package Part in Photography Only: ",e)
                        else:
                            #Getting Current Time and setting it as Edited_on
                            from datetime import datetime

                            # datetime object containing current date and time
                            currentdate = datetime.now()
 
                            print("Current Date =", currentdate)
                            appoint.booking_payment = 500
                            appoint.edited_on = currentdate
                            try:
                                appoint.save()
                            except Exception as e:
                                print("Error While Saving Appointment in editAppointment in Package in Photo Only: ",e)
                            else:
                                isappointmentchanged = True
                            
                        
            except Exception as e:
                
                print("\n\nError to edit appoint obj in editAppointment: ",e)
            else:
                print("\n\nAppoint obj edited now saving it in editAppointment")
                #Getting Current Time and setting it as Edited_on
                from datetime import datetime

                # datetime object containing current date and time
                currentdate = datetime.now()
                print("Current Date =", currentdate)
                appoint.edited_on = currentdate
                try:
                    appoint.save()
                except Exception as e:
                    print("Error While Saving Appointment in editAppointment: ",e)

            print(f"isaddresschange: {isaddresschanged}\nisappointmentchanged: {isappointmentchanged}")
            if isaddresschanged and isappointmentchanged:
                msg = "Appointment Details Saved Successfully"
                try:
                    appoint = Appointment.objects.get(appoint_id=appoint_id,user_id=curuser.user_id)  # Getting Current Appointment Obj
                    address = Address.objects.get(address_id=appoint.address_id.address_id)
                except Exception as e:
                    print("Error while getting appointment object in editAppointment in POST , Error: ", e)
                else:
                    print("Alternative Contact: ",address.contact_2)
                    print("Length of Alternative Contact: ",len(address.contact_2))
                    print("Type of Alternative Contact: ",type(address.contact_2))
                    #send mail
                    subject = "You Have Made Changes in Your Appointment"
                    email_text = "email/appointment/AppointEdited.txt" #Make Another Template for this mail
                    email_html = "email/appointment/AppointEdited.html"
                    c = {
                                "email":curuser.userobj.email,
                                'domain':'127.0.0.1:8000',
                                'site_name': 'Photostudioroom',
                                "user": curuser,
                                "firstname":curuser.userobj.first_name,
                                "lastname":curuser.userobj.last_name,
                                "appoint":appoint,
                                "address":address,
                                'protocol': 'http',
                        }
                    email = render_to_string(email_text, c)
                    email_html = render_to_string(email_html, c)
                    email_from = "Photostudioroom <psr.gj26.github@gmail.com>"
                    try:
                        send_mail(subject, email, email_from , [curuser.userobj.email], fail_silently=False,html_message=email_html)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
            else:
                msg = "Appointment Details Not Saved,Something Went Wrong, Please Try Again!"

            #Have to convert date and time into required format
            try:
                appoint = Appointment.objects.get(appoint_id=appoint_id,user_id=curuser.user_id)  # Getting Current Appointment Obj
                address = Address.objects.get(address_id=appoint.address_id.address_id)
            except Exception as e:
                print("Error while getting appointment object in editAppointment in POST , Error: ", e)

            appointdate = appoint.date
            appointtime = appoint.time

            appointdate = appointdate.strftime("%Y-%m-%d")
            appointtime = appointtime.strftime("%H:%M")

            #Sending Basic Data
            eventtypes = Event_Types.objects.all()
            states = State_Details.objects.all()

            fivehundredphotos = []
            for i in range(5,501,5):
                fivehundredphotos.append(i)
            return render(request,"appointment/editappointmentform.html",{"appointment":appoint,"appointdate":appointdate,"appointtime":appointtime,"address":address,"curuser":curuser.userobj,"eventtypes":eventtypes,"fivehundredphotos":fivehundredphotos,"states":states,"msg":msg})
            
    #Load Appointment Data in The Form
    try:
        appoint = Appointment.objects.get(appoint_id=appoint_id,user_id=curuser.user_id)  # Getting Current Appointment Obj
        
    except Exception as e:
        print("Error while getting appointment object in editAppointment , Error: ", e)
    else:
        try:
            address = Address.objects.get(address_id=appoint.address_id.address_id)
        except Exception as e:
            print("Address not found in editAppointment it means It is a Package Service: ",e)
        #Have to convert date and time into required format
        import datetime
        appointdate = appoint.date
        appointtime = appoint.time

        appointdate = appointdate.strftime("%Y-%m-%d")
        appointtime = appointtime.strftime("%H:%M")

        #Sending Basic Data
        eventtypes = Event_Types.objects.all()
        states = State_Details.objects.all()

        fivehundredphotos = []
        for i in range(5,501,5):
            fivehundredphotos.append(i)
        return render(request,"appointment/editappointmentform.html",{"appointment":appoint,"appointdate":appointdate,"appointtime":appointtime,"address":address,"curuser":curuser.userobj,"eventtypes":eventtypes,"fivehundredphotos":fivehundredphotos,"states":states})

#To Delete Appointment From User Profile
def deleteAppointment(request,appoint_id):
    curuser = None
    try:
        curuser = request.user  # Getting Current Logged in User
        curuser = User_Details.objects.get(userobj=curuser)
    except TypeError as e:
        print("Error while getting user object in deleteAppointment , Error: ", e)
    try:
        print("in try of appointment")
        appoint = Appointment.objects.get(appoint_id=appoint_id)
    except Exception as e:
        print("\n\nunable to get appoint obj in deleteAppointment: ",e)
        return JsonResponse({"status": "failed"}, status=500)
    else:
        print("cancelling appoint")
        appoint.appoint_status = False

        #Getting Current Time and setting it as cancelled_on
        from datetime import datetime

        # datetime object containing current date and time
        currentdate = datetime.now()
        print("Current Date =", currentdate)
        appoint.cancelled_on = currentdate
        try:
            appoint.save()
        except Exception as e:
            print("Error While Saving Appointment Obj in deleteAppointment: ",e)
            return JsonResponse({"status": "failed"}, status=500)
        else:
            try:
                print("in try of appointment")
                appoint = Appointment.objects.get(appoint_id=appoint_id)
                
            except Exception as e:
                print("\n\nunable to get appoint obj in deleteAppointment: ",e)
                return JsonResponse({"status": "failed"}, status=500)
            try:
                address = Address.objects.get(address_id=appoint.address_id.address_id)
            except Exception as e:
                print("Unable to get address obj in deleteappointment it means it is package booking: ",e)
                address = None

        
            #Send Mail
            subject = "You Have Cancelled Your Appointment"
            email_text = "email/appointment/AppointCancelled.txt" #Make Another Template for this mail
            email_html = "email/appointment/AppointCancelled.html"
            c = {
                    "email":curuser.userobj.email,
                    'domain':'127.0.0.1:8000',
                    'site_name': 'Photostudioroom',
                    "user": curuser,
                    "firstname":curuser.userobj.first_name,
                    "lastname":curuser.userobj.last_name,
                    "appoint":appoint,
                    "address":address,
                    'protocol': 'http',
                }
            email = render_to_string(email_text, c)
            email_html = render_to_string(email_html, c)
            email_from = "Photostudioroom <psr.gj26.github@gmail.com>"
            try:
                send_mail(subject, email, email_from , [curuser.userobj.email], fail_silently=False,html_message=email_html)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            
        return JsonResponse({"status": "done"}, status=200)
    
    
def load_places(request):
    print("load places called")
    locationids = []
    places = []
    #Getting Eventype Selected By The User
    eventtype = request.GET["event"]
    print("Got Event From AJAX: ",eventtype)
    #Getting All The Even_Location_Details Object Which Has Selected EventType
    eventlocdets = Event_Location_Details.objects.filter(event_id=eventtype)
    print("Event Location Details : ",eventlocdets)

    #Getting Every eventlocation details and adding its ids to locationids list 
    for eventlocdet in eventlocdets:
        print("Event Location: ",eventlocdet)
        print("Event Location Location id: ",eventlocdet.location_id)
        print("Event Location Location id Location id: ",eventlocdet.location_id.location_id)
        locationids.append(eventlocdet.location_id.location_id)
    print("Location Ids: ",locationids)

    #Getting Every Location id and Getting Location_Details Object From it and appending Them to Places list
    for locationid in locationids:
        tempplaces = Location_Details.objects.get(location_id=locationid)
        places.append(tempplaces)
    print("Places: ",places)
    
    return render(request, 'ajax/locationload.html', {'places': places})

#To Show Packages Page
def showPackages(request):
    events = None
    try:
        events = Event_Types.objects.all()
    except Exception as e:
        print("Error While GEtting Events in showPackages: ",e)
    return render(request,"appointment/packages.html",{"events":events})