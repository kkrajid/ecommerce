from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from Accounts.models import User
from Accounts.models import *
from datetime import datetime
from django.contrib import messages
import json
import random
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator,EmptyPage,InvalidPage
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Q
from django.template.loader import render_to_string


@login_required(login_url='login')
def base(request):
    count = cartItems.objects.filter(user=request.user).count()
    response = {
    'state':True,
    'count':count 
    }
    return JsonResponse(response)

@login_required(login_url='login')
def Home(request):
    count = cartItems.objects.filter(user=request.user).count()
    email = request.user.email
    user = User.objects.get(email=email)
    category = Category.objects.filter(status=0,delete_category = False)
    products = Products.objects.filter(trending=1, delete_product=False, Category__delete_category=False)[:8]
    banner = Customer_banner.objects.all().filter(status=0)
    return render(request,'Pages/index.html',{"category":category ,"products":products, "banner":banner,'user':user,'count':count})




@login_required(login_url='login')
def Categories(request):
    count = cartItems.objects.filter(user=request.user).count()
    category = Category.objects.filter(status=0,delete_category =False)
    return render(request,'Pages/categories.html',{'category':category,'count':count})


@login_required(login_url='login') 
def CategoriesView(request,name):
    if (Category.objects.filter(status=0,name=name,delete_category =False)):
        products = Products.objects.filter(Category__name=name,delete_product =False,Category__delete_category=False)
        count = cartItems.objects.filter(user=request.user).count()
        return render(request,'product/products.html',{'products':products,'category':name,'count':count})
    else:
        messages.warning(request,"No Such Category Found")
        return redirect('Categories')

@login_required(login_url='login')   
def ProductDetails(request,categoryName,productName):
    count = cartItems.objects.filter(user=request.user).count()
    if (Category.objects.filter(status=0,name=categoryName,delete_category=False)):
        if(Products.objects.filter(name=productName,status=0,delete_product =False,Category__delete_category=False)):
            products =Products.objects.filter(name=productName,status=0,delete_product =False).first()
            cart = cartItems.objects.filter(user=request.user)
            cart_ids = [item.products_id for item in cart]
            return render(request,'product/productDetails.html',{'products':products,'count':count,'cart':cart_ids})
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
    for item in cart_list:
        cart = cartItems.objects.get(id = item.id)
        cart.total =cart.product_qty*cart.products.selling_price
        cart.save()
 
    total_price = 0
    for item in cart_list:
        total_price= total_price + item.products.selling_price*item.product_qty     
    return render(request,'product/Cart_page.html',{'cart_list':cart_list, 'total_price':total_price,})


@login_required(login_url='login')
def  delete_cart_item(request):
    if request.method == "POST":
        prod_id = int(request.POST.get('product_id'))
        if (cartItems.objects.filter(user=request.user,products_id=prod_id)):
            cartItem = cartItems.objects.get(user= request.user,products_id = prod_id)
            cartItem.delete()
            count = cartItems.objects.filter(user=request.user).count()
            return JsonResponse({"status":"delete successfully","count":count})
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
            cartItemS = cartItems.objects.filter(user= request.user)
            total_price = 0
            for item in cartItemS:
                total_price= total_price + item.products.selling_price*item.product_qty  
            response = {
                'total_price':total_price,
            }       
            return JsonResponse(response)
    return redirect('Cart_page')





@login_required(login_url='login')
def checkout(request):
    cartItem = cartItems.objects.filter(user=request.user)
    user_wallet = wallet.objects.filter(user = request.user)
    total_wallet_amount = 0
    for item in user_wallet:
        total_wallet_amount += item.amount

    total_price = 0
    try:
        user_address = Address.objects.get(user=request.user, defaults=True,delete_address=False)
    except Address.DoesNotExist:
        # Handle the case where there's no default address for the user
        user_address = None
    unique_addresses = Address.objects.filter(user=request.user,delete_address=False).order_by("-defaults")
    for item in cartItem:
        if item.product_qty > item.products.quantity:
            cart = cartItems.objects.filter(id=item.id)
            cart.delete()

    cartItem = cartItems.objects.filter(user=request.user)
    for item in cartItem:
        total_price = total_price + item.products.selling_price*item.product_qty

    context = {
    'cartItemS': cartItem,
    'total_price': total_price,
    'adds': unique_addresses,
    'user_address': user_address,
    'total_wallet_amount':total_wallet_amount
   }      
    return render(request, 'product/checkout.html', context)




