
from django.db.models.fields import DecimalField
from Photostudioroom.views import login_page
import datetime
import json
from django import template
from django.contrib.auth.models import AnonymousUser
from django.core.mail import send_mail
from django.db.models.query import QuerySet
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from Appointment.models import *
from django.http import HttpResponseRedirect
from django.core import serializers
from django.template import Library
from django.contrib.auth.decorators import login_required
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os, sys






# Create your views here. 


#For Adding Watermark to Images Uploaded By Contributor
FONT = 'arial.ttf'
 
def add_watermark(in_file, text, username,filename,out_file='', angle=23, opacity=0.25):
    thumb_folder=f'media/stockimages/thumbnails/{username}'
    out_file=f'media/stockimages/thumbnails/{username}/thumb{filename}'
    


    try:
        if not os.path.exists(thumb_folder):
            os.makedirs(thumb_folder)
    except OSError:
        print ("Creation of the directory %s failed" % thumb_folder)
    else:
        print ("Successfully created the directory %s" % thumb_folder)
    
    print("we are in add_watermark view")
    img = Image.open(in_file).convert('RGB')
    watermark = Image.new('RGBA', img.size, (0,0,0,0))
    size = 2
    n_font = ImageFont.truetype(FONT, size)
    n_width, n_height = n_font.getsize(text)
    while n_width+n_height < watermark.size[0]:
        size += 2
        n_font = ImageFont.truetype(FONT, size)
        n_width, n_height = n_font.getsize(text)
    draw = ImageDraw.Draw(watermark, 'RGBA')
    draw.text(((watermark.size[0] - n_width) / 2,
              (watermark.size[1] - n_height) / 2),
              text, font=n_font)
    watermark = watermark.rotate(angle,Image.BICUBIC)
    alpha = watermark.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    watermark.putalpha(alpha)
    Image.composite(watermark, img, watermark).save(fp=out_file, format='JPEG')
    return out_file
    

#This Function Will Be Called When Watermark has to be Added to Image, This Function will Call Above Function
def wm(request,filepath,username,filename):
    print("we are in wm view")
    img = add_watermark(in_file=f'media/{filepath}',text="Photostudioroom",username=username,filename=filename)
    print("this is watermark img filepath: ",img)
    
    return img



#MAIN
def stockImagesHome(request):
    # isstockactive for nav bar to set orange bg in navbar,id as active to get orange color back when scroll up
    orderdetobjs = {}
    orderdetobj = None
    if request.method == 'POST':
        if request.user.is_authenticated:
            if 'imgviewinc' in request.POST:  # TO Increase Views Of an Image When User Clicks On It

                # Get Imageid Sent By Ajax From Template
                imgid = request.POST['imageid']
                try:
                    # Get Image Object Of This Imageid
                    image = Images.objects.get(image_id=imgid)
                    image.views += 1  # Increase its view by 1
                except Exception as e:
                    print(e)
                else:  # If There is no errors
                    image.save()  # save image object

            if 'imglikeinc' in request.POST:  # TO Increase Likes Of an Image When User Clicks Like Button
                # Getting Imageid sent by Ajax From Template
                
                imgid = request.POST['imageid']
                # Getting image object of it
                image = Images.objects.get(image_id=imgid)
                try:
                    print("in try")
                    try:
                        if request.user.is_authenticated:  # if user is logged in
                            curuser = request.user  # then get Current Logged in User
                            curuser = User_Details.objects.get(
                                userobj=curuser)  # need user_Details object
                            print(curuser)
                    except Exception as e:
                        print("Error in Cart View - AddItems , Error: ", e)
                    else:  # If No Error Occured

                        try:  # Check if user already liked this image
                            likebyuser = Like_Details.objects.get(
                                user_id=curuser, image_id=image)
                        except Exception as e:  # image not liked then this will execute
                            print(e)
                            image.likes += 1  # then increase like by 1 for this image
                            likebyuser = Like_Details.objects.create(
                                user_id=curuser, image_id=image)  # create new obj for like_details
                            likebyuser.save()  # save it

                        else:  # if already liked then unlike it
                            likebyuser.delete()  # delete object(row from table)
                            print("decreasing like")
                            image.likes -= 1  # decrease like for this image

                except Exception as e:
                    print("Error: ", e)
                else:  # If No Errors
                    print("saving image")
                    image.save()  # Then Save Image
                if 'getalllikesfrminc' in request.POST:  # TO Update Likes Of all Images When Page Loads
                    print("WE ARE IN GETTOTALLIKES")
                    # Get Image Ids Which Are in Current Page(Sent By Ajax)
                    imgidsflikes = request.POST['imgidsforlikes']
                    # Converting Stringified JSON to Array
                    imgidsflikes = json.loads(imgidsflikes)
                    actualimgids = []
                    print("before slicing: ", imgidsflikes)
                    i = 0
                    # Converting js Imageids to DB Imageids(i.e. img11 to 11)
                    while i < len(imgidsflikes):
                    # img11 is js image id set by me and 11 is database id for that same image
                        if imgidsflikes[i][3:] not in actualimgids:
                            actualimgids.append(imgidsflikes[i][3:])
                        i += 1
                    print("After Slicing: ", actualimgids)

                    try:

                        images = Images.objects.in_bulk(actualimgids)
                    except Exception as e:
                        print(e)
                    else:
                        imgswlikes = {}
                        print(type(images))
                        for key,value in images.items():
                            imgswlikes[value.image_id] = value.likes
                        if request.user.is_authenticated:
                            return JsonResponse({"imgswlikes": imgswlikes}, status=200)
                        else:
                            return JsonResponse({"imgswlikes": imgswlikes,"unknownuser": True}, status=200)
                        
                            

            if 'getlikes' in request.POST:  # TO Update Likes Of an Image When Page Loads Which is Liked By Current User
                try:
                    if request.user.is_authenticated:  # if user is logged in
                        curuser = request.user  # then get Current Logged in User
                        curuser = User_Details.objects.get(
                            userobj=curuser)  # need user_Details object
                        print(curuser)
                except Exception as e:
                    print("Error: ", e)
                else:  # If No Errors
                    # Get Image Ids Which Are in Current Page(Sent By Ajax)
                    imgidsflikes = request.POST['imgidsforlikes']
                    # Converting Stringified JSON to Array
                    imgidsflikes = json.loads(imgidsflikes)
                    actualimgids = []
                    print("before slicing: ", imgidsflikes)
                    i = 0
                    # Converting js Imageids to DB Imageids(i.e. img11 to 11)
                    while i < len(imgidsflikes):
                        # img11 is js image id set by me and 11 is database id for that same image
                        if imgidsflikes[i][3:] not in actualimgids:
                            actualimgids.append(imgidsflikes[i][3:])
                        i += 1
                    print("After Slicing: ", actualimgids)

                    reimageidsflikes = []
                    try:  # check how many images from current page is liked by current user
                        likesbycuruser = Like_Details.objects.filter(
                            user_id=curuser)
                    except Exception as e:
                        print(e)
                    else:  # If likes found
                        for image in likesbycuruser:  # get image ids of liked images and add it with true value into dict
                            reimageidsflikes.append(
                                str(image.image_id.image_id))
                    return JsonResponse({"imageslikedbyuser": reimageidsflikes}, status=200)
            
                """

                reimageidsflikes = []
                try:  # check how many images from current page is liked by current user
                    likesbycuruser = Like_Details.objects.filter(
                        user_id=curuser)
                except Exception as e:
                    print(e)
                else:  # If likes found
                    for image in likesbycuruser:  # get image ids of liked images and add it with true value into dict
                        reimageidsflikes.append(str(image.image_id.image_id))
                return JsonResponse({"imageslikedbyuser": reimageidsflikes}, status=200)
          
              """
        
        if 'gettotallikes' in request.POST:  # TO Update Likes Of all Images When Page Loads
            print("WE ARE IN GETTOTALLIKES")
            # Get Image Ids Which Are in Current Page(Sent By Ajax)
            imgidsflikes = request.POST['imgidsforlikes']
            # Converting Stringified JSON to Array
            imgidsflikes = json.loads(imgidsflikes)
            actualimgids = []
            print("before slicing: ", imgidsflikes)
            i = 0
            # Converting js Imageids to DB Imageids(i.e. img11 to 11)
            while i < len(imgidsflikes):
                # img11 is js image id set by me and 11 is database id for that same image
                if imgidsflikes[i][3:] not in actualimgids:
                    actualimgids.append(imgidsflikes[i][3:])
                i += 1
            print("After Slicing: ", actualimgids)

            try:

                images = Images.objects.in_bulk(actualimgids)
            except Exception as e:
                print(e)
            else:
                imgswlikes = {}
                print(type(images))
                for key,value in images.items():
                    imgswlikes[value.image_id] = value.likes
                return JsonResponse({"imgswlikes": imgswlikes}, status=200)
    purchasedimageids = []    
    if request.user.is_authenticated:
        orderids = []
        
        try:
            user = request.user
            curuser = User_Details.objects.get(userobj=user)
            orderobj = Order.objects.filter(user_id=curuser)
        except Exception as e:
            print("Error While Getting Order Object in StockImagesHome: ",e)
        else:
            try:
                print(orderobj)
                for order in orderobj:
                    print(type(order.order_id))
                    orderids.append(order.order_id)
                i = 0
                for orderid in orderids:
                    print("Order Id: ",orderid)
                    try:
                        orderdetobj = Order_Details.objects.filter(order_id=orderid)
                    except Exception as e:
                        print(e)
                    else:
                        print("OrderDetObj: ",orderdetobj)
                        orderdetobjs[i] =  orderdetobj
                        i += 1

                print(orderdetobjs)

            except Exception as e:
                print("Error While Getting Order Details Object in StockImages Home: ",e)
            else:
                print(orderdetobj)
                for key,value in orderdetobjs.items():
                    print("Value: ",value)
                    for val in value:
                        print("Val: ",val.image_id.image_id)
                        purchasedimageids.append(val.image_id.image_id)
                print("Purchased Image Ids : ",purchasedimageids)
                        
    
    images = Images.objects.all() #To Display All The Images On Main StockImages Page
    print(type(images))
    
 
    
    #return JsonResponse({"imgswlikes": imgswlikes}, status=200)
    
    return render(request, "stockimages/stockimages.html", {'isstockactive': 'class=active id=active','images':images,"purchasedimageids":purchasedimageids})

