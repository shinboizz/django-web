from django.shortcuts import render,redirect,HttpResponse
##from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth  import authenticate,  login, logout
from django.contrib import messages
from .models import Product,Contact,Orders,OrderUpdate
from math import ceil
import json
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
##from PayTm import Checksum


# Create your views here.
##MERCHANT_KEY = '7302-5759-5793'

def index(request):
    allProds = []
    catProds = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catProds}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds}
    return render(request, 'shop/index.html', params)

def searchMatch(query, item):
    query=query.lower()
    if query in item.product_name.lower() or query in item.category.lower() or query in item.desc.lower() or query in item.sub_category.lower():
        return True
    else:
        return False

def search(request):
    query= request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod=[item for item in prodtemp if searchMatch(query, item)]
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod)!= 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg":""}
    if len(allProds)==0 or len(query)<4:
        params={'msg':"Please make sure to enter relevant search query"}
    return render(request, 'shop/search.html', params)

def about(request):
    return render(request,'shop/about.html')



def contact(request):
    thank = False
    if request.method=="POST":

        name = request.POST.get('name','')
        email = request.POST.get('email','')
        phone = request.POST.get('phone','')
        desc = request.POST.get('desc','')
        print(name,email,phone,desc)
        contact = Contact(name=name,email=email,phone=phone,desc=desc)
        contact.save()
        thank = True

    return render(request,'shop/contact.html', {'thank' : thank})

def productview(request,myid):
    #fetch the product using the id
    product = Product.objects.filter(id=myid)
    print(product)
    return render(request,'shop/productview.html',{'product':product[0]})


def checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone,amount=amount)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        thank = True
        id = order.order_id
        #return render(request, 'shop/checkout.html', {'thank':thank, 'id': id})
        #request paytm to tranfer the amount to your account after payment by user
        ##param_dict = {

            ##'MID': '7302-5759-5793',
            ##'ORDER_ID': str(order.order_id),
            ##'TXN_AMOUNT': str(amount),
            ##'CUST_ID': email,
            ##'INDUSTRY_TYPE_ID': 'Retail',
            ##'WEBSITE': 'WEBSTAGING',
            ##'CHANNEL_ID': 'WEB',
            ##'CALLBACK_URL': 'http://127.0.0.1:8000/shop/handlerequest/',

        #}
       # param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        #return render(request, 'shop/paytm.html', {'param_dict': param_dict})

    return render(request, 'shop/checkout.html')

def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"no item"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'shop/tracker.html')


##@csrf_exempt
##def handlerequest(request):
    ##paytm will send you post request here
    ##form = request.POST
    ##response_dict = {}
    #for i in form.keys():
       #response_dict[i] = form[i]
        #if i == 'CHECKSUMHASH':
            #checksum = form[i]

    #verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    #if verify:
        #if response_dict['RESPCODE'] == '01':
            #print('order successful')
        #else:
            #print('order was not successful because' + response_dict['RESPMSG'])
    #return render(request, 'shop/paymentstatus.html', {'response': response_dict})

def simpleCheckout(request):
    oderz = Orders.objects.all()
    context = {'oderz': oderz}

    return render(request, 'shop/simple_checkout.html',context)





def paymentComplete(request):
        body = json.loads(request.body)
        print('BODY:', body)
        product = Product.objects.get(id=body['productId'])
        Orders.objects.create(
            product=product
            )

        return JsonResponse('Payment completed!', safe=False)


def handleSignUp(request):
    if request.method == "POST":
        # Get the post parameters
        username = request.POST['username']
        email = request.POST['email']
        fname = request.POST['fname']
        lname = request.POST['lname']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        # check for errorneous input
        if len(username) > 10:
            messages.error(request, " Your user name must be under 10 characters")
            return redirect('ShopHome')

        if not username.isalnum():
            messages.error(request, " User name should only contain letters and numbers")
            return redirect('ShopHome')
        if (pass1 != pass2):
            messages.error(request, " Passwords do not match")
            return redirect('ShopHome')



        # Create the user
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()
        messages.success(request, " Your account has been successfully created")
        return redirect('ShopHome')

    else:
        return HttpResponse("404 - Not found")



def handleLogin(request):

    if request.method=="POST":
        # Get the post parameters
        loginusername = request.POST['loginusername']
        loginpassword = request.POST['loginpassword']

        user = authenticate(username = loginusername , password = loginpassword)
        if user is not None:
            login(request , user)
            messages.success(request, "Successfully Logged In")
            return redirect('ShopHome')
        else:
            messages.error(request, "Invalid credentials! Please try again")
            return redirect('ShopHome')

    return HttpResponse('404- not found')



def handleLogout(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect('ShopHome')