from PIL.Image import Image
from django.contrib.auth import tokens
from django.http import request
from django.http.response import BadHeaderError, HttpResponse, JsonResponse
from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from Appointment.models import Appointment, User, User_Details
from django.contrib.auth import authenticate, login, logout
from Appointment.models import *
from django.conf import settings
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

#PHOTOSTUDIOROOM OFFICIAL PAYMENT DETAILS 
PSR_PAY_DET_ID = 1
PSR_PAY_CARD_NO = 75686783467666
PSR_PAY_CARD_HOLDER_NAME = "Photostudioroom"
PSR_PAY_CARD_EXPIRY_DATE = "2022-12-31"

# Create your views here.
def index(request):
    return render(request,"main/index.html",{"ishomeactive":"class=active id=active"}) #ishomeactive for nav bar to set orange bg in navbar,id as active to get orange color back when scroll up 

def login_page(request,nextpage=None):
    print(nextpage)
    
    print("login called")
    notif = {"msg":""}
    notif['nextp'] = f'{nextpage}'
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request,username=username, password=password)
        if user is not None:
            

            login(request, user)
            if(user.is_contributor):
                return redirect("/stockimages")
    
            else:
                if nextpage == None:
                    return redirect("/appointment")
                else:
                    if 'appointment' in nextpage:
                        return redirect('/appointment/appointment-form')
                    elif 'stockimages' in nextpage:
                        return redirect('/stockimages')

                
            #notif["msg"] = f"Login Successfully, Welcome {user.get_username()}"
            
        else:
            notif["msg"] = "Login Failed - Username/Password is Incorrect"
    print(notif)
    print("rendering login page")
    return render(request,"main/login.html",notif)

def logout_page(request):
    logout(request)
    return render(request,"main/login.html",{"msg":"You're Logged Out"})

def register_cust(request):
    notif = {"msg":"",'usertype':"Customer"}
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")

        try:

            user = User.objects.create_user(username, email, password)
            user.first_name = firstname
            user.last_name = lastname
            user.is_customer = True


            customer = User_Details.objects.create(userobj=user)
        except Exception as e:
            print(e)
        else:
            print("IN ELSE")
            user.save()
            customer.save()
            print("ELSE DONE")
            subject = 'Welcome to Photostudioroom'
            email_text = "email/main/register/newregister.txt"
            email_html = "email/main/register/newregister.html"
            c = {
                    "email":customer.userobj.email,
                    'domain':'127.0.0.1:8000',
                    'site_name': 'Photostudioroom',
                    "user": customer,
                    "firstname":customer.userobj.first_name,
                    "lastname":customer.userobj.last_name,
                    'protocol': 'http',
                }
            email = render_to_string(email_text, c)
            email_html = render_to_string(email_html, c)
            email_from = "Photostudioroom <psr.gj26.github@gmail.com>"
            try:
                send_mail(subject, email, email_from , [customer.userobj.email], fail_silently=False,html_message=email_html)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            
        notif["msg"] = f"Registered Successfully"
        return redirect("/login")
        
    return render(request,"main/register.html",notif)

def register_cont(request):
    notif = {"msg":"",'usertype':"Contributor"}
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")

        


        try:

            user = User.objects.create_user(username, email, password)
            user.first_name = firstname
            user.last_name = lastname
            user.is_contributor = True
            user.save()
            
            contributor = User_Details.objects.create(userobj=user)
            contributor.save()
        except Exception as e:
            print(e)
        else:
            print("IN ELSE")
            
            print("ELSE DONE")
            subject = 'Welcome to Photostudioroom'
            email_text = "email/main/register/newregister.txt"
            email_html = "email/main/register/newregister.html"
            c = {
                    "email":contributor.userobj.email,
                    'domain':'127.0.0.1:8000',
                    'site_name': 'Photostudioroom',
                    "user": contributor,
                    "firstname":contributor.userobj.first_name,
                    "lastname":contributor.userobj.last_name,
                    'protocol': 'http',
                }
            email = render_to_string(email_text, c)
            email_html = render_to_string(email_html, c)
            email_from = "Photostudioroom <psr.gj26.github@gmail.com>"
            try:
                send_mail(subject, email, email_from , [contributor.userobj.email], fail_silently=False,html_message=email_html)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
        
        notif["msg"] = f"Registered Successfully"
        return redirect("/login")
        
    return render(request,"main/register.html",notif)

def register_home(request):
    return render(request,"main/register_home.html")

def checkUsername(request):
    # request should be ajax and method should be GET.
    if request.is_ajax and request.method == "GET":
        # get the username from the client side.
        username = request.GET.get("username", None)
        # check for the username in the database.
        if User.objects.filter(username = username).exists():
            # if username found return not valid
            return JsonResponse({"valid":False}, status = 200)
        else:
            # if username not found, then user can create a new user with this username
            return JsonResponse({"valid":True}, status = 200)

    return JsonResponse({}, status = 400)

def about(request):
    return render(request,"main/about.html",{"isaboutactive":"class=active id=active"}) #isaboutactive for nav bar to set orange bg in navbar,id as active to get orange color back when scroll up 

def temp(request):
    return render(request,"main/base.html")