#For Searching Images
def search(request):
    orderdetobjs = {}
    imagesbyname = None
    imagesbycat = None
    imagesbytags = None
    images = None
    catobj = None
    msg = None
    if request.method == 'POST':
        searchquery = request.POST.get('searchquery') #Get Search Query
        print("Search Query For Images: ",searchquery)
        try:
            imagesbyname = Images.objects.filter(image_name__icontains=searchquery) #Get Image Obj Which Contains Image Name as  Search Query
            print("ImagesByName: ",imagesbyname)
            
        except Exception as e:
            print(e)
        try:
            imagesbytags = Images.objects.filter(tags__icontains=searchquery) #Get Image Obj Which Contains Image Tags as  Search Query
            print("ImagesByTags: ",imagesbytags)
            
        except Exception as e:
            print(e)
        
        try:
            catobj = Categories.objects.get(category_name__icontains=searchquery) #Get Cate Obj Which Contains Category as Search Query
            imagesbycat = Images.objects.filter(category=catobj) #Get Image Obj Which Contains Image Category as Search Query
            print("Category: ",catobj)    
            print("Images By Category: ",imagesbycat)    
        except Exception as e:
            print(e)
        print("imagesbycat",imagesbycat)
        try:
            if imagesbycat != None and imagesbyname != None and imagesbytags != None: #If ImagebyCategory and ImageByName is not None
                images = imagesbyname | imagesbycat | imagesbytags #Add Both to Images 
            elif imagesbycat != None and imagesbyname != None: #If ImagebyCategory and ImageByName is not None
                images = imagesbyname | imagesbycat #Add Both to Images 
            elif imagesbytags != None and imagesbyname != None:
                images = imagesbyname | imagesbytags
            elif imagesbycat != None and imagesbytags != None:
                images = imagesbycat | imagesbytags
            elif imagesbyname != None: #If ImageByCategory is None It Means Only ImageByName is Not None
                images = imagesbyname #Then Set Images as ImageByName
            elif imagesbytags != None: #If ImageByCategory is None It Means Only ImageByName is Not None
                images = imagesbytags #Then Set Images as ImageByName
            elif imagesbycat != None: #If ImageByName is None It Means Only ImageByCategory is Not None
                images = imagesbycat #Then Set Images as ImageByCategory
        except Exception as e:
            print(e)
        print("Images: ",images)
        if images == None or images.count() == 0: #If There is No Search Result For Search Query
            msg = f"No Images Found For \"{searchquery}\" Search   " #Then Set No Images Found Message
        else:
            print("no none")
            print("searrchimg",images)
    purchasedimageids = []    
    if request.user.is_authenticated:
        orderids = []
        
        try:
            user = request.user
            curuser = User_Details.objects.get(userobj=user)
            orderobj = Order.objects.filter(user_id=curuser)
        except Exception as e:
            print("Error While Getting Order Object in StockImagesHome: ",e)
        else:
            try:
                print(orderobj)
                for order in orderobj:
                    print(type(order.order_id))
                    orderids.append(order.order_id)
                i = 0
                for orderid in orderids:
                    print("Order Id: ",orderid)
                    try:
                        orderdetobj = Order_Details.objects.filter(order_id=orderid)
                    except Exception as e:
                        print(e)
                    else:
                        print("OrderDetObj: ",orderdetobj)
                        orderdetobjs[i] =  orderdetobj
                        i += 1

                print(orderdetobjs)

            except Exception as e:
                print("Error While Getting Order Details Object in StockImages Home: ",e)
            else:
                print(orderdetobj)
                for key,value in orderdetobjs.items():
                    print("Value: ",value)
                    for val in value:
                        print("Val: ",val.image_id.image_id)
                        purchasedimageids.append(val.image_id.image_id)
                print("Purchased Image Ids : ",purchasedimageids)
    return render(request, "stockimages/stockimages.html", {'images': images, 'searchquery': searchquery, 'isstockactive': 'class=active id=active',"msg":msg,"purchasedimageids":purchasedimageids})