@login_required(login_url='login')
def default_set(request,def_id):
    address_in = Address.objects.get(id = def_id,user=request.user)
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
        return redirect('checkout')




@login_required(login_url='login')
def placeorder(request):
    if request.method == 'POST':
        user_address = Address.objects.get(user=request.user,defaults=True,delete_address=False)
        new_order = Order()
        new_order.user = request.user
        new_order.address=user_address
        new_order.payment_mode = request.POST.get('payment_mode')
        new_order.payment_id = request.POST.get('payment_id')
        payment_mode = request.POST.get('payment_mode')
        cart = cartItems.objects.filter(user= request.user)
        cart_total_price = 0
        discount = 0
        for item in cart:
            cart_total_price += item.products.selling_price*item.product_qty
#------------------------------------------------------------------------------------------------
        coupon_name = request.POST.get('coupon_name')
        print('-----------------------------------------------------------')
        print(coupon_name)
        print('-----------------------------------------------------------')
        coup = Coupon.objects.filter(id=coupon_name).first()
        print(coup)
        message=0
        
        try:
            coup = Coupon.objects.filter(id=coupon_name).first()

            if coup :
                rd = Order.objects.filter(user=request.user,coupon_id =coupon_name)
                if rd:
                    message = 'Coupon already taken'
                else:
                    if cart_total_price > coup.discount_price:
                        discou =cart_total_price- coup.discount_price
                        discount = discou
                        new_order.coupon_id = int(coupon_name)
                        message = 'Coupon added'
                    else:
                        message = 'Buy above '+str(coup.discount_price)
            else:
                message = 'invalid coupon'
        except:
            pass

        # if not Coupon.objects.filter(coupon_code=coupon_name).exists():
        #     message = 'invalid coupon'
        # else:
        #     coupon_user = Coupon.objects.get(coupon_code=coupon_name)
        #     if(Order.objects.filter(user=request.user,coupon__coupon_code =coupon_name).exists()):
        #         message = 'Coupon already taken'
        #     else:
        #         if cart_total_price > coupon_user.discount_price:
        #             cart_total_price -=coupon_user.discount_price
        #             discount = cart_total_price
        #             new_order.coupon.coupon_code =coupon_name
        #             message = 'Coupon added'
        #         else:
        #             message = 'Buy above '+str(coupon_user.discount_price)
        print('-----------------------------------------------------------')
        print(message)
        print('-----------------------------------------------------------')
#------------------------------------------------------------------------------------------------
        if payment_mode == 'Wallet':
            balance = cart_total_price*-1
            time = datetime.now().time()
            wallet.objects.create(user = request.user,mode='Money out',amount=balance,created_at=time)

        if payment_mode == 'Razorpay+Wallet' or payment_mode == 'COD+Wallet':
            user_wallet = wallet.objects.filter(user = request.user)
            total_wallet_amount = 0
            for item in user_wallet:
                total_wallet_amount += item.amount
            wallet_remain = total_wallet_amount*-1
            balance = wallet_remain
            time = datetime.now().time()
            wallet.objects.create(user = request.user,mode='Money out',amount=balance,created_at=time)

        new_order.total_price = cart_total_price
        new_order.discount_price = discount

        trackno = 'TGN'+str(random.randint(1111111,9999999))

        while Order.objects.filter(tracking_no = trackno) is None:
            trackno = 'TGN'+str(random.randint(1111111,9999999))
            
        new_order.tracking_no = trackno
        new_order.created_at=datetime.now().time()
        new_order.save()
        new_order_items = cartItems.objects.filter(user=request.user)
        print(new_order_items)
        print(new_order)
        for item in new_order_items:
            rtotal = item.products.selling_price*item.product_qty
            Orderitem.objects.create(order=new_order,product=item.products,price=item.products.selling_price,quantity=item.product_qty,total=rtotal)
            orderproduct = Products.objects.filter(id=item.products.id).first()
            orderproduct.quantity = orderproduct.quantity - item.product_qty
            orderproduct.save()

        cartItems.objects.filter(user=request.user).delete()

        payMode = request.POST.get('payment_mode')
        pr_id = request.POST.get('payment_id')
        name =  user_address.first_name + ' '+  user_address.last_name
        if payMode == 'Razorpay' or payMode == 'Razorpay+Wallet' :
            responsess = {
                'product_id':pr_id,
                'name':name
            }
            print("payment done")
            return JsonResponse(responsess)
        return redirect('successful')

    else:
        return redirect('Home')