#Showing Profile to User
def showProfile(request):
    if request.user.is_authenticated:
        address = None
        status = None
        old = None
        curuser = None
        msg = ""
        appointments = None
        cancelledappointments = None
        images = None
        try:
            #Getting Status From URL if Status is true it means some data is changed by user(personal or password is changed)
            status = request.GET["status"]
        except Exception as e:
            print("\n\nnothing got in status from url in showProfile: ",e)
    
        try:
            #Getting Old Variable From URL if Old is true it means old password matched and can be changed
            old = request.GET["old"]
        except Exception as e:
            print("\n\nnothing got in old from url in showProfile: ",e)

        if status == "True":#it means some details is changed and this is got from updatePersonal view or updatePassword View
            print(True)
            msg = "Details Saved Successfully" #Send Message and Display it
        elif status == "False":#it means some details is not changed(got some error whjile changing details) and this is got from updatePersonal view or updatePassword View
            msg = "Details Not Saved!, Something Went Wrong!!"
            print(False)
        if old == "True":#it means old password matched so don't show any error(blank msg) and this is got from  updatePassword View
            msg = ""
        elif old == "False":#it means old password didn't match so show error and this is got from updatePassword View
            msg = "Old Password Did Not Match!!"
    


    
        try:
            print("is user auth: ",request.user.is_authenticated)
            if request.user.is_authenticated:  # if user is logged in
                curuser = request.user  # then get Current Logged in User
                curuser = User_Details.objects.get(
                                userobj=curuser)  # need user_Details object
            
        except Exception as e:
            print("Error While Getting User Object in showProfile View: ",e)

        try:
            print(type(curuser.address_id))
            #Getting Address Object to Display
            address = Address.objects.get(address_id=int(str(curuser.address_id)))
        except Exception as e:
            print("Not Found Address in SHow Profile()")
            print(e)
        #Getting All the States
        states = State_Details.objects.all()

        
        try:
            #Trying to get appointments to display in profile
            appointments = Appointment.objects.filter(user_id=curuser,appoint_status=True)
            cancelledappointments = Appointment.objects.filter(user_id=curuser,appoint_status=False)
            """
            totalamount = []
            for appointment in appointments: #For Every Appointment Of Current User
                payment = Payment.objects.filter(appoint_id=appointment.appoint_id) #Get Payment Object Of it
                for paym in payment: #For Every Payment For Current Appointment
                    totalamount.append(paym.total_amount)  #Add Total Amount in Total AMount List
            """
        except Exception as e:
            print("In Show Profile for appointment",e)
        try:
            #GEtting Order Object to Display Purchased Images in Profile
            orders = Order.objects.filter(user_id=curuser)
            print("orders",orders)
            imageobjs = [] #This will COntains All the image objects of current user's purchases
            imageids = []
            for order in orders: #For Every Order
                print(order)
                #GEt Order Details Obj
                orderdets = Order_Details.objects.filter(order_id=order)
                for orderdet in orderdets: #For Every Order Details
                    imageobjs.append(orderdet.image_id) #Get its Image id and append in imageobjs
            for imageid in imageobjs: #Getting Imageids of every image object from imageobjs
                print(imageid.image_id)
                imageids.append(imageid.image_id) #Appending image ids to imageids list
            print(imageobjs)
            print(imageids)
            images  = Images.objects.in_bulk(imageids) #Getting all the image's objects from imageids list
            print(images)
        except Exception as e:
            print("Error While Getting Order Object or order details object in showProfle View line 234: ",e)
        

        return render(request,"main/profile.html",{"curuser":curuser,"address":address,"msg":msg,"states":states,"appointments":appointments,"cancelledappointments":cancelledappointments,"images":images})
    else:
        notif = {}
        notif["msg"] = "Password Changed Successfully, Please Login Again."
        return render(request,"main/login.html",notif)

def updatePersonal(request):
    status = False
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        print(username)
        print(email)

        try:
            
            user = User.objects.get(id=request.user.id)
            if firstname != "":
                user.first_name = firstname
            if lastname != "":
                user.last_name = lastname
            if username != "":
                user.username = username
            if email != "":
                user.email = email
        
        except Exception as e:
            print(e)
        else:
            pass
            msg = True
            user.save()
            
        
    
    return redirect(f"/profile?status={msg}")

def updatePassword(request):
    ispasscorrect = False
    
    msg = False
    if request.method == "POST":
        oldpassword = request.POST.get("oldpassword")
        newpassword = request.POST.get("newpassword")
        
        try:
            
            user = User.objects.get(id=request.user.id)
            if oldpassword != "":
                ispasscorrect = user.check_password(oldpassword)

            if ispasscorrect:
                user.set_password(newpassword)
            else:
                return redirect(f"/profile?old={msg}")
        
        except Exception as e:
            print(e)
        else:
            pass
            msg = True
            user.save()
            try:
                subject = 'Password Changed!'
                email_text = "email/main/password/passwordchanged.txt"
                email_html = "email/main/password/passwordchanged.html"
                c = {
                    "email":user.email,
                    'domain':'127.0.0.1:8000',
                    'site_name': 'Photostudioroom',
                    "user": user,
                    "firstname":user.first_name,
                    "lastname":user.last_name,
                    'protocol': 'http',
                }
                email = render_to_string(email_text, c)
                email_html = render_to_string(email_html, c)
                email_from = "Photostudioroom <psr.gj26.github@gmail.com>"
                try:
                    send_mail(subject, email, email_from , [user.email], fail_silently=False,html_message=email_html)
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
                
            except Exception as e:
                print(e)
            
            
        
    
    return redirect(f"/profile?status={msg}")
    