#To Send Images By Category
def categories(request, category=None):
    orderdetobjs = {}
    print(category)
    images = None
    msg = None
    catobj = Categories.objects.get(category_name__icontains=category[1:])

    images = Images.objects.filter(category=catobj)
    if images.count() == 0:
        msg = f"No Images Found For \"{catobj.category_name}\" Category"
    else:
        print("no none")
    print("img: ",images)
    """
    # getting data available in variable atcs,sent via url from cart() view
    # used to determine that image is added to cart
    atcs = request.GET.get('atcs','')
    if "psratc" in atcs: #if image is added to cart
        imageid = atcs[6:] #Slicing to Remove Prefix psratc
    """
    print(type(images))
    purchasedimageids = []    
    if request.user.is_authenticated:
        orderids = []
        
        try:
            user = request.user
            curuser = User_Details.objects.get(userobj=user)
            orderobj = Order.objects.filter(user_id=curuser)
        except Exception as e:
            print("Error While Getting Order Object in StockImagesHome: ",e)
        else:
            try:
                print(orderobj)
                for order in orderobj:
                    print(type(order.order_id))
                    orderids.append(order.order_id)
                i = 0
                for orderid in orderids:
                    print("Order Id: ",orderid)
                    try:
                        orderdetobj = Order_Details.objects.filter(order_id=orderid)
                    except Exception as e:
                        print(e)
                    else:
                        print("OrderDetObj: ",orderdetobj)
                        orderdetobjs[i] =  orderdetobj
                        i += 1

                print(orderdetobjs)

            except Exception as e:
                print("Error While Getting Order Details Object in StockImages Home: ",e)
            else:
                print(orderdetobj)
                for key,value in orderdetobjs.items():
                    print("Value: ",value)
                    for val in value:
                        print("Val: ",val.image_id.image_id)
                        purchasedimageids.append(val.image_id.image_id)
                print("Purchased Image Ids : ",purchasedimageids)
    return render(request, "stockimages/stockimages.html", {'images': images, 'isstockactive': 'class=active id=active',"msg":msg,"purchasedimageids":purchasedimageids})


"""
cart() view to get cart details and to update cart details
"""


def cart(request):
    imageids = []
    cartcount = 0
    print("cart() called")
    if not request.user.is_authenticated:
        return JsonResponse({"unknownuser": 'true'}, status=200)

    if request.method == 'POST':
        if 'additems' in request.POST:  # If additems variable is sent by ajax
            print("We are in add items")
            # Then retrieve imgidfrmajax variable
            imgidfrmajax = request.POST['imgidfrmajax']
            print("imgidfrmajax: ", imgidfrmajax)
            imageid = imgidfrmajax[3:]  # remove prefix img
            print("image id after slicing", imageid)
            # Getting Image Object Of Image Which is Being Added To The Cart
            image = Images.objects.get(image_id=imageid)
            print("image obj:", image)
            try:
                if request.user.is_authenticated:  # if user is logged in
                    curuser = request.user  # then get Current Logged in User
                    curuser = User_Details.objects.get(
                        userobj=curuser)  # need user_Details object
                    print(curuser)
            except Exception as e:
                print("Error in Cart View - AddItems , Error: ", e)
            try:
                # check if cart is already available
                cart = Cart.objects.get(user_id=curuser)

            except Cart.DoesNotExist as e:  # if not then exception will occur
                # then create one cart or this user
                cart = Cart.objects.create(user_id=curuser)
                cart.save()  # save it
            except Exception as e:  # handling other exception
                print("Error if", e)
            finally:  # not matter what happens finally do this
                cartdet = Cart_Details.objects.create(
                    cart_id=cart, image_id=image)  # create a cart_Details object
                cartdet.save()  # save it

                cartdet = Cart_Details.objects.filter(
                    cart_id=cart)  # get cart_Details
                cartcount = cartdet.count()  # count how many items in cart

        elif 'getitems' in request.POST:  # If getitems variable is sent by ajax
            try:
                if request.user.is_authenticated:  # if user is logged in
                    curuser = request.user  # Getting Current Logged in User
                    curuser = User_Details.objects.get(userobj=curuser)
            except TypeError as e:
                print("Error in Cart View - GetItems , Error: ", e)
            try:

                if request.user.is_authenticated:
                    # get cart if available
                    cart = Cart.objects.get(user_id=curuser)
                    cartdet = Cart_Details.objects.filter(
                        cart_id=cart)  # get cart details
                    cartcount = cartdet.count()  # get cartcount
                    imageidss = []  # will get image ids as queryset
                    for carts in cartdet:  # getting ids of images from cart_Details, Lil bit complex code
                        # get values_list of image_id from image table where image_id=carts.image_id.image_id
                        # carts.image_id gives one image id object that's why by writing cart.image_id.image_id
                        # we are fetching actual image_id, then append imageids in imageidss list
                        imageidss.append(Images.objects.filter(
                            image_id=carts.image_id.image_id).values_list("image_id"))

                    # values_list() returns queryset, which has nested elements,so we have to get our required data
                    # in our case we are getting actual imageids
                    for imageidoutest in imageidss:
                        for imageidouter in imageidoutest:
                            for imageid in imageidouter:
                                # finally getting imageids and adding them into imageids list
                                imageids.append(imageid)

            except Cart.DoesNotExist as e:  # will raise if cart not available
                cartcount = 0  # then simply set cartcount as 0
            except Exception as e:  # handling other exception
                cartcount = 0
                print("Error elif", e)
    return JsonResponse({"cartcount": cartcount, 'imageids': imageids}, status=200)

#TO Display Cart Items In Cart Page
def showCart(request):
    imageids = []
    images = None
    totalamount = None
    imagecount = None
    try:
        if request.user.is_authenticated:  # if user is logged in
            curuser = request.user  # Getting Current Logged in User
            curuser = User_Details.objects.get(userobj=curuser)
    except TypeError as e:
        print("Error in Cart View - GetItems , Error: ", e)
    try:

        if request.user.is_authenticated:
            cart = Cart.objects.get(user_id=curuser)  # get cart if available
            cartdet = Cart_Details.objects.filter(
                cart_id=cart)  # get cart details
            # cartcount = cartdet.count() #get cartcount
            imageidss = []  # will get image ids as queryset
            for carts in cartdet:
                # getting ids of images from cart_Details, Lil bit complex code
                # get values_list of image_id from image table where image_id=carts.image_id.image_id
                # carts.image_id gives one image id object that's why by writing cart.image_id.image_id
                # we are fetching actual image_id, then append imageids in imageidss list
                imageidss.append(Images.objects.filter(
                    image_id=carts.image_id.image_id).values_list("image_id"))

            # values_list() returns queryset, which has nested elements,so we have to get our required data
            # in our case we are getting actual imageids

            for imageidoutest in imageidss:
                for imageidouter in imageidoutest:
                    for imageid in imageidouter:
                        # finally getting imageids and adding them into imageids list
                        imageids.append(imageid)

            print(imageids)
            images = Images.objects.filter(pk__in=imageids) #Getting Total Images
            print(images)
            totalamount = 0
            imagecount = 0
            for image in images:
                totalamount += image.price #Getting Total Amount
            imagecount = images.count() #Counting Total Images
            print(totalamount)

    except Cart.DoesNotExist as e:  # will raise if cart not available
        cartcount = 0  # then simply set cartcount as 0
    except Exception as e:  # handling other exception
        cartcount = 0
        print("Error elif", e)
    return render(request, "stockimages/customer/cartpage.html", {"images": images, "totalamount": totalamount, "imagecount": imagecount})