@login_required(login_url='login')  
def razorpay(request):
    cart = cartItems.objects.filter(user = request.user)
    total_price = 0
    for item in cart:
        total_price = total_price + item.products.selling_price*item.product_qty
    user_wallet = wallet.objects.filter(user = request.user)
    total_wallet_amount = 0
    for item in user_wallet:
        total_wallet_amount += item.amount
# total_price =request.session.get("Coupon_after")
    response = {
        'total_price':total_price,
        'total_wallet_amount':total_wallet_amount
    }
    return JsonResponse(response)


@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at','updated_at')
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


@login_required(login_url='login')
def cancel_order(request,order_id):
    orderite = Orderitem.objects.filter(order_id=order_id)
    for item in orderite:
        prod = Products.objects.get(id = item.product_id)
        prod.quantity = prod.quantity + item.quantity
        prod.save()
    orders = Order.objects.get(id=order_id)
    orders.status = 'Cancelled'
    orders.updated_at =timezone.now()
    orders.save()
    traking = orders.tracking_no
    return redirect('orderview',traking)

@login_required(login_url='login')
def returnorder(request,order_id):
    orders = Order.objects.get(id=order_id)
    orders.status = 'Return'
    orders.updated_at =timezone.now()
    orders.save()
    traking = orders.tracking_no
    return redirect('orderview',traking)

@login_required(login_url='login')
def product_list(request):
    products = Products.objects.filter(status = 0,delete_product =False).values_list('name',flat=True)
    productList = list(products)
    return JsonResponse(productList,safe=False)

@login_required(login_url='login')
def searchproduct(request):
    if request.method == 'POST':
        search = request.POST.get('product')
        productsList = Products.objects.filter(name__icontains=search,delete_product =False,Category__delete_category=False)

        if len(productsList) > 0:
            data = []
            for item in productsList:
                data.append({
                    'id': item.id,
                    'name': item.name,
                    'category': item.Category.name,
                    'description': item.description,
                    'image': str(item.product_image.url),
                })
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse({'error': 'No Product found...'})
    return JsonResponse({'error': 'Invalid request method.'})


        

# def allproducts(request):
#     if request.method == 'POST':
#         catag = request.POST.get('catag')
#         if catag == '':
#             products = Products.objects.all()
#             category = Category.objects.all()
#             paginator = Paginator(products,4)
#             try:
#                 page = int(request.GET.get('page','1'))
#             except:
#                 page=1
#             try:
#                 ord = paginator.page(page)
#             except(EmptyPage,InvalidPage):
#                 ord = paginator.page(paginator.num_pages)
#             context = {
#                 'products':products,
#                 'pg':ord,
#                 'category':category ,
                
#             }
#             return render(request,'product/allproducts.html',context)
#         else:
#             products = Products.objects.filter(Category__name=catag)
#             category = Category.objects.all()
#             paginator = Paginator(products,4)
#             try:
#                 page = int(request.GET.get('page','1'))
#             except:
#                 page=1
#             try:
#                 ord = paginator.page(page)
#             except(EmptyPage,InvalidPage):
#                 ord = paginator.page(paginator.num_pages)
#             context = {
#                 'products':products,
#                 'pg':ord,
#                 'category':category ,
                
#             }
#             return render(request,'product/allproducts.html',context)

#     else:    
#         products = Products.objects.all()
#         category = Category.objects.all()
#         paginator = Paginator(products,4)
#         try:
#             page = int(request.GET.get('page','1'))
#         except:
#             page=1
#         try:
#             ord = paginator.page(page)
#         except(EmptyPage,InvalidPage):
#             ord = paginator.page(paginator.num_pages)
#         context = {
#             'products':products,
#             'pg':ord,
#             'category':category ,
            