def updateAddress(request):

    print("We are in updateaddress\n\n")
    msg = False
    if request.method == "POST":
        print("We are in request post\n\n")
        addressline1 = request.POST.get("addressline1")
        addressline2 = request.POST.get("addressline2")
        state = request.POST['selectstate'] 
        city = request.POST['selectcity'] 
        area = request.POST['selectarea'] 
        contact1 = request.POST.get('contact1')
        contact2 = request.POST.get('contact2')
        
        stateobj = State_Details.objects.get(state_id=state)
        cityobj = City_Details.objects.get(city_id=city)
        areaobj = Area_Details.objects.get(area_id=area)
        print(f"add1={addressline1}\n\n add2={addressline2}\n\nstate={state}\n\ncity={city}\n\narea={area}\n\ncontact1={contact1}\n\ncontact2={contact2}\n\nstateobj={stateobj}\n\ncityobj={cityobj}\n\nareaobj={areaobj}")
        try:
            
            user = User.objects.get(id=request.user.id)
            user_det = User_Details.objects.get(userobj=user)
            if user_det.address_id == None: #if userdetails table has no address id data for current user
                print("We are in user address id is none\n\n")

                try:#Check if address table is already having same data
                    print("We are in try 1\n\n")
                    address = Address.objects.get(address_line1=addressline1,address_line2=addressline2,area=areaobj,city=cityobj,state=stateobj,contact_1=contact1,contact_2=contact2)
                except Exception as e: #If Not 
                    print("We are in exception of address.get()\n\n")
                    print(e)
                    try: #Try To Create a new Object
                        address = Address.objects.create(address_line1=addressline1,address_line2=addressline2,area=areaobj,city=cityobj,state=stateobj,contact_1=contact1,contact_2=contact2)
                    except Exception as e:
                        print(e)

                finally:#Finally save address table, add addressid in userdetails table and save it also
                    print("We are in finally address.get()\n\n")
                    msg = True
                    address.save()
                    user_det.address_id = address
                    user_det.save()
                    print("data saved")

                    
                
            else: #if user details is already having data
                print("We are in user address id is not none\n\n")
                try:#then get address object and update values
                    print("we are in try 2")
                    address = Address.objects.get(address_id=int(str(user_det.address_id)))
                    address.address_line1 = addressline1
                    address.address_line2 = addressline2
                    address.area = areaobj
                    address.city = cityobj
                    address.state = stateobj
                    address.contact_1 = contact1
                    address.contact_2 = contact2
                    
                except Exception as e:
                    print("We are in exception of address.get() 2\n\n")
                    print(e)
                else: #if no errors then save it
                    print("We are in else of 2\n\n")
                    msg = True
                    address.save()
        except Exception as e:
            print("We are in main exception\n\n")
            print(e)

        
    return redirect(f"/profile?status={msg}")

def uploadProfilePhoto(request):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(id=request.user.id)
            user_det = User_Details.objects.get(userobj=user)
        except Exception as e:
            print(e)
        else:
            if request.method == 'POST':
                if request.is_ajax():
                    try:
                        profilephoto = request.FILES.get('srcval')
                        print(profilephoto)
                       
                      
                    except Exception as e:
                        print(e)
 
        return JsonResponse({"uploaded":"true"}, status = 200)
    
def uploadprofilephototemp(request):
    msg = False
    from django.core.files.storage import FileSystemStorage
    print("outside")
    if request.method == 'POST':
        print("inside")
        myfile = request.FILES['profileimage']
        print(myfile)
        if request.user.is_authenticated:
            try:
                user = User.objects.get(id=request.user.id)
                user_det = User_Details.objects.get(userobj=user)
            except Exception as e:
                print(e)
            else:
                username = user.username
        
        fs = FileSystemStorage()
        filename = fs.save(f"stockimages/profile/photos/{username}/{myfile.name}", myfile)
        uploaded_file_url = fs.url(filename)
     
        try:
            user_det.profile_photo = f"stockimages/profile/photos/{username}/{myfile.name}"

        except Exception as e:
            print(e)
        else:
            msg = True
            user_det.save()
        #return render(request, 'core/simple_upload.html', {'uploaded_file_url': uploaded_file_url})
    #return render(request, 'core/simple_upload.html')
    
    return redirect(f"/profile?status={msg}")



def forgotPassword(request):
    msg = None
    if request.method == "POST":
        username = request.POST.get("username")
        try:
            user = User.objects.get(username=username)
        except Exception as e:
            print(e)
            return render(request,"passwordreset/password_reset.html",{"msg":"User Not Found!, Please Check Username You Have Entered"})

        else:
            subject = "Password Reset Requested"
            email_template_name = "email/main/password/password_reset_email.txt"
            email_html = "email/main/password/password_reset_email.html"
            c = {
                "email":user.email,
                'domain':'127.0.0.1:8000',
                'site_name': 'Photostudioroom',
                "uid": urlsafe_base64_encode(force_bytes(user.id)),
                "user": user,
                "firstname": user.first_name,
                "lastname": user.last_name,
                "username":user.username,
                'token': default_token_generator.make_token(user),
                'protocol': 'http',
                }
            email = render_to_string(email_template_name, c)
            email_html = render_to_string(email_html, c)
            email_from = "Photostudioroom <psr.gj26.github@gmail.com>"
            try:
                send_mail(subject, email, email_from , [user.email], fail_silently=False,html_message=email_html)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect ("/password_reset/done/")
    
    return render(request,"passwordreset/password_reset.html")


def resetConfirm(request,token=None,uidb64=None,username=None):
    print("Token : ",token)
    print("uidb64: ",uidb64)
    print("username: ",username)
    if request.method == "POST":
        print("method is post in reset confirm")
        newpassword = request.POST.get("newpassword")
        print(newpassword)
        if username != None:
            try:
                print("username is not none in reset confirm")
                user = User.objects.get(username=username)

                print("Token : ",token)
                print("uidb64: ",uidb64)

                user.set_password(newpassword)
           
        
            except Exception as e:
                print(e)
            else:
            
                user.save()
            try:
                subject = 'Password Reset Successfully!'
                email_text = "email/main/password/passwordchanged.txt"
                email_html = "email/main/password/passwordchanged.html"
                c = {
                    "email":user.email,
                    'domain':'127.0.0.1:8000',
                    'site_name': 'Photostudioroom',
                    "user": user,
                    "firstname":user.first_name,
                    "lastname":user.last_name,
                    'protocol': 'http',
                }
                email = render_to_string(email_text, c)
                email_html = render_to_string(email_html, c)
                email_from = "Photostudioroom <psr.gj26.github@gmail.com>"
                try:
                    send_mail(subject, email, email_from , [user.email], fail_silently=False,html_message=email_html)
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
            except Exception as e:
                print(e)
            return redirect('/reset/done/')
    return render(request,"passwordreset/password_reset_confirm.html",{'uidb64':uidb64,'token':token,'username':username})

def resetComplete(request):
    return render(request,'passwordreset/password_reset_complete.html')

