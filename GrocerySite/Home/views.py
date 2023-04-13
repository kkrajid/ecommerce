from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from Accounts.models import User
from Accounts.models import *
from django.contrib import messages
import json
import random
from django.shortcuts import get_object_or_404
# Create your views here.

@login_required(login_url='login')
def Home(request):
    count = cartItems.objects.filter(user=request.user).count()
    email = request.user.email
    user = User.objects.get(email=email)
    category = Category.objects.filter(status=0)
    products = Products.objects.all().filter(trending=1)[:8]
    banner = Customer_banner.objects.all().filter(status=0)
    return render(request,'Pages/index.html',{"category":category ,"products":products, "banner":banner,'user':user,'count':count})

@login_required(login_url='login')
def Categories(request):
    category = Category.objects.filter(status=0)
    return render(request,'Pages/categories.html',{'category':category})


@login_required(login_url='login')
def CategoriesView(request,name):
    if (Category.objects.filter(status=0,name=name)):
        products = Products.objects.filter(Category__name=name)
        return render(request,'product/products.html',{'products':products,'category':name})
    else:
        messages.warning(request,"No Such Category Found")
        return redirect('Categories')

@login_required(login_url='login')   
def ProductDetails(request,categoryName,productName):
    count = cartItems.objects.filter(user=request.user).count()
    if (Category.objects.filter(status=0,name=categoryName)):
        if(Products.objects.filter(name=productName,status=0)):
            products =Products.objects.filter(name=productName,status=0).first()
            return render(request,'product/productDetails.html',{'products':products,'count':count})
        else:
            messages.warning(request,"No Such Product Found")
            return redirect('CategoriesView')
    else:
        messages.warning(request,"No Such Category Found")
        return redirect('Categories')



@login_required
def add_to_cart(request):
    count = cartItems.objects.filter(user=request.user).count()
    if request.method == 'POST':
        if request.user.is_authenticated:
            prod_id = int(request.POST.get('product_id'))
            product_check = Products.objects.get(id = prod_id)
            if product_check:
                if cartItems.objects.filter(user = request.user.id, products_id = prod_id):
                    response = {
                        'state':True,
                        'message':'Product Already in Cart',
                        'count':count
                    }
                    return JsonResponse(response)
                else:
                    prod_qty = int(request.POST.get('product_qty'))
                    if product_check.quantity >= prod_qty:
                        cartItems.objects.create(user=request.user,products_id=prod_id,product_qty=prod_qty)
                        count = cartItems.objects.filter(user=request.user).count()
                        response = {
                        'state':True,
                        'message':'Product added successfully',
                        'count':count
                    }
                        return JsonResponse(response)
                    else:
                         response = {
                        'state':True,
                        'message':'Only '+str(product_check.quantity)+'quantity available',
                        'count':count
                    }
                         return JsonResponse(response)
            else:
                 response = {
                        'state':True,
                        'message':'No such product Found',
                        'count':count
                    }
                 return JsonResponse(response)
    else:
        response = {
                        'state':True,
                        'message':'login to continue',
                        'count':count
                    }
        return JsonResponse(response)


@login_required(login_url='login')  
def Cart_page(request):
    cart_list = cartItems.objects.filter(user = request.user)
    return render(request,'product/Cart_page.html',{'cart_list':cart_list})


@login_required(login_url='login')
def delete_cart_item(request):
    if request.method == "POST":
        prod_id = int(request.POST.get('product_id'))
        if (cartItems.objects.filter(user=request.user,products_id=prod_id)):
            cartItem = cartItems.objects.get(user= request.user,products_id = prod_id)
            cartItem.delete()
            return JsonResponse({"status":"delete successfully"})
    return redirect('Cart_page')


@login_required(login_url='login')
def update_cart(request):
    if request.method == 'POST':
        prod_id = request.POST.get('product_id')
        if (cartItems.objects.filter(user=request.user,products_id=prod_id)):
            prod_qty = int(request.POST.get('product_qty'))
            cart = cartItems.objects.get(user=request.user,products_id=prod_id)
            cart.product_qty = prod_qty
            cart.save()
            response = { 'Status ':"Update Successfully" }
            return JsonResponse(response)
    return redirect('Cart_page')





@login_required(login_url='login')
def checkout(request):
    cartItem = cartItems.objects.filter(user= request.user)
    unique_addresses = Address.objects.filter(user=request.user).order_by("-defaults")
    for item in cartItem:
        if item.product_qty > item.products.quantity:
            cartItems.objects.delete(id=item.id)
    cartItemS = cartItems.objects.filter(user= request.user)
    total_price = 0  
    for item in cartItemS:
        total_price= total_price + item.products.selling_price*item.product_qty 
    context = {
        'cartItemS':cartItemS,
        'total_price':total_price,
        'adds':unique_addresses
    }       
    return render(request,'product/checkout.html',context)


@login_required(login_url='login')
def default_set(request,def_id):
    address_in = Address.objects.get(id = def_id)
    all_adds = Address.objects.filter(user=request.user)

    for address in all_adds:
        address.defaults = False
        address.save()

    address_in.defaults = True
    address_in.save()

    return redirect('checkout')


@login_required(login_url='login')
def checkout_add_address(request):
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
def placeorder(request):
    if request.method == 'POST':
        user_address = Address.objects.get(user=request.user,defaults=True)
        new_order = Order()
        new_order.user = request.user
        new_order.address=user_address
        new_order.payment_mode = request.POST.get('payment_mode')

        cart = cartItems.objects.filter(user= request.user)
        cart_total_price = 0
        for item in cart:
            cart_total_price = cart_total_price + item.products.selling_price*item.product_qty

        new_order.total_price = cart_total_price

        trackno = 'TGN'+str(random.randint(1111111,9999999))

        while Order.objects.filter(tracking_no = trackno) is None:
            trackno = 'TGN'+str(random.randint(1111111,9999999))
        new_order.tracking_no = trackno
        new_order.save()

        new_order_items = cartItems.objects.filter(user=request.user)
        for item in new_order_items:
            Orderitem.objects.create(order=new_order,product=item.products,price=item.products.selling_price,quantity=item.product_qty)

            orderproduct = Products.objects.filter(id=item.products.id).first()
            orderproduct.quantity = orderproduct.quantity - item.product_qty
            orderproduct.save()

        cartItems.objects.filter(user=request.user).delete()
        return redirect('successful')

    else:
        return redirect('Home')
    


@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter( user= request.user)
    context = {
        'orders':orders
    }
    return render(request,'Pages/my_orders.html',context)


@login_required(login_url='login')
def orderview(request,tracking_no):
    order = Order.objects.filter(tracking_no=tracking_no).filter(user=request.user).first()
    orderitem = Orderitem.objects.filter(order=order)
    context = {
        'order':order,
        'orderitem':orderitem
    }
    return render(request,'Pages/orderview.html',context)


@login_required(login_url='login')
def successful(request):
    user = User.objects.get(id=request.user.id)
    return render(request,'Pages/successful.html',{'user':user})