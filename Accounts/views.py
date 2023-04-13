import random
from django.shortcuts import render,redirect
from django.contrib import auth
from Accounts.models import *
from django.contrib import auth
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
import vonage
from django.db.models import Count
# Create your views here.


def send_otp(mobile,otp):
    client = vonage.Client(key="8b79c8c7", secret="plm3fd2e2TRhV8ug")
    sms = vonage.Sms(client)
    Mobile_No = str(91)+mobile
    print(mobile)
    responseData = sms.send_message(
        {
            "from": "Vonage APIs",
            "to": Mobile_No,
            "text": f"Enter this OTP {otp}",
        }
    )
    if responseData["messages"][0]["status"] == "0":
        print("Message sent successfully.")
    else:
        print(f"Message failed with error: {responseData['messages'][0]['error-text']}")
    return None



@never_cache
def registration(request):
    if request.user.is_authenticated:
        return redirect('Home')
    if request.method == 'POST':
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        name = request.POST.get('first_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.info(request, 'Passwords do not match')
            return render(request, 'userAccount/registration.html')

        else:
            check_user = User.objects.filter(email=email, mobile=mobile)

            if check_user:
                messages.info(request, 'User already exists')
                return render(request, 'userAccount/registration.html')

            user = User.objects.create_user(
                email=email,
                mobile=mobile,
                first_name=name,
                password=password1
            )
            user.save()

            otp = str(random.randint(1000, 9999))
            request.session['otp'] = otp
            request.session['email'] = email
            send_otp(mobile,otp)
            print(otp)
            return redirect("otp")
    return render(request, 'userAccount/registration.html')



@never_cache
def otp(request):
    if request.user.is_authenticated:
        return redirect('Home')
    
    if 'email' not in request.session or 'otp' not in request.session:
        return redirect('registration')
    
    if request.method == 'POST':
        otp_one = request.session['otp']
        otp = request.POST.get('otp')

        if otp == otp_one:
            user = User.objects.get(email=request.session['email'])
            user.mobile_verified = True
            user.save()
            return redirect('login')
        
        else:
            return render(request,'userAccount/mobile_verification.html')
        
    return render(request,'userAccount/mobile_verification.html')


@never_cache
def login(request):
    if request.user.is_authenticated:
        return redirect('Home')
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email,password=password)

        if user is not None and user.mobile_verified:
            auth.login(request,user)
            return redirect('Home')
        
        else:
            messages.info(request,'Mobile Not verified')
            return render(request,'userAccount/login.html')
    
    else:
        if not request.user.is_authenticated:
            return render(request,'userAccount/login.html')
    
        else:
            return redirect('Home')



def logout(request):
    auth.logout(request)
    return redirect('login')



def Password_reset(request):
    return render(request,'userAccount/Password_reset.html')

def mobile_verification(request):
    return render(request,'userAccount/mobile_verification.html')


@login_required(login_url='login')
def Myaccounts(request):
    count = cartItems.objects.filter(user=request.user).count()
    user = User.objects.filter(id = request.user.id)
    print(user)
    if request.method == 'POST':
        email = request.POST.get("email")
        name = request.POST.get("name")
        mobile = request.POST.get("mobile")
        User.objects.filter(id = request.user.id).update(email = email,first_name = name,mobile = mobile)
        return render(request,'userAccount/my_accounts.html',{'user':user,'count':count})
    else:
        return render(request,'userAccount/my_accounts.html',{'user':user,'count':count})


@login_required(login_url='login')
def Myaddress(request):
    count = cartItems.objects.filter(user=request.user).count()
    # duplicates = Address.objects.values('first_name', 'last_name', 'phone').annotate(count=Count('id')).filter(count__gt=1)
    # for duplicate in duplicates:
    #     Address.objects.filter(first_name=duplicate['first_name'], last_name=duplicate['last_name'], phone=duplicate['phone']).exclude(id=min(Address.objects.filter(first_name=duplicate['first_name'], last_name=duplicate['last_name'], phone=duplicate['phone']).values_list('id', flat=True))).delete()
    user = request.user
    unique_addresses = Address.objects.filter(user=request.user ,delete_address =False)
    context = {
        'adds':unique_addresses,
        'user':user,
        'count':count
    }
    return render(request,'userAccount/my_address.html',context)

@login_required(login_url='login')
def add_address(request):
    if request.method == 'POST':
        address_data = {
        'user':request.user,
        'first_name': request.POST['first_name'],
        'last_name': request.POST['last_name'],
        'email': request.POST['email'],
        'phone': request.POST['phone'],
        'address': request.POST['address'],
        'city': request.POST['city'],
        'state': request.POST['state'],
        'country': request.POST['country'],
        'pincode': request.POST['pincode']
        }
        address = Address(**address_data)
        address.save()
        return redirect('Myaddress')



@login_required(login_url='login')
def delete_address(request,add_id):
    adds = Address.objects.get(id = add_id)
    adds.delete_address = True
    adds.save()
    return redirect('Myaddress')

@login_required(login_url='login')
def update_address(request,up_id):
    if request.method == 'POST':
        adds = Address.objects.get(id=up_id)
        adds.user = request.user
        adds.first_name = request.POST['first_name']
        adds.last_name = request.POST['last_name']
        adds.email = request.POST['email']
        adds.phone = request.POST['phone']
        adds.address = request.POST['address']
        adds.city = request.POST['city']
        adds.state =  request.POST['state']
        adds.country = request.POST['country']
        adds.pincode = request.POST['pincode']
        adds.save()
        return redirect('Myaddress')
    else:
        return redirect('Myaddress')
    
    




# def add_address(request):
    # if request.method == 'POST':
    #     if request.user.is_authenticated:
    #         first_name = request.POST.get('first_name')
    #         last_name = request.POST.get('last_name')
    #         email = request.POST.get('email')
    #         phone = request.POST.get('phone')
    #         address = request.POST.get('address')
    #         city = request.POST.get('city')
    #         state = request.POST.get('state')
    #         country = request.POST.get('country')
    #         pin_code = request.POST.get('pin_code')
    #         user_address= Address.objects.create(Fname=first_name,Lname=last_name,address=address,phone=phone,email=email,city=city,state=state,country=country,pincode=pin_code)
    #         return JsonResponse({"status":"Address added Succes"})
    # return render(request,'userAccount/add_address.html')

# @login_required(login_url='login')
# def Myaddress(request):
#     user = User.objects.get(id=request.user.id)
#     address = Address.objects.filter(user=request.user)
#     if request.method == 'POST':
#         delivery_area = request.POST.get("delivery_area")
#         complete_address = request.POST.get("complete_address")
#         delivery_instructions = request.POST.get("delivery_instructions")
#         name = request.POST.get("name")
#         addressOne = Address.objects.create(
#             delivery_area = delivery_area,
#             complete_address = complete_address,
#             delivery_instructions = delivery_instructions,
#             nickname = name,
#             user = request.user
#             )
#         address = Address.objects.filter(user=request.user)
#         return render(request,'userAccount/my_address.html',{'address':address})
#     else:
#         return render(request,'userAccount/my_address.html',{'address':address})
    


# @login_required(login_url='login')
# def DeleteMyaddress(request,addressId):
#     addressE = Address.objects.get(id=addressId)
#     addressE.delete()
#     address = Address.objects.filter(user=request.user)
#     return redirect(Myaddress)

# @login_required(login_url='login')
# def EditMyaddress(request,addressId):
#     addressE = Address.objects.get(id=addressId)
#     addressE.delete()
#     address = Address.objects.filter(user=request.user)
#     return redirect(Myaddress)


    