"""
def resetDone(request):
    return render(request,"passwordreset/password_reset_done.html")

def resetConfirm(request):
    return render(request,"passwordreset/password_reset_confirm.html")

def resetComplete(request):
    return render(request,"passwordreset/password_reset_complete.html")
"""
#For AJAX(Dropdowns)
def load_cities(request):
    print("load states called")
    state_id = request.GET.get('state')
    cities = City_Details.objects.filter(state_id=state_id).order_by('city_name')
    return render(request, 'ajax/cityload.html', {'cities': cities})

def load_areas(request):
    print("load areas called")
    city_id = request.GET.get('city')
    areas = Area_Details.objects.filter(city_id=city_id).order_by('area_name')
    return render(request, 'ajax/areaload.html', {'areas': areas})


    
def temp(request):
    from django.core.mail import send_mail
    from django.template.loader import render_to_string

    msg_plain = render_to_string('email.txt', {'username': request.user.username})
    msg_html = render_to_string('email.html', {'username': request.user.username})

    send_mail(
        'Sending HTML',
        msg_plain,
        "Photostudioroom <psr.gj26.github@gmail.com>",
        [request.user.email],
        html_message=msg_html,
    )

    return HttpResponse("Sent")



#Testing Email Formatting - TEMP
def testEmailFormat(request):
    
        
        try:
            user = request.user
        except Exception as e:
            print(e)
        else:
            
                
                
                

            subject = "Testing Email Formatting For PSR"
            email_text = "email.txt"
            email_html = "email.html"
            c = {
                "email":user.email,
                'domain':'127.0.0.1:8000',
                'site_name': 'Photostudioroom',
                "user": user,
                "username":user.username,
                'protocol': 'http',
                }
            email = render_to_string(email_text, c)
            email_html = render_to_string(email_html, c)
            email_from = "Photostudioroom <psr.gj26.github@gmail.com>"
            try:
                send_mail(subject, email, email_from , [user.email], fail_silently=False,html_message=email_html)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            
        return HttpResponse("OK Done I Guess")
    
def help(request):
    return render(request,"main/help.html",{"ishelpactive":"class=active id=active"})

"""
This Will Load First Admin Page Where Admin Can See Contributor's Earnings also Admin Can Pay,
And Also Admin Can Visit Django Admin Panel From This Page.
"""
def showAdminHome(request,success=None):
    #For Giving Payment to The Contributor Every Month
    curuser = None
    users = []
    userids = []
    msg = None
    
    print(type(success))
    if request.user.is_authenticated:
        try:
            usersobj = User.objects.filter(is_contributor=True)
            print(usersobj)
            for user in usersobj:
                users.append(user)
            for user in users:
                curuser = User_Details.objects.get(userobj =user)
                userids.append(curuser.user_id)

            curuser = User_Details.objects.in_bulk(userids)

        except Exception as e:
            print("Error While Getting User Obj in showAdminHome",e)
    if success != None:
        if success == True or success == "True":
            msg = "Payment Paid to The Contributor."
        elif success == False or success == "False":
            print(False)
            msg = "Payment Already Paid!!"

        
    return render(request,"main/contpayforadmin.html",{"isadminhomeactive":"class=active id=active","curuser": curuser,"msg":msg})


"""
This Will Show Details Of a Particular Contributor Like How Much He Has Earned From How Many Images and Also How Much Payment is Remaining To Pay
"""
def showContWiseData(request,contid=None):
    print("In showContWiseData")
    print("Contid Got From URL: ",contid)
    if contid != None:
        rem_cont_pay = None
        rem_cont_det_pay = None
        unpaidimageids = []
        paidimageids = []
        paidimagesdict = {}
        paidearningstotalamount = 0
        unpaidimagesdict = {}
        unpaidearningstotalamount = 0
        curuser = None
        contpaydet = None
        imageids = []
        images = None
        contpay = None
        totalEarned = 0
        totalearningsfromcontpay = 0
        unpaidearnings = {}
        unpaidearningsonly = 0

        print("Contid is not none..")
        
        if request.user.is_authenticated:
            print("User is Authenticated")
            try:
                
                curuser = User_Details.objects.get(user_id=contid)
            except Exception as e:
                print("Error While Getting User Obj in showContWiseData in StockImages",e)

            try:
                #Getting ContPay Obj If Available
                contpay = Contributor_Payment.objects.filter(user_id=curuser)
            except Exception as e:
                    
                print("Error While Getting Cont Pay in showContWiseData: ",e)
            print("Contpay: ",contpay)
            if contpay:
                for contp in contpay:
                    paidearningstotalamount += contp.total_amount
                    try:
                        contpaydet = Contributor_Payment_Details.objects.filter(cont_pay_id=contp)
                    except Exception as e:
                        print("Error While Getting Cont Pay Det in showContWiseData: ",e)
                    if contpaydet:
                        for contpd in contpaydet:
                            try:
                                imagesobj = Images.objects.filter(image_id=contpd.image_id.image_id)
                            except Exception as e:
                                print("Error While Getting Imagesobj in showContWiseData: ",e)
                            if imagesobj:
                                for imageobj in imagesobj:
                                    paidimagesdict[imageobj.image_id] = contpd.id

                        for imageid,contpd_id in paidimagesdict.items():
                            print("Inside PaidImagesDict Loop")
                            print("imageid: ",imageid)
                            print("contpd_id: ",contpd_id)
                            paidimageids.append(imageid)

            try:
                rem_cont_pay = Remaining_Contributor_Payment.objects.filter(user_id=curuser)
            except Exception as e:
                print("Error While Getting rem cont pay in showContWiseData: ",e)
            if rem_cont_pay:
                
                    for rem_pay in rem_cont_pay:
                        unpaidearningstotalamount += rem_pay.total_amount
                        try:
                            rem_cont_det_pay = Remaining_Contributor_Payment_Details.objects.filter(rem_cont_pay_id=rem_pay)
                        except Exception as e:
                            print("Error While Getting rem cont det pay in showContWiseData: ",e)
                        if rem_cont_det_pay:
                            for rem_det in rem_cont_det_pay:
                                print("Trying to get imageobjs")
                                try:
                                    imageobjs = Images.objects.filter(image_id=rem_det.image_id.image_id)
                                except Exception as e:
                                    print("Error While Getting Imageobjs in showContWiseData: ",e)
                                if imageobjs:
                                    print("Got imageobjs")
                                    print("Running Imageobjs Loop")
                                    for imageobj in imageobjs:
                                        unpaidimagesdict[imageobj.image_id] = rem_det.id
                                    
                    #Get Images From unpaidimagesdict and send to template
                    print("Will Run UnpaidImagesIds Loop")
                    for imageid,rem_det_id in unpaidimagesdict.items():
                        print("Inside UnpaidImagesDict Loop")
                        print("imageid: ",imageid)
                        print("rem_det_id: ",rem_det_id)
                        unpaidimageids.append(imageid)
                    print("Will Run paidImagesIds Loop")
                    
                    
                    
                


                    


            """
            #Get All The Approved Images Uploaded By Current Contributor

            try:
                #Getting Images of Current Contributor Which Are Approved
                images = Images.objects.filter(user_id=curuser.user_id,status="A")
            except Exception as e:
                print("Error While Getting Images in paymentForContAuto: ",e)
            else:#If Image Found
                
                print("Images: ",images)
                #Calculate Total Earnings
                try:
                    #Getting ContPay Obj If Available
                    contpay = Contributor_Payment.objects.filter(user_id=curuser)
                except Exception as e:
                    
                    print("Error While Getting Cont Pay in showContWiseData: ",e)
                else:
                    #Checking if ContPay is Null
                    if len(contpay) <= 0:
                        #Then Directly Pay For The Contributor
                        return paymentForContAuto(request,username=curuser.userobj.username)
                    print("Contpay: ",contpay)
                    for contp in contpay:
                        print("contp: ",contp)
                        print("cont.total_amount: ",contp.total_amount)
                        print("total_earningsfromcontpay before: ",totalearningsfromcontpay)
                        totalearningsfromcontpay += contp.total_amount
                        print("total_earningsfromcontpay after: ",totalearningsfromcontpay)
                        for image in images:
                            print(image.downloads)
                            if image.downloads > 0:
                                try:
                                    contpaydet = Contributor_Payment_Details.objects.filter(image_id=image)
                                except Exception as e:
                                    print("Error While Getting contpaydet in showContWiseData: ",e)
                                else:
                                    print(len(contpaydet))
                                    if len(contpaydet) <= 0: #It Means For This Image Payment is Never Done
                                        print("It is none")
                                        totalunpaidearnings = image.downloads * image.price
                                        totalunpaidearnings = totalunpaidearnings * 70 / 100
                                        try:
                                            unpaidearnings[image.image_id] += totalunpaidearnings
                                        except Exception as e:
                                            print(e)
                        #Calculate UnPaid Earnings For Images Which Payment Has Been Already Paid
                        try:
                            contpaydet = Contributor_Payment_Details.objects.filter(cont_pay_id=contp)
                        except Exception as e:
                            print("Error While Getting contpaydet in showContWiseData: ",e)
                        else:
                            for contpd in contpaydet:
                                if contpd.image_id.image_id not in imageids:
                                    imageids.append(contpd.image_id.image_id)
                                
                                print("contpaydet image id: ",contpd.image_id.image_id)
                                print("contpaydet downloads when paid: ",contpd.downloads_when_paid)
                                print("contpaydet image downloads: ",contpd.image_id.downloads)
                                if contpd.image_id.downloads > contpd.downloads_when_paid:
                                    actualdownloads = contpd.image_id.downloads - contpd.downloads_when_paid
                                    actualamount = actualdownloads * contpd.image_id.price
                                    try:
                                        unpaidearnings[contpd.image_id.image_id] += actualamount
                                    except Exception as e:
                                        print(e)

                                    print("Actual Downloads: ",actualdownloads)
                                    print("Actual Amount: ",actualamount)
                                    print("UnpaidEarnings: ",unpaidearnings)
                                else:
                                    try:
                                        unpaidearnings[contpd.image_id.image_id] = 0
                                    except Exception as e:
                                        print(e)
                                
            unpaidearningsonly = 0
            for key,value in unpaidearnings.items():
                unpaidearningsonly += value
            totalEarned = totalearningsfromcontpay + unpaidearningsonly
            try:
                totalEarned = int(totalEarned)
                totalearningsfromcontpay = int(totalearningsfromcontpay)
                unpaidearningsonly = int(unpaidearningsonly)
            except Exception as e:
                print("Unable to Convert Amount in Int: ",e)
            """
            totalEarned = paidearningstotalamount + unpaidearningstotalamount
    try:
        paidimages = Images.objects.in_bulk(paidimageids)
    except Exception as e:
        print("Error While Getting Images Objects in showContWiseData: ",e)
    try:
        unpaidimages = Images.objects.in_bulk(unpaidimageids)
    except Exception as e:
        print("Error While Getting Images Objects in showContWiseData: ",e)

    print("Converting All The Amounts to Int")
    try:
        unpaidearningstotalamount = int(unpaidearningstotalamount)
        paidearningstotalamount = int(paidearningstotalamount)
        totalEarned = int(totalEarned)
    except Exception as e:
        print("Error While Converting Variables into int in showCOntWiseData..")
    print("Final...")
    print("paidimageids: ",paidimageids)
    print("paidEarnings: ",paidimagesdict)
    print("paidimages: ",paidimages)
    
    print("UnpaidEarnings: ",unpaidimagesdict)
    print("UnpaidEarningsonly: ",unpaidearningstotalamount)
    print("totalEarned: ",totalEarned)
    print("totalearningsfromcontpay: ",paidearningstotalamount)
    return render(request,"main/showcontwisedata.html",{"isadminhomeactive":"class=active id=active","curuser":curuser,"totalearnings":paidearningstotalamount,"unpaidearnings":unpaidearningstotalamount,"totalearned":totalEarned,"remcontpay":rem_cont_pay,"contpaydet":contpaydet,"paidimages":paidimages,"unpaidimages":unpaidimages})