#When Customer Want to Remove Item From Cart
def removeCart(request):
    if request.method == 'POST':
        try:
            if request.user.is_authenticated:  # if user is logged in
                curuser = request.user  # Getting Current Logged in User
                curuser = User_Details.objects.get(userobj=curuser)
        except TypeError as e:
            print("Error in Cart View - GetItems , Error: ", e)
        if 'removeitems' in request.POST:  # If additems variable is sent by ajax
            imgidfrmajax = request.POST['imageid'] #Getting Image Id Which Image We Want to Remove From Cart

            if request.user.is_authenticated:
                try:
                    # get cart if available
                    cart = Cart.objects.get(user_id=curuser) #Get Cart Object Of User
                    cartdet = Cart_Details.objects.filter(
                        cart_id=cart, image_id=imgidfrmajax)  # get cart details
                    print(cartdet)
                    cartdet.delete() #Delete CartDetails Object

                except Exception as e:
                    print(e)

            return JsonResponse({"imgid": imgidfrmajax}, status=200)


#Stock Payment Page When User Checkout
def stockpaymentpage(request,image=None):
    """
    argument image will be none if this view is called from cart page,
    if there is something in image then it is directly called from purchase button
    """
    print("\n\nWe are in stockpaymentpage")
    print("Image is ",image)
    iscartpurchase = None
    imageobjforload = None
    totalamount = 0
    if request.user.is_authenticated:
        if image == None:
            try:
                curuser = User.objects.get(id=request.user.id)
                curuser = User_Details.objects.get(userobj=curuser)
            except Exception as e:
                print("Error While Getting User Object in stockpaymentpage View: ",e)
            try:
                cartobj = Cart.objects.get(user_id=curuser) #Getting CartObject
                print(cartobj)
                cartdetobj = Cart_Details.objects.filter(cart_id=cartobj.cart_id) #Getting Cart_Details Object
                print(cartdetobj)

                for img in cartdetobj: #Getting Every Image Available in Cart
                    print(img.image_id.image_id)
                    try:
                        imageobj = Images.objects.get(image_id=img.image_id.image_id) #Getting Image Object From Image_id
                        print(imageobj)
                        print(imageobj.price)
                        totalamount += imageobj.price #Adding Image Price in Total Amount
                        print(totalamount)
                    except Exception as e:
                        print("Error While Getting Image Object in stockpaymentpage View: ",e)
                iscartpurchase = True

        #Single Image Purchase
            except Exception as e: #If Nothing in Cart
                print("Error While Getting Cart Object in stockpaymentpage View(Probably Because Cart is Empty): ",e)
        if image != None: #if Got Imageid From Url
            print("You Are From Direct Purchase")
            try:
                   
                imageobjforload = Images.objects.get(image_id=image)
                print(imageobjforload)
            except Exception as e:
                print("Error While Getting Image Object For Single Image Purchase in stockpaymentpage View: ",e)
            else:
                totalamount = imageobjforload.price
                iscartpurchase = False
    else:
        return login_page(request)
    return render(request,"payment/stockpayment.html",{"totalamount":totalamount,"image":imageobjforload,"iscartpurchase":iscartpurchase})