#         }
#         return render(request,'product/allproducts.html',context)
    



# def allproducts(request):
#     products = Products.objects.all()
#     catag = Category.objects.all()

#     category = request.GET.get('category')
#     if category:
#         products = Products.objects.filter(Category__name=category)

#     # Filter products based on price range
#     min_price = request.GET.get('min_price')
#     max_price = request.GET.get('max_price')
#     if min_price and max_price:
#         products = Products.objects.filter(selling_price__gte=min_price, selling_price__lte=max_price)

#     # Sort products based on price
#     sort_by_price = request.GET.get('sort_by_price')
#     if sort_by_price == 'asc':
#         products = Products.objects.order_by('selling_price')
#     elif sort_by_price == 'desc':
#         products = Products.objects.order_by('-selling_price')

#     context = {
#         'products': products,
#         'category':catag

#     }
#     return render(request,'product/allproducts.html', context)


@login_required(login_url='login')
def allproducts(request):
    categories = Category.objects.filter(delete_category=False)
    selected_category_id = request.GET.get('category_id')
    order_by_price = request.GET.get('order_by_price')
    if selected_category_id and selected_category_id != 'all':
        selected_category = get_object_or_404(Category, id=selected_category_id)
        product = Products.objects.filter(trending=1, delete_product=False, Category=selected_category)
    else:
        product = Products.objects.filter(trending=1, delete_product=False, Category__delete_category=False)
    if order_by_price:
        if order_by_price == 'asc':
            product = product.order_by('selling_price')
        elif order_by_price == 'desc':
            product = product.order_by('-selling_price')
            
    paginator = Paginator(product, 8)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    try:
        ord = paginator.page(page)
    except (EmptyPage, InvalidPage):
        ord = paginator.page(paginator.num_pages)
    context = {
        'products': products,
        'pg': ord,
        'categories': categories,
        'selected_category_id': selected_category_id,
    }
    if request.method=='POST':
        products_html = render_to_string('Pages/products.html', {'products': products})
        return JsonResponse({'products_html': products_html})
    return render(request, 'product/allproducts.html', context)



@login_required(login_url='login')
def walletDetails(request):
    user_wallet = wallet.objects.filter(user = request.user)
    total_amount = 0
    for item in user_wallet:
        total_amount += item.amount
    context ={
        'user_wallet':user_wallet,'total_amount':total_amount
    }
    return render(request,'userAccount/wallet.html',context)


@login_required(login_url='login')
def pdf_invoice(request,tracking_no):
    order = Order.objects.filter(tracking_no=tracking_no).filter(user=request.user).first()
    orderitem = Orderitem.objects.filter(order=order)
    template_path = 'product/pdfinvoice.html'
    context = {
        'order': order,
        'orderitem': orderitem
    }
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Invoice.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response











@login_required(login_url='login')
def listing(request):
    categories = Category.objects.filter(delete_category=False)
    selected_category_id = request.GET.get('category_id')
    order_by_price = request.GET.get('order_by_price')
    if selected_category_id and selected_category_id != 'all':
        selected_category = get_object_or_404(Category, id=selected_category_id)
        product = Products.objects.filter(delete_product=False, Category=selected_category)
    else:
        product = Products.objects.filter(delete_product=False, Category__delete_category=False)
    if order_by_price:
        if order_by_price == 'asc':
            product = product.order_by('selling_price')
        elif order_by_price == 'desc':
            product = product.order_by('-selling_price')
            
    paginator = Paginator(product, 8)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    try:
        ord = paginator.page(page)
    except (EmptyPage, InvalidPage):
        ord = paginator.page(paginator.num_pages)
    context = {
        'products': products,
        'pg': ord,
        'categories': categories,
        'selected_category_id': selected_category_id,
    }
    if request.method=='POST':
        products_html = render_to_string('Pages/products.html', {'products': products})
        return JsonResponse({'products_html': products_html})
    return render(request, 'Pages/listing.html', context)