"""
This Will Load Payment Page For Admin Which Will Be Used To Pay Payment To The Contributors
"""
def loadPaymentPageForContPayment(request,contid=None,totalpayment=None):
    curuser = None
    try:
        curuser = User_Details.objects.get(user_id=contid)
    except Exception as e:
        print("Error While Getting userdet obj in loadPaymentPageForContPayment: ",e)

    return render(request,"payment/contpayfromadmin.html",{"paymentamount":totalpayment,"curuser":curuser})
    

"""
Actual Function Which Will be Used To Pay Payment To The Contributor
"""
#For Giving Payment to The Contributor Every Month
def paymentForContAuto(request,contid=None,totalpayment=None,username=None):
    print("In paymentForContAuto")
    ispaymentpaid = None
    totalamount = 0
    curuser = None
    iseveryalreadypaid = True
    unpaidtotal = 0
    msg = None
    if request.user.is_authenticated:
        try:
            user = User.objects.get(username=username)
            curuser = User_Details.objects.get(userobj = user)
        except Exception as e:
            print("Error While Getting User Obj in paymentForContAuto in Main",e)

        #Getting Remaining Cont Pay Obj

        try:
            rem_pay_obj = Remaining_Contributor_Payment.objects.filter(user_id=curuser)
        except Exception as e:
            print("Error While Getting Rem Pay Obj in paymentForContAuto in Main: ",e)
        
            

        if rem_pay_obj:
            print("\nGot RemPayObj....")
            print("Rem Pay Obj: ",rem_pay_obj)
            #For Every Rem Cont Pay Obj
            for rem_obj in rem_pay_obj:
                print("For Every RemPayObj....")
                print("Rem Obj in RemPayObj: ",rem_obj)
                try:
                    #GEtting REm Pay Det Obj
                    rem_pay_det_obj  = Remaining_Contributor_Payment_Details.objects.filter(rem_cont_pay_id=rem_obj)
                except Exception as e:
                    print("Error While Getting Rem Pay Det Obj in paymentForContAuto in Main: ",e)
                if rem_pay_det_obj:
                    print("\nGot RemPayDetObj....")
                    print("Rem Pay Det Obj: ",rem_pay_det_obj)
                    #For Every Rem Cont Pay Det Obj
                    for rem_det_obj in rem_pay_det_obj:
                        print("\For Every RemDetObj in RemPayDetObj....")
                        print("Rem Det Obj: ",rem_det_obj)
                        #Getting Image Object
                        try:
                            imageobj = Images.objects.get(image_id=rem_det_obj.image_id.image_id)
                        except Exception as e:
                            print("Error While Getting Image Obj in paymentForContAuto: ",e)
                        else:
                            print("Imageobj: ",imageobj)
                            try:#Getting PayDetObj Of PSR From Which THe Payment Will Be Paid
                                pay_det = Payment_Details.objects.get(pay_details_id=PSR_PAY_DET_ID)
                            except Exception as e:
                                print("Error While Getting Payment Details Obj in paymentForContAuto: ",e)
                            else:#If Payment Det Obj Found(Rare case if not found)
                                print("Payment Details: ",pay_det)
                                #Try to Find ContPay Obj For Current Contributor
                                try:
                                    contpay = Contributor_Payment.objects.get(user_id=curuser)
                                except Exception as e:
                                    print("Error While Getting Cont Pay Obj in paymentForContAuto: ",e)
                                    print("Not Found COntpay So Creating")
                                    try:#Then Create a ContPay Object With Pay_Det_id and Total_amount as 0
                                        contpay = Contributor_Payment.objects.create(pay_details_id=pay_det,total_amount=totalamount,user_id=curuser)
                                    except Exception as e:
                                        print("Error While Creating COntributor Payment Details: ",e)
                                finally:#Found
                                    print("COnt Pay Obj: ",contpay)
                                    #Then Try to Get Cont_Pay_Details Obj
                                    try:
                                        contpaydet = Contributor_Payment_Details.objects.filter(cont_pay_id=contpay,image_id=imageobj)
                                    except Exception as e:
                                        print("Error While Getting Cont Pay Det Obj in paymentForContAuto: ",e)
                                    if not contpaydet:
                                        print("Not Found contpaydet So Creating New")
                                        try:
                                            contpaydet = Contributor_Payment_Details.objects.create(cont_pay_id=contpay,image_id=imageobj,downloads_when_paid=imageobj.downloads)
                                        except Exception as e:
                                            print("Error While Creating cont pay det obj in paymentForContAuto: ",e)
                                        
                                        
                                    if contpaydet: #If Found
                                        print("Contpaydet: ",contpaydet)
                                        total_downloads = imageobj.downloads
                                        payment_paid_downloads = imageobj.downloads - rem_det_obj.downloads_when_purchased
                                        #Converting To Int If Not
                                        try:
                                            total_downloads = int(total_downloads)
                                            payment_paid_downloads = int(payment_paid_downloads)
                                        except Exception as e:
                                            print("Error While Converting To Int Type in paymentForContAuto: ",e)
                                        #Calculating Downloads For Which Payment is Not Paid Yet
                                        try:
                                            payment_rem_downloads = total_downloads - payment_paid_downloads
                                        except Exception as e:
                                            print("Error While Calculating payment_rem_downloads in paymentForContAuto: ",e)
                                        else:
                                            #Calculating Actual Amount
                                            try:
                                                totalamount = payment_rem_downloads * imageobj.price
                                                total_earnings = totalamount * 70 / 100
                                                imageobj.total_earnings = total_earnings
                                                

                                            except Exception as e:
                                                print("Error While Calculating TotalAMount in paymentForContAuto: ",e)
                                            else:
                                                try:
                                                    imageobj.save()
                                                except Exception as e:
                                                    print("Error While Saving Imageobj in paymentForContAuto: ",e)

                                                print("Total Downloads: ",total_downloads)
                                                print("Payment Paid Downloads: ",payment_paid_downloads)
                                                print("Payment REmaining Downloads: ",payment_rem_downloads)
                                                print("Total Earnings: ",total_earnings)
                                                #Update ContPay Obj's Total Amount
                                                print("Before Total Amount in Contpay Obj: ",contpay.total_amount)
                                                try:
                                                    totalamountforcont =  imageobj.price * imageobj.downloads
                                                    total_earningsforcont = totalamountforcont * 70 / 100
                                                    contpay.total_amount += total_earningsforcont
                                                except Exception as e:
                                                    print("Error While Setting TotalAMount For COntPay Obj in paymentForContAuto: ",e)
                                                else:
                                                    
                                                    #Save Cont Pay
                                                    try:
                                                        contpay.save()
                                                    except Exception as e:
                                                        print("Error While Saving contpay obj in paymentForContAuto: ",e)
                                                    else:
                                                        #get ContPayDet Obj
                                                        print("COnpay SAved")
                                                        print("After Total Amount in Contpay Obj: ",contpay.total_amount)
                                                        print("Trying to Get COntPayDet")
                                                        try:
                                                            contpaydet = Contributor_Payment_Details.objects.get(cont_pay_id=contpay,image_id=imageobj.image_id)
                                                        except Exception as e:
                                                            print("Error While Getting contpaydet in paymentForContAuto: ",e)
                                                            #Then Create
                                                            print("So Creating NEw ContPayDet Obj")
                                                            try:
                                                                contpaydet = Contributor_Payment_Details.objects.create(cont_pay_id=contpay,image_id=imageobj,downloads_when_paid=imageobj.downloads)
                                                            except Exception as e:
                                                                print("Error While Creating contpaydet in paymentForContAuto: ",e)
                                                            else:
                                                                contpaydet.payment_status = True
                                                                try:
                                                                    contpaydet.save()
                                                                except Exception as e:
                                                                    print("Error While Saving contpaydet in paymentForContAuto: ",e)
                                                                else:
                                                                    print("Contpaydet Created")
                                                                    print("Contpaydet: ",contpaydet)
                                                                
                                                        finally:
                                                            
                                                                    unpaid = imageobj.price * 70 / 100
                                                                    if imageobj.total_unpaid_earnings > 0:
                                                                        imageobj.total_unpaid_earnings -= unpaid
                                                                    ispaymentpaid = True
                                                                    #Delete rem det obj
                                                                    try:
                                                                        
                                                                        rem_det_obj.delete()
                                                                        imageobj.save()
                                                                    except Exception as e:
                                                                        print("Error While Deleting rem det obj in paymentForContAuto: ",e)
                                                                    else:
                                                                        print("Rem_Det_obj Deleted")
                               

                    #delete rem_obj
                    try:
                        print("Deleting RemObj")
                        unpaidtotal+=rem_obj.total_amount
                        rem_obj.delete()
                    except Exception as e:
                        print("Error While Deleting rem_pay_obj in paymentForContAuto: ",e)
                    else:
                        print("RemObj Deleted")
            print("ispaymentpaid: ",ispaymentpaid)
            if ispaymentpaid:
                print("Payment Has Been Paid So Send Mail")
                subject = "Payment From Photostudioroom"
                email_text = "email/stockimages/contributor/contpayment.txt"
                email_html = "email/stockimages/contributor/contpayment.html"
                c = {
                        "email":curuser.userobj.email,
                        'domain':'127.0.0.1:8000',
                        'site_name': 'Photostudioroom',
                        "user": curuser,
                        "firstname":curuser.userobj.first_name,
                        "lastname":curuser.userobj.last_name,
                        "totalamount":unpaidtotal,
                        'protocol': 'http',
                    }
                email = render_to_string(email_text, c)
                email_html = render_to_string(email_html, c)
                email_from = "Photostudioroom <psr.gj26.github@gmail.com>"
                try:
                    send_mail(subject, email, email_from , [curuser.userobj.email], fail_silently=False,html_message=email_html)
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
                return redirect("/adminhome/result/True")        
            else:
                print("Payment Failed!!")
                return redirect("/adminhome/result/False") 
      

                            

                                        
                                        

                    
        """
        #Get All The Approved Images Uploaded By Current Contributor
        try:
            images = Images.objects.filter(user_id=curuser.user_id,status="A")
        except Exception as e:
            print("Error While Getting Images in paymentForContAuto: ",e)
        else:#If Image Found
            #Have to Give 70% to The Contributor
            #First Calculate The Total Amount
            print("Images: ",images)
            try:#Getting PayDetObj Of PSR From Which THe Payment Will Be Paid
                pay_det = Payment_Details.objects.get(pay_details_id=PSR_PAY_DET_ID)
            except Exception as e:
                print("Error While Getting Payment Details Obj in paymentForContAuto: ",e)
            else:#If Payment Det Obj Found(Rare case if not found)
                print("Payment Details: ",pay_det)
                try:#Then Create a ContPay Object With Pay_Det_id and Total_amount as 0
                    contpay = Contributor_Payment.objects.create(pay_details_id=pay_det,total_amount=totalamount,user_id=curuser)
                except Exception as e:
                    print("Error While Creating COntributor Payment Details: ",e)
                else:#If Got ContPay Obj Then
                    print("Cont Pay: ",contpay)
                    try:#Save ContPay
                        contpay.save()
                    except Exception as e:
                        print("Error While SAving ContPay Obj in paymentForContAuto: ",e)
                    
                    else:#If ContPay is Saved
                        i = 0
                        

                        for image in images:#Get Each Image From All the Images
                            try:

                                print("Loop Counter : ",i)
                                i += 1
                                print("Image in Second Loop",image)
                                print("Image_id: ",image.image_id)
                                print("Image Downloads: ",image.downloads)
                                
                                try:#Check if Payment is Already Done(if downloads when paid = image downloads)
                                    contpaydet = Contributor_Payment_Details.objects.get(image_id=image,downloads_when_paid=image.downloads,payment_status=True)
                                except Exception as e:#IF Not Then
                                    print("Error While Getting Cont Pay Det in payForContAuto: ",e)
                                    
                                    try:#Get Last ContPayDet Object With Payment True If Not Found Then None
                                        contpaydet = Contributor_Payment_Details.objects.filter(image_id=image,payment_status=True).last()
                                    except Exception as e:
                                        print("Error While Getting COntPayDet: ",e)
                                    print("contpaydet: ",contpaydet)
                                    print("image: ",image)
                                    print("downloads: ",image.downloads)
                                    print("Image Price: ",image.price)
                                    if image.downloads > 0:#If Image is Purchased atleast One Time
                                        print("I am in if")
                                        print(f"Total Amount Before {image.image_name}\n")
                                        print(totalamount)
                                        if contpaydet != None:#If Already Paid Any Previous Payment For The Current Image
                                            print("Cont Pay Det is Not None")
                                            if image.downloads > contpaydet.downloads_when_paid:#Then Check if image downloads is > downloads when paid(Means After Last Payment Some More Purchases Are Done For The Current Image)
                                                print("Image Downloads is Greater Then Downloads When Paid")
                                                #If True Then GEt Actual Downloads By Subtracting Downloads When Paid From Image Downloads
                                                actualdownloads = image.downloads - contpaydet.downloads_when_paid
                                                #Then Get Total AMount With Actualdownloads * Image Price
                                                totalamount += actualdownloads * image.price    
                                        else:#First Time Payment
                                            print("Contpaydet is None")
                                            print("Image Downloads is Not Greater Then Downloads When Paid")
                                            #THen Calculate Total Amount With Image Downloads * Image Price
                                            totalamount += image.downloads * image.price

                                        
                                        print(f"Total Amount After {image.image_name}\n")
                                        print(totalamount)
                                    
                                    iseveryalreadypaid = False #Indicates That Payment is Due
                                    #Create COntPayDet Obj From Above Details
                                    contpaydet = Contributor_Payment_Details.objects.create(image_id=image,downloads_when_paid=image.downloads,cont_pay_id=contpay) 

                                    try:
                                        total_earnings = image.price * image.downloads
                                        total_earnings = total_earnings * 70 / 100
                                        image.total_earnings = total_earnings
                                    except Exception as e:
                                        print("Error While Setting Total Earnings in Image in payForContAuto: ",e)
                                    else:
                                        try:
                                            image.save()
                                        except Exception as e:
                                            print("Error While Saving Image Object in payForContAuto: ",e)
                                else:#If Payment is Already Done Then Continue The loop Don't Run Below Code and Increase Iterator
                                    print("contpaydet image_id: ",contpaydet.image_id.image_id)
                                    print("contpaydet downloads when paid: ",contpaydet.downloads_when_paid)
                                    print("contpaydet paymentStatus: ",contpaydet.payment_status)
                                    print("Already Paid For ",image.image_name)
                                    continue
                            except Exception as e:
                                print("Error While Creating Contributor Payment Details in paymentForContAuto: ",e)
                            else:#If No Error In Above Code
                                print("Cont Pay Details: ",contpaydet)
                                try:#Then Try To Set Payment_Status = True and Save the ContPayDet Obj
                                    contpaydet.payment_status = True
                                    contpaydet.save()
                                except Exception as e:#If Error Then Return Error Message as HttpResponse
                                    print("Error While Saving contpaydet obj in paymentForContAuto: ",e)
                                    return HttpResponse("Error While Giving Payment to Contributor ",username)
                                
                                    #sendmail
                        
                        print("iseverypaid: ",iseveryalreadypaid)
                        #If iseveryalreadypaid is false it means That We Had Paid Payment to Cont
                        if iseveryalreadypaid == False:
                            from decimal import Decimal 
                            #According to policies We are giving 70% of Total Income to THe Contributor and 30% Will be Shared With PSR
                            print("Total Amount Before Cut: ",totalamount)
                            totalamount = totalamount * 70 / 100  
                            print("Total Amount After Cut: ",totalamount)
                            try:#Then Try To Set Total Amount of ContPay Obj and Save it
                                contpay.total_amount = totalamount
                                contpay.save()
                            except Exception as e:
                                print("Error While Saving ContPay Obj in payForCOntAuto: ",e)
                            #Then Send an Email to Contributor
                            subject = "Payment From Photostudioroom"
                            email_text = "email/stockimages/contributor/contpayment.txt"
                            email_html = "email/stockimages/contributor/contpayment.html"
                            c = {
                                "email":curuser.userobj.email,
                                'domain':'127.0.0.1:8000',
                                'site_name': 'Photostudioroom',
                                "user": curuser,
                                "firstname":curuser.userobj.first_name,
                                "lastname":curuser.userobj.last_name,
                                "totalamount":totalamount,
                                'protocol': 'http',
                                }
                            email = render_to_string(email_text, c)
                            email_html = render_to_string(email_html, c)
                            email_from = "Photostudioroom <psr.gj26.github@gmail.com>"
                            try:
                                send_mail(subject, email, email_from , [curuser.userobj.email], fail_silently=False,html_message=email_html)
                            except BadHeaderError:
                                return HttpResponse('Invalid header found.')
                            
                            return redirect("/adminhome/result/True")
                            
                        #If iseveryalreadypaid is true it means That We Don't Have to Pay Payment to Cont
                        else:
                            #Deleting ContPay Object Because It Will Created Unnecessarily as Payment is Already Paids
                            try:
                                contpay.delete()
                            except Exception as e:
                                print("Error While Deleting ContPay Obj in PayForContAuto: ",e)
                            
                            
                            return redirect("/adminhome/result/False")
            """
        
        
        return redirect("/adminhome/")
        