#This Page Will be Loaded After PaymentPage Which Will Get Payment Details and Save it
def stockpaymentload(request,imageparam=None):
    """
    If Imageparam is None it Means It is Came From Cart
    If Not None it Means It Came Directly From Single Image Purchase
    """
    print("\n\nWe are in stockpaymentload")
    curuser = None
    paymobj = None
    orderdetobj = None
    orderobj = None
    paydet = None
    totalamount = 0
    if request.user.is_authenticated:
        try:
            curuser = User.objects.get(id=request.user.id)
            curuser = User_Details.objects.get(userobj=curuser)
        except Exception as e:
            print(e)
    else:
        return login_page(request)
    if request.method == "POST":
        print(type(imageparam))
        if imageparam == None: #Came From Cart(Cart Has Images)
            print("\n\nPOST in stockpaymentload(From Cart)")
            try:
                cartobj = Cart.objects.get(user_id=curuser) #Getting Cartobj For Current User
                print(cartobj)
                cartdetobj = Cart_Details.objects.filter(cart_id=cartobj.cart_id) #Getting Cartdetails obj For Current User
                print(cartdetobj)

                for image in cartdetobj: #Getting Single Image From Cart
                    print(image.image_id.image_id)
                    try:
                        imageobj = Images.objects.get(image_id=image.image_id.image_id) #Get Image Object For Image From Cart
                        print(imageobj)
                        print(imageobj.price)
                        totalamount += imageobj.price #Add Current Image Price in Total Amount
                        print(totalamount)
                    except Exception as e:
                         print("Error While Getting Image Object For Cart Purchase in stockpaymentload View: ",e)

            except Exception as e:
                 print("Error While Getting Cart Object For Cart Purchase in stockpaymentload View: ",e)
            #Getting Data From The Form
            cardholdername = request.POST.get("card-holder")
            expmonth = request.POST.get("expmm")
            expyear = request.POST.get("expyy")
            cardnumber = request.POST.get("card-number")
            print(cardholdername,expmonth,expyear,cardnumber)
            expdate = expmonth + "/"+ expyear #Merging Date and Month For Proper Datetime Format
            print(expdate)
            try:
                print("\n\nTrying to get paymentdetails obj in stockpaymentload")
                expdateobj = datetime.datetime.strptime(expdate, '%m/%y').date()
                print(expdateobj)
                #Checking if there is any field available with same details in payment_Details table if found do nothing it will be handled in finally
                paydet = Payment_Details.objects.get(card_no=cardnumber,card_holder_name=cardholdername,expiry_date=expdateobj)
                
            except Exception as e: #if there is nothing available with same details in payment_Details table,some steps in finally
                print(e)
                print("\n\npaymentdetails obj not found in stockpaymentload")
                try:
                    print("\n\nSo trying to create payment details obj in stockpaymentload")
                    #Creating Payment_Details Object Because Not Found in the Table With Same Details
                    paydet = Payment_Details.objects.create(card_no=cardnumber,card_holder_name=cardholdername,expiry_date=expdateobj)
                except Exception as e:#Got Error While Creating Payment_Details Object
                    print("\n\n unable to create payment details obj in stockpaymentload")
                    print(e)
                else:#If No Error Then Save
                    print("\n\ncreated payment details obj now saving it in stockpaymentload")
                    paydet.save()
            finally:
                print("\n\nWE are in finally in stockpaymentload")
                try:
                    print("\n\n trying to get appoint obj in stockpaymentload")
                    #Creating Order Object and Saving it
                    orderobj = Order.objects.create(user_id=curuser,Total_Amount=totalamount,InCart=False)
                    orderobj.save()
                    try:
                        #Getting Cart Object
                        cartobj = Cart.objects.get(user_id=curuser)
                        print(cartobj)
                        #Getting Cartdetails Object
                        cartdetobj = Cart_Details.objects.filter(cart_id=cartobj.cart_id)
                        print(cartdetobj)
                        try:
                            print("Trying to create rem_cont_pay in stockpaymentload")
                            rem_cont_pay = Remaining_Contributor_Payment.objects.create(user_id=imageobj.user_id)
                        except Exception as e:
                            print("Error While Creating Remaining_Cont_Pay Obj in stockpaymentload: ",e)
                        for image in cartdetobj: #For Every Image in Cart
                            print("Imageid: ",image.image_id.image_id)
                            print("Cartid: ",image.cart_id)
                            
                            try:
                                imageobj = Images.objects.get(image_id=image.image_id.image_id) #Get Image Obj
                                try:
                                    imageobj.downloads += 1
                                    try:
                                            totalamount = imageobj.downloads * imageobj.price
                                            total_earnings = totalamount * 70 / 100
                                            imageobj.total_earnings = total_earnings
                                    except Exception as e:
                                            print("Error While Setting totalEarnings in stockpaymentload: ",e)

                                except Exception as e:
                                    print("Error While Increasing Downloads in stockpaymentload: ",e)
                                else:
                                    
                                    try:
                                        imageobj.save()
                                    except Exception as e:
                                        print("Error While Saving Image obj in stockpaymentload: ",e)
                                    else:
                                        
                                        if rem_cont_pay:
                                            print("created rem_cont_pay in stockpaymentload")
                                            print("rem_cont_pay: ",rem_cont_pay)
                                            totalremamount = imageobj.price * 70 / 100
                                            rem_cont_pay.total_amount += totalremamount

                                            try:
                                                rem_cont_pay.save()
                                            except Exception as e:
                                                print("Error While Saving Remaining_Cont_Pay Obj in stockpaymentload: ",e)
                                            else:
                                                print("Saved rem_cont_pay in stockpaymentload")
                                                print("Cont_Pay = ",rem_cont_pay)
                                                print("Type Cont_Pay = ",type(rem_cont_pay))
                                                
                                                #Calculating Amount Per Image
                                                try:
                                                    amount = int(imageobj.price ) * 70 / 100
                                                    
                                                except Exception as e:
                                                    print("Error WHile to Calculating amount of image in stockpaymentload")
                                                    
                                            
                                                try:
                                                    print("Trying to create rem_cont_pay_det in stockpaymentload")
                                                    rem_cont_pay_det = Remaining_Contributor_Payment_Details.objects.create(rem_cont_pay_id=rem_cont_pay,image_id=imageobj,downloads_when_purchased=imageobj.downloads,amount=amount)
                                                except Exception as e:
                                                    print("Error While Creating Remaining_Cont_Pay_Det Obj in stockpaymentload: ",e)
                                                else:
                                                    print("Created rem_cont_pay_det in stockpaymentload")
                                                    print("rem_cont_pay_det: ",rem_cont_pay_det)
                                                    try:
                                                        print(imageobj)
                                                        print(imageobj.price)
                                                        unpaid = imageobj.price * 70 / 100
                                                        print(unpaid)
                                                        print("imageobj total unpaid earnings: ",imageobj.total_unpaid_earnings)
                                                        if imageobj.total_unpaid_earnings == None:
                                                            imageobj.total_unpaid_earnings = 0
                                                        imageobj.total_unpaid_earnings += unpaid
                                                        print("after imageobj total unpaid earnings: ",imageobj.total_unpaid_earnings)
                                                    except Exception as e:
                                                        print("Error While Setting imageobj unpaidearnings Obj in stockpaymentload in line 840: ",e)

                                                    try:
                                                        rem_cont_pay_det.save()
                                                        imageobj.save()
                                                    except Exception as e:
                                                        print("Error While Saving Remaining_Cont_Pay_Det Obj in stockpaymentload: ",e)
                                orderdetobj = Order_Details.objects.create(order_id=orderobj,image_id=imageobj) #Create OrderDetails With Current Orderid and Imageid
                                
                            except Exception as e:
                                print("Error While Getting Image Object or Creating Order Details Obj in stockpaymentload View: ",e)
                            else:#If No Error Then Save All Objects
                                orderdetobj.save()
                                try:
                                    image.delete()
                                    
                                except Exception as e:
                                    print("Error While or image in stockpaymentload: ",e)
                        try:
                            cartobj.delete()
                        except Exception as e:
                            print("Error While Deleting Cartob in stockpaymentload: ",e)

                    except Exception as e:
                        print("Error While Getting Cart Object For Cart in Finally of stockpaymentload View: ",e)
                    try:
                        #Creating New Payment Object 
                        paymobj = Payment.objects.create(pay_details_id=paydet,user_id=curuser,order_id=orderobj,total_amount=totalamount,payment_mode="DC",description="Images Payment")
                    except Exception as e:
                        print("Error While Creating Payment Object in Finally of stockpaymentload View: ",e)
                    else:
                        paymobj.save()
                except Exception as e:
                    print("Error While Creating Order Object or Saving it in Finally of stockpaymentload View: ",e)
            
                finally: #Finally Send Mail

                        subject = 'Thank You For Purchasing Images From Photostudioroom'
                        email_text = "email/stockimages/customer/imagepurchased.txt"
                        email_html = "email/stockimages/customer/imagepurchased.html"
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
        else: #Came From Direct Image Purchase(Cart Has No Images)
            try: 
                imageobj = Images.objects.get(image_id=imageparam) #Get Image Object From ImageId Got From Url
            
            except Exception as e:
                print("Error While Getting Image Object For Single Purchase in stockpaymentload View: ",e)
            else:
                try:
                    totalamount += imageobj.price 
                    #Create Order Object
                    
                    try:
                        imageobj.downloads += 1
                        try:
                                            totalamount = imageobj.downloads * imageobj.price
                                            total_earnings = totalamount * 70 / 100
                                            imageobj.total_earnings = total_earnings
                        except Exception as e:
                                            print("Error While Setting totalEarnings in stockpaymentload: ",e)
                    except Exception as e:
                        print("Error While Increasing Downloads in stockpaymentload: ",e)
                    else:
                        try:
                            imageobj.save()
                        except Exception as e:
                            print("Error While Saving Image obj in stockpaymentload: ",e)
                        else:
                            
                            try:
                                rem_cont_pay = Remaining_Contributor_Payment.objects.create(user_id=imageobj.user_id)
                            except Exception as e:
                                print("Error While Creating Remaining_Cont_Pay Obj in stockpaymentload: ",e)
                            else:
                                totalremamount = imageobj.price * 70 / 100
                                rem_cont_pay.total_amount += totalremamount
                                try:
                                    rem_cont_pay.save()
                                except Exception as e:
                                    print("Error While Saving Remaining_Cont_Pay Obj in stockpaymentload: ",e)
                                else:
                                    try:
                                                    amount = int(imageobj.price ) * 70 / 100
                                                    
                                    except Exception as e:
                                                    print("Error WHile to Calculating amount of image in stockpaymentload")
                                    try:
                                        rem_cont_pay_det = Remaining_Contributor_Payment_Details.objects.create(rem_cont_pay_id=rem_cont_pay,image_id=imageobj,downloads_when_purchased=imageobj.downloads)
                                    except Exception as e:
                                        print("Error While Creating Remaining_Cont_Pay_Det Obj in stockpaymentload: ",e)
                                    else:
                                        try:
                                                        unpaid = imageobj.price * 70 / 100
                                                        
                                                        print("imageobj total unpaid earnings: ",imageobj.total_unpaid_earnings)
                                                        if imageobj.total_unpaid_earnings == None:
                                                            imageobj.total_unpaid_earnings = 0
                                                        imageobj.total_unpaid_earnings += unpaid
                                                        print("after imageobj total unpaid earnings: ",imageobj.total_unpaid_earnings)
                                        except Exception as e:
                                                        print("Error While Setting imageobj unpaidearnings Obj in stockpaymentload: ",e)


                                        try:
                                            rem_cont_pay_det.save()
                                            imageobj.save()
                                        except Exception as e:
                                            print("Error While Saving Remaining_Cont_Pay_Det Obj in stockpaymentload: ",e)
                                
                    orderobj = Order.objects.create(user_id=curuser,Total_Amount=imageobj.price,InCart=False)
                except Exception as e:
                    print("Error While Creating Order Object For Single Purchase in stockpaymentload View: ",e)
                else:
                    orderobj.save()
                    try:
                        #Creating OrderDetails Object
                        orderdetobj = Order_Details.objects.create(order_id=orderobj,image_id=imageobj)
                    except Exception as e:
                        print("Error While Creating Order Details Object For Single Purchase in stockpaymentload View: ",e)
                    else:
                        orderdetobj.save()

            #Getting Data Sent From Form
            cardholdername = request.POST.get("card-holder")
            expmonth = request.POST.get("expmm")
            expyear = request.POST.get("expyy")
            cardnumber = request.POST.get("card-number")
            print(cardholdername,expmonth,expyear,cardnumber)
            expdate = expmonth + "/"+ expyear
            print(expdate)
            try:
                print("\n\nTrying to get paymentdetails obj in appointpaymentload")
                expdateobj = datetime.datetime.strptime(expdate, '%m/%y').date()
                print(expdateobj)
                paydet = Payment_Details.objects.get(card_no=cardnumber,card_holder_name=cardholdername,expiry_date=expdateobj)
                
            except Exception as e:
                print(e)
                print("\n\npaymentdetails obj not found in appointpaymentload")
                try:
                    print("\n\nSo trying to create payment details obj in appointpaymentload")
                    paydet = Payment_Details.objects.create(card_no=cardnumber,card_holder_name=cardholdername,expiry_date=expdateobj)
                except Exception as e:
                    print("\n\n unable to create payment details obj in appointpaymentload")
                    print(e)
                else:
                    print("\n\ncreated payment details obj now saving it in appointpaymentload")
                    paydet.save()
            finally:
                print("\n\nWE are in finally in Stockpaymentload")
                try:
                    paymobj = Payment.objects.create(pay_details_id=paydet,user_id=curuser,order_id=orderobj,total_amount=totalamount,payment_mode="DC",description="Images Payment")
                  
                except Exception as e:
                    print(e)
                else:
                    paymobj.save()
            
                finally:
                        subject = 'Thank You For Purchasing Images From Photostudioroom'
                        email_text = "email/stockimages/customer/imagepurchased.txt"
                        email_html = "email/stockimages/customer/imagepurchased.html"
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
        

    return render(request,"payment/stockpaymentloading.html")