def coupon_discount(request):
    if request.method  == 'POST':
        if request.POST.get('couponValue') != 'NaN':
            val = request.POST.get('couponValue')
            print('------------------------------------')
            print(val)
            print('------------------------------------')
            cart = cartItems.objects.filter(user = request.user)
            total_price = 0
            message=0
            for item in cart:
                total_price = total_price + item.products.selling_price*item.product_qty
            if not  Coupon.objects.filter(coupon_code=val).exists():
                message = 'invalid coupon'
            else:
                coupon_user = Coupon.objects.get(coupon_code=val)
                if(Order.objects.filter(coupon__coupon_code =coupon_user.coupon_code).exists()):
                    message = 'Coupon already taken'
                else:
                    coupon_user = Coupon.objects.get(coupon_code=val)
                    if total_price > coupon_user.discount_price:
                        total_price -=coupon_user.discount_price
                        message = 'Coupon added'
                    else:
                        message = 'Buy above '+str(coupon_user.discount_price)

            total = {
                'total_price':total_price,
                'message':message,
                'coupon_num' :coupon_user.id
            }
            return JsonResponse(total)
        else:
            cart = cartItems.objects.filter(user = request.user)
            total_price = 0
            for item in cart:
                total_price = total_price + item.products.selling_price*item.product_qty
            total = {
                'total_price':total_price
            }
            return JsonResponse(total)


# products = Products.objects.filter(trending=1, delete_product=False, Category__delete_category=False)[:8]

#7/04/2023 change  checkout 

# @login_required(login_url='login')
# def checkout(request):
#     cartItem = cartItems.objects.filter(user=request.user)
#     total_price = 0
#     try:
#         user_address = Address.objects.get(user=request.user, defaults=True,delete_address=False)
#     except Address.DoesNotExist:
#         # Handle the case where there's no default address for the user
#         user_address = None
#     unique_addresses = Address.objects.filter(user=request.user,delete_address=False).order_by("-defaults")
#     for item in cartItem:
#         if item.product_qty > item.products.quantity:
#             cartItems.objects.delete(id=item.id)
#     # if request.method == 'POST':
#     #     coupon_id  = request.POST.get('coupon')
#     #     coupon_obj = Coupon.objects.filter(coupon_code=coupon_id).first()
#     #     if not coupon_obj:
#     #         messages.warning(request, 'Invalid Coupon')
#     #         return redirect(request.META.get('HTTP_REFERER'))
#     #     cart_obj = cartItems.objects.filter(user=request.user).first()
#     #     if cart_obj.coupon_id == coupon_obj.id:
#     #         messages.warning(request, 'Coupon Already Exists')
#     #         return redirect(request.META.get('HTTP_REFERER'))
#     #     if coupon_obj.is_expired == False:
#     #         cart_obj.coupon = coupon_obj
#     #         cart_obj.save()
#     #         coupon_obj.is_expired = True
#     #         coupon_obj.save()
#     #         messages.success(request, 'Coupon Applied')
#     #     else:
#     #         messages.success(request, 'Coupon expired')
 
#     # if cart_obj.coupon_id == None:
#     #     for item in cartItemS:
#     #         total_price = total_price + item.products.selling_price*item.product_qty
#     #         request.session["Coupon_ids"] = total_price
#     #         request.session["Coupon_after"] = total_price
#     #         try:
#     #             coupon_obj = Coupon.objects.get(id = cart_obj.coupon_id)
#     #             total_price = total_price-coupon_obj.discount_price
#     #             request.session["Coupon_after"] = total_price
#     #         except:
#     #             pass
           

#     # else:
#     #     coupon_obj = Coupon.objects.get(id = cart_obj.coupon_id)
#     #     total_price=request.session.get("Coupon_ids")
#     #     total_price = total_price-coupon_obj.discount_price
#     #     request.session["Coupon_after"] = total_price

#     for item in cartItem:
#         total_price = total_price + item.products.selling_price*item.product_qty

#     context = {
#     'cartItemS': cartItem,
#     'total_price': total_price,
#     'adds': unique_addresses,
#     'user_address': user_address,
#    }      
#     return render(request, 'product/checkout.html', context)