#CONTRIBUTOR

#To Show Dashboard
def showDashboard(request):

    print("In showDashboard")
    curuser = None
    imagesbycont = None
    totalimages = None
    pendingimages = None
    pendingimagesbycont = None
    rejectedimagesbycont = None
    rejectedimages = 0
    approvedimagesbycont = None
    approvedimages = 0
    try:
        if request.user.is_authenticated:  # if user is logged in
            curuserobj = request.user  # Getting Current Logged in User

            print(curuserobj.first_name)

            try:
                curuser = User_Details.objects.get(userobj=curuserobj)
            except Exception as e:
                print(e)
            else:
                try:
                    imagesbycont = Images.objects.filter(user_id=curuser)
                    totalimages = 0
                    for timage in imagesbycont:
                        totalimages += 1
                    print("Total Images: ",totalimages)
                    pendingimagesbycont = Images.objects.filter(user_id=curuser,status="P")
                    pendingimages = 0
                    for pimages in pendingimagesbycont:
                        pendingimages += 1
                    print("Pending Images: ",pendingimages)
                    rejectedimagesbycont = Images.objects.filter(user_id=curuser,status="R")
                    rejectedimages = 0
                    for rimages in rejectedimagesbycont:
                        rejectedimages += 1
                    print("Rejected Images: ",rejectedimages)
                    approvedimagesbycont = Images.objects.filter(user_id=curuser,status="A")
                    approvedimages = 0

                    for aimages in approvedimagesbycont:
                        approvedimages += 1
                    print("Approved Images: ",approvedimages)
                except Exception as e:
                    print(e)
            
        else:
            print("not logged in")
            return render(request,"main/login.html",{"msg":"You're Logged Out"})
    except TypeError as e:
        print("Error: ", e)
    return render(request,"stockimages/contributor/dashboard.html",{"curuser":curuser,"totalimages":totalimages,"approvedimages":approvedimages,"pendingimages":pendingimages,"rejectedimages":rejectedimages,"imagesbycont":imagesbycont,"approvedimagesbycont":approvedimagesbycont,"pendingimagesbycont":pendingimagesbycont,"rejectedimagesbycont":rejectedimagesbycont})

#Earnings in Dashboard
def showEarnings(request):
    rem_cont_det_pay = None
    rem_cont_pay = None
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
    actualdownloads = 0
    actualamount = 0
        
    if request.user.is_authenticated:
            try:
                
                curuser = User_Details.objects.get(userobj=request.user)
            except Exception as e:
                print("Error While Getting User Obj in showContWiseData in StockImages",e)

            try:
                #Getting ContPay Obj If Available
                contpay = Contributor_Payment.objects.filter(user_id=curuser)
            except Exception as e:
                    
                print("Error While Getting Cont Pay in showContWiseData: ",e)

            if contpay:
                print("Contpay: ",contpay)
                for contp in contpay:
                    print("Contp: ",contp)
                    print("Contp total amount: ",contp.total_amount)
                    print("paidearningstotalamount : ",paidearningstotalamount)
                    paidearningstotalamount += contp.total_amount
                    print("after paidearningstotalamount : ",paidearningstotalamount)

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
                            paidimageids.append(imageid)

            try:
                rem_cont_pay = Remaining_Contributor_Payment.objects.filter(user_id=curuser)
            except Exception as e:
                print("Error While Getting rem cont pay in showContWiseData: ",e)
            if rem_cont_pay:
                    print("rem_cont_pay: ",rem_cont_pay)
                    for rem_pay in rem_cont_pay:
                        print("rem_pay: ",rem_pay)
                        unpaidearningstotalamount += rem_pay.total_amount
                        try:
                            rem_cont_det_pay = Remaining_Contributor_Payment_Details.objects.filter(rem_cont_pay_id=rem_pay.rem_cont_pay_id)
                        except Exception as e:
                            print("Error While Getting rem cont det pay in showContWiseData: ",e)
                        if rem_cont_det_pay:
                            for rem_det in rem_cont_det_pay:
                                try:
                                    imageobjs = Images.objects.filter(image_id=rem_det.image_id.image_id)
                                except Exception as e:
                                    print("Error While Getting Imageobjs in showContWiseData: ",e)
                                if imageobjs:
                                    for imageobj in imageobjs:
                                        unpaidimagesdict[imageobj.image_id] = rem_det.id    
                                    
                    #Get Images From unpaidimagesdict and send to template
                    for imageid,rem_det_id in unpaidimagesdict.items():
                        unpaidimageids.append(imageid)
                    

    totalEarned = paidearningstotalamount + unpaidearningstotalamount
    try:
        paidimages = Images.objects.in_bulk(paidimageids)
    except Exception as e:
        print("Error While Getting Images Objects in showContWiseData: ",e)
    try:
        unpaidimages = Images.objects.in_bulk(unpaidimageids)
    except Exception as e:
        print("Error While Getting Images Objects in showContWiseData: ",e)








    """
    curuser = None
    contpaydet = None
    contpay = None
    unpaidearnings = {}
    unpaidearningsonly = 0
    actualdownloads = 0
    actualamount = 0
    totalEarned = 0
    totalearningsfromcontpay = 0
    
    imageids = []
    images = None
    iseveryalreadypaid = True
    if request.user.is_authenticated:
        try:
            user = request.user
            curuser = User_Details.objects.get(userobj =user)
        except Exception as e:
            print("Error While Getting User Obj in paymentForContAuto in StockImages",e)
        #Get All The Approved Images Uploaded By Current Contributor
        try:
            images = Images.objects.filter(user_id=curuser.user_id,status="A")
        except Exception as e:
            print("Error While Getting Images in paymentForContAuto: ",e)
        else:#If Image Found
            
            print("Images: ",images)
            #Calculate Total Earnings
            try:
                contpay = Contributor_Payment.objects.filter(user_id=curuser)
            except Exception as e:
                print("Error While Getting Cont Pay in SHowEarnings: ",e)
            else:
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
                                print("Error While Getting contpaydet in showEarnings: ",e)
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
                        print("Error While Getting contpaydet in showEarnings: ",e)
                    else:
                        for contpd in contpaydet:
                            if contpd.image_id.image_id not in imageids:
                                imageids.append(contpd.image_id.image_id)
                            print("contpaydet: ",contpd.downloads_when_paid)
                            print("contpaydet: ",contpd.image_id.downloads)
                            if contpd.image_id.downloads > contpd.downloads_when_paid:
                                actualdownloads = contpd.image_id.downloads - contpd.downloads_when_paid
                                actualamount = actualdownloads * contpd.image_id.price
                                try:
                                    unpaidearnings[contpd.image_id.image_id] += actualamount
                                except Exception as e:
                                    print(e)
                                
                            else:
                                try:
                                    unpaidearnings[contpd.image_id.image_id] = 0
                                except Exception as e:
                                    print(e)

        unpaidearningsonly = 0
        for key,value in unpaidearnings.items():
            unpaidearningsonly += value
        totalEarned = totalearningsfromcontpay + unpaidearningsonly
    """
  

    
    return render(request,"stockimages/contributor/earnings.html",{"curuser":curuser,"totalearnings":paidearningstotalamount,"unpaidearnings":unpaidearningstotalamount,"totalearned":totalEarned,"contpaydet":contpaydet,"remcontdet":rem_cont_det_pay,"unpaidimages":unpaidimages,"paidimages":paidimages})

#TO Display ImageUpload Form
def uploadImageForm(request):
    return render(request,"stockimages/contributor/uploadimageform.html",{"isimageuploaded":"False"})

#This Function Will Convert Bytes To KB,MB,GB or TB
def convert_bytes(size):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0

    return size

#This Will Save Image Got From Upload Image Form 
def uploadImageFromCont(request):
    user = None
    user_det = None
    msg = False
    imageobj = None
    from django.core.files.storage import FileSystemStorage
    print("outside")
    if request.method == 'POST':
        print("inside")
        myfile = request.FILES['imgfromcont'] #Getting Image From Form
        print(myfile)
        if request.user.is_authenticated:
            try:
                user = User.objects.get(id=request.user.id)
                user_det = User_Details.objects.get(userobj=user)
            except Exception as e:
                print(e)
            else:
                username = user.username

        
        print("Size of file is",convert_bytes(myfile.size))
        #Saving File to a Particular Location
        fs = FileSystemStorage()
        filename = fs.save(f"stockimages/uploads/{username}/{myfile.name}", myfile)
        uploaded_file_url = fs.url(filename)

        #Adding Watermark and Saving it in Thumbnails Folder
        wmimagepath = wm(request,filepath=f'stockimages/uploads/{username}/{myfile.name}',username=username,filename=myfile.name)
        print(wmimagepath)
        imagepath = f'stockimages/uploads/{username}/{myfile.name}'

        #Fetching Image Data
        filesize = convert_bytes(myfile.size)
        from PIL import Image
        img_file = Image.open(f'media/stockimages/uploads/{username}/{myfile.name}')
        w,h = img_file.size
        print("Format is",img_file.format)
        print(f"Resolution of Image: {w} x {h} ")
        imgresolution = f'{w} x {h}'
        imgformat = img_file.format

        
        thumbimgpath = f"stockimages/thumbnails/{username}/thumb{myfile.name}"
        #Creating Image Object
        try:
            #Creating Image Object
            imageobj = Images.objects.create(user_id=user_det,size=filesize,resolution=imgresolution,image_format=imgformat,fordeveloper="TempLatestByCont",image_upload=f"stockimages/uploads/{username}/{myfile.name}",image_thumb=thumbimgpath)
        except Exception as e:
            print("Error in uploadImageFromCont While Creating Main Image Object",e)
        else:
            imageobj.save()
            print("Image Object Created Successfully")
    return render(request,"stockimages/contributor/uploadimageform.html",{"isimageuploaded":"True","imagepath":imagepath})
      
     
#This Will Save Image Details Sent From Image Upload Form
def fillDetailsUploadImageForm(request):
    """
        Created Image Object With Thumbnail Path, ACtual Image Path and User_id in another View Which is Above this View,
        Have To Update That Object In This View But How To Fetch it??, SO Saved That Image Object in Previous View with fordeveloper=TempLatestByCont, So I can Fetch it and Then Will Change it
    
    """
    categories = None
    curuser = None
    imageobj = None
    catobj = None
    try:
        categories = Categories.objects.all()
    except Exception as e:
        print(e)

    try:
        user = request.user
        curuser = User_Details.objects.get(userobj =user)
    except Exception as e:
        print(e)
    if request.method == 'POST':
        #Getting Data From The Form
        image_name = request.POST.get('imagename')
        description = request.POST.get('imagedesc')
        category = request.POST["selectcategory"]
        tags = request.POST.get('tags')

        #Getting Category Object
        try:
            catobj = Categories.objects.get(category_id=int(category))
        except Exception as e:
            print(e)
        #Adding Info To Image Object
        if curuser != None:
            try:
                #getting image object which is latest added in table
                imageobj = Images.objects.get(fordeveloper="TempLatestByCont",user_id=curuser)
            except Exception as e:
                print("Error While Getting Image Object in filldetailsuploadimageform View: ",e)
            else: #If No Error
                print("Image Object: ",imageobj)
                print("Image Resoultion: ",imageobj.resolution)
                print("Image Path: ",imageobj.image_upload)
                print("Image Thumb Path: ",imageobj.image_thumb)
                print("Image Added Date: ",imageobj.date_added)
                try:#Set Data
                    imageobj.image_name = image_name
                    imageobj.description = description
                    imageobj.category = catobj
                    imageobj.tags = tags
                    imageobj.fordeveloper = None
                    
                except Exception as e:
                    print("Error While Setting Data to Image Object in filldetailsuploadimageform View: ",e)
                else:
                        imageobj.save()
                        subject = 'Thank You For Requesting Image Approval On Photostudioroom'
                        email_text = "email/stockimages/contributor/imagerequested.txt"
                        email_html = "email/stockimages/contributor/imagerequested.html"
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
                    
                    
        print(f"Image Name: {image_name}\nDescription: {description}\nCategory: {category}\nTags: {tags}")

        return render(request,"stockimages/contributor/uploadimagesuccess.html")
    
    return render(request,"stockimages/contributor/filldetailsimageform.html",{"categories":categories})
    
#Showing Full Image to Contributor
def showImageForCont(request,imageid=None):
    print("Got Image id: ",imageid)
    imagecont = None
    curuser = None
   

    try:
        user = request.user
        curuser = User_Details.objects.get(userobj =user)
    except Exception as e:
        print(e)

    try:
        imagecont = Images.objects.get(image_id=int(imageid))
    except Exception as e:
        print(e)
    return render(request,"stockimages/contributor/showimagecont.html",{'imagecont':imagecont})
    

#edit image from dashboard by contributor
def updateImageDetails(request,imageid):
    categories = None
    catobj = None
    imagename = None
    imagedesc = None
    category = None
    tags = None
    imageobj = None
    msg = None
    if request.user.is_authenticated:
        try:
            user = request.user
            curuser = User_Details.objects.get(userobj =user)
        except Exception as e:
            print(e)
        imagetoedit = None
        try:
            #Getting Image Object Which Will be Edited
            imagetoedit = Images.objects.get(image_id=imageid)
        except Exception as e:
            print("Exception In updateImageDetails View in Stockimages Views.py:  ",e)
        print(imagetoedit)
        if request.method=='POST': 
            #Getting New Data
            imagename = request.POST['imagename']
            imagedesc = request.POST['imagedesc']
            category = request.POST["selectcategory"]
            tags = request.POST.get('tags')

            try:
                catobj = Categories.objects.get(category_id=int(category))
            except Exception as e:
                print(e)
        
            print("image desc",imagename)
            print("image name",imagedesc)
            print("length of image name",len(imagename))
            try:
            #Getting Image Object Which Will be Edited
                imageobj = Images.objects.get(image_id=imageid)
            except Exception as e:
                print("Exception In updateImageDetails View in Stockimages Views.py:  ",e)
                print(imagetoedit)
            else: #If No Error
                print("Image Object: ",imageobj)
                print("Image Resoultion: ",imageobj.resolution)
                print("Image Path: ",imageobj.image_upload)
                print("Image Thumb Path: ",imageobj.image_thumb)
                print("Image Added Date: ",imageobj.date_added)
                try:#Set Data
                    imageobj.image_name = imagename
                    imageobj.description = imagedesc
                    imageobj.category = catobj
                    imageobj.tags = tags
                    imagetoedit.status = "P"
                    imagetoedit.fordeveloper = "Edited By Contributor"
                    
                except Exception as e:
                    print("Error While Editing Data to Image Object in updateimagedetails View: ",e)
                else:
                    try:
                        imageobj.save()
                    except Exception as e:
                        print("Error While Saving Image obj in updateimagedetails: ",e)
                        msg = "Image Details Not Saved,Something Went Wrong!!"
                    else:
                        try:
            #Getting Image Object Which Will be Edited
                            imageobj = Images.objects.get(image_id=imageid)
                        except Exception as e:
                            print("Exception In updateImageDetails View in Stockimages Views.py:  ",e)
                        
                        subject = 'You Have Made Changes to Your Image On Photostudioroom'
                        email_text = "email/stockimages/contributor/imageedited.txt"
                        email_html = "email/stockimages/contributor/imageedited.html"
                        c = {
                            "email":curuser.userobj.email,
                            'domain':'127.0.0.1:8000',
                            'site_name': 'Photostudioroom',
                            "user": curuser,
                            "firstname":curuser.userobj.first_name,
                            "lastname":curuser.userobj.last_name,
                            "image":imageobj,
                            'protocol': 'http',
                            }
                        email = render_to_string(email_text, c)
                        email_html = render_to_string(email_html, c)
                        email_from = "Photostudioroom <psr.gj26.github@gmail.com>"
                        try:
                            send_mail(subject, email, email_from , [curuser.userobj.email], fail_silently=False,html_message=email_html)
                        except BadHeaderError:
                            return HttpResponse('Invalid header found.')

                        
                        msg = "Image Details Saved Successfully"
                return render(request,"stockimages/contributor/editdetailsimageform.html",{"image":imagetoedit,"categories":categories,"msg":msg})        
        try:
            categories = Categories.objects.all()
        except Exception as e:
            print("Error While Getting Categories From The Database in UpdateImageDetails: ",e)
        return render(request,"stockimages/contributor/editdetailsimageform.html",{"image":imagetoedit,"categories":categories,"msg":msg})
    else:#If User is Not Logged in Then Refer to Login Page
        return login_page(request)
    

#delete image for contributor
def deleteImageForCont(request,imageid):
    if request.user.is_authenticated:
        try:
            user = request.user
            curuser = User_Details.objects.get(userobj =user)
        except Exception as e:
            print(e)
        try:
            #Getting Image Object Which is going to be deleted
            imagetoedit = Images.objects.get(image_id=imageid)
        except Exception as e:
            print("Exception In updateImageDetails View in Stockimages Views.py:  ",e)
        print(imagetoedit)
        if request.method=='POST': # It doesn't access this condition so the updates won't occur
           
            try:
                #Delete the Image
                try:
            #Getting Image Object Which Will be Edited
                    imageobj = Images.objects.get(image_id=imageid)
                except Exception as e:
                    print("Exception In updateImageDetails View in Stockimages Views.py:  ",e)
                        
                subject = 'You Have Deleted Your Image On Photostudioroom'
                email_text = "email/stockimages/contributor/imagedeleted.txt"
                email_html = "email/stockimages/contributor/imagedeleted.html"
                c = {
                            "email":curuser.userobj.email,
                            'domain':'127.0.0.1:8000',
                            'site_name': 'Photostudioroom',
                            "user": curuser,
                            "firstname":curuser.userobj.first_name,
                            "lastname":curuser.userobj.last_name,
                            "image":imageobj,
                            'protocol': 'http',
                            }
                email = render_to_string(email_text, c)
                email_html = render_to_string(email_html, c)
                email_from = "Photostudioroom <psr.gj26.github@gmail.com>"
                try:
                    send_mail(subject, email, email_from , [curuser.userobj.email], fail_silently=False,html_message=email_html)
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')

                imagetoedit.delete()
            except Exception as e:
                print("Exception In deleteImageForCont View in Stockimages Views.py while deleting object:  ",e)
                return JsonResponse({"status": "error"}, status=500)
            

            return JsonResponse({"status": "done"}, status=200)
    else: #If User is Not Logged in Then Refer to Login Page
        return login_page(request)

