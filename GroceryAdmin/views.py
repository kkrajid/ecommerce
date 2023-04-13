from django.utils import timezone
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from Accounts.models import User
from django.contrib import auth
from Accounts.models import *
from django.core.paginator import Paginator,EmptyPage,InvalidPage
# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from datetime import datetime

from django.db.models import Q
from django.db.models import Sum
from django.utils.timezone import datetime
from matplotlib import pyplot as plt
from django.db.models import Count
from django.http import FileResponse
import io
from django.db.models.functions import TruncMonth, Coalesce


from django.http import HttpResponse
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from django.db.models import F




@never_cache
def GroceryAdmin(request):
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email,password=password)
        if user is not None and user.is_superuser:
            auth.login(request,user)
            return redirect('dashboard')
        else:
            messages.info(request,'password is incorrect')
            return render(request,'gAdmin/GeoceryAdmin.html')
    else:
        
        if not request.user.is_authenticated:
            return render(request,'gAdmin/GeoceryAdmin.html')
        else:
                return redirect('dashboard')




@never_cache
@login_required(login_url='login')
def dashboard(request):
    if request.user.is_superuser:
        fromdateOfpayment=0
        todateOfpayment=0

        if request.method == "POST":
            fromdateOfpayment = request.POST.get('fromdateOfpayment')
            todateOfpayment = request.POST.get('todateOfpayment')
        
        # Handle form validation before using form data
            if not fromdateOfpayment or not todateOfpayment:
                error_message = "Please enter valid dates."
                return render(request, 'dashboard.html', {'error_message': error_message})
        
        # Use __range operator for filtering by date range
            payment_method_counts = Order.objects.filter(created_at__range=(fromdateOfpayment, todateOfpayment)).values('payment_mode').annotate(count=Count('payment_mode'))
            order_by_months = Order.objects.filter(created_at__range=(fromdateOfpayment, todateOfpayment)).annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id'))
            sales_by_products = Orderitem.objects.filter(product__created_at__range=(fromdateOfpayment, todateOfpayment)).values('product__name').annotate(count=Count('id')).order_by('-count')
            category_counts = Orderitem.objects.filter(product__created_at__range=(fromdateOfpayment, todateOfpayment)).values('product__Category__name').annotate(count=Count('id')).order_by('-count')
        else:
            payment_method_counts = Order.objects.all().values('payment_mode').annotate(count=Count('payment_mode'))
            order_by_months = Order.objects.all().annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id'))
            category_counts = Orderitem.objects.all().values('product__Category__name').annotate(count=Count('id')).order_by('-count')
            sales_by_products = Orderitem.objects.all().values('product__name').annotate(count=Count('id')).order_by('-count')
#--------------------------------------------------------------------------------
        user_count =User.objects.filter(is_superuser=False).count()
#--------------------------------------------------------------------------------
        order_rev = Order.objects.filter(status ='Deliverd')
        total_rev = 0 
        for item in order_rev:
            total_rev+=item.total_price
#--------------------------------------------------------------------------------
        order_all =Order.objects.all()
        order_count = order_all.count()
        total_sales = 0
        for item in order_all:
            total_sales+=item.total_price
#--------------------------------------------------------------------------------
        labels = []
        data = []
        for count in payment_method_counts:
            labels.append(count['payment_mode'])
            data.append(count['count'])
#--------------------------------------------------------------------------------   
        labels1 = []
        data1 = []
        for count in category_counts:
            labels1.append(count['product__Category__name'])
            data1.append(count['count'])
#--------------------------------------------------------------------------------
        labels3 = []
        data3 = []
        for count in sales_by_products:
            labels3.append(count['product__name'])
            data3.append(count['count'])
#--------------------------------------------------------------------------------
        labels4 = []
        data4 = []

        for count in order_by_months:
            labels4.append(count['month'].strftime('%B %Y'))
            data4.append(count['count'])
#--------------------------------------------------------------------------------           
        orderitem = Orderitem.objects.all()
#--------------------------------------------------------------------------------
        context = {
            'orderitem':orderitem ,
            'labels':labels,
            'data':data,
            'labels1':labels1,
            'data1':data1,
            'data3':data3,
            'labels3':labels3,
            'data4':data4,
            'labels4':labels4,
            'user_count':user_count,
            'order_count':order_count,
            'total_sales':total_sales,
            'total_rev':total_rev,
            'fromdateOfpayment':fromdateOfpayment,
            'todateOfpayment':todateOfpayment,
        }

        return render(request,'gAdmin/dashboard.html',context)
    else:
        return redirect('Home')
    

@login_required(login_url='GroceryAdmin')
def customer(request):
    if request.user.is_superuser:
        user= User.objects.filter(is_superuser =False)
        return render(request,'gAdmin/customer.html',{'user':user})
    else:
        return redirect('home')
    

@never_cache
@login_required(login_url='GroceryAdmin')
def update_page(request,u_id):
    if request.user.is_superuser:
        user = User.objects.get(id=u_id)
        user.block = False
        user.save()
        return redirect('customer') 
    else:
        return redirect('home')



@never_cache
@login_required(login_url='GroceryAdmin')
def createuser(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            name = request.POST['name']
            email = request.POST['email']
            mobile = request.POST['mobile']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            role = request.POST['role']
            if role == 'admin':
                userRole = True
            else:
                userRole = False

            if User.objects.filter(email=email).exists():
                return render(request,'gAdmin/add_customer.html')
            elif User.objects.filter(mobile=mobile).exists():
                return render(request,'gAdmin/add_customer.html')
            elif password1 != password2:
                return render(request,'gAdmin/add_customer.html')
            else:
                if role == 'admin':
                    user = User.objects.create_user(mobile=mobile,password=password1,email=email,first_name=name,is_superuser=True)
                else:
                    user = User.objects.create_user(mobile=mobile,password=password1,email=email,first_name=name,is_superuser=True)
                user.save()
                return redirect('customer')
        return render(request,'gAdmin/add_customer.html')
    else:
        return redirect('home')
    

@never_cache
@login_required(login_url='GroceryAdmin')
def db_delete(request,userid):
    if request.user.is_superuser:
        if request.method == 'POST':
            u = User.objects.get(id = userid)
            u.block=True
            u.save()
            return redirect('customer')
    else:
        return redirect('home')





@never_cache
@login_required(login_url='GroceryAdmin')
def productUpdate(request,u_id):
    if request.user.is_superuser:
        if request.method == 'POST':
            prd = Products.objects.get(id=u_id)
            prd.name= request.POST['name']
            category_name = request.POST['category']
            category_instance = Category.objects.get(name=category_name,delete_category=False)
            prd.Category = category_instance
            prd.vendor = request.POST['Vendor']
            prd.quantity = request.POST['quantity']
            prd.original_price = request.POST['original_price']
            prd.selling_price = request.POST['selling_price']
            prd.description = request.POST['description']
            if 'image' in request.FILES and len(request.FILES['image']) > 0:
                img =  request.FILES['image']
                prd.product_image = img
                print(request.FILES['image'])
            prd.save()
            return redirect('product')
        else:
            prd = Products.objects.get(id=u_id)
            categories = Category.objects.filter(delete_category=False)
            return render(request,'gAdmin/productEdit.html',{'ob':prd,'categories':categories})
    else:
        return redirect('home')
    
    
@never_cache
@login_required(login_url='GroceryAdmin')
def pdelete(request,userid):
    if request.user.is_superuser:
        if request.method == 'POST':
            u = Products.objects.get(id = userid)
            u.delete_product =True
            u.save()

            return redirect('product')
    else:
        return redirect('home')
    

@never_cache
@login_required(login_url='GroceryAdmin')
def pcreate(request):
    if request.user.is_superuser:
        categories = Category.objects.filter(delete_category=False)
        if request.method == 'POST':
            name = request.POST['name']
            role = request.POST['role']
            vendor = request.POST['vendor']
            quantity = request.POST['quantity']
            original_price = request.POST['original_price']
            selling_price = request.POST['selling_price']
            description = request.POST['description']
            image = request.FILES['image']
            category, created = Category.objects.get_or_create(name=role,delete_category=False)
            prd = Products(name=name,
               product_image=image,
               Category=category,
               quantity=quantity,
               vendor=vendor,
               original_price=original_price,
               selling_price=selling_price,
               description=description
)
            prd.save()
            return redirect('product')
        context = {
            'categories': categories,
        }
        return render(request,'gAdmin/pcreate.html',context)
    else:
        return redirect('home')


def Trending(request,p_id):
    if request.user.is_superuser:
        user = Products.objects.get(id=p_id)
        user.trending = True
        user.save()
        return redirect('product') 
    else:
        return redirect('home')


def not_trending(request,p_id):
    if request.user.is_superuser:
        user = Products.objects.get(id=p_id)
        user.trending = False
        user.save()
        return redirect('product') 
    else:
        return redirect('home')



@login_required(login_url='GroceryAdmin')
def category(request):
    if request.user.is_superuser:
        category=Category.objects.filter(delete_category = False)
        return render(request,'gAdmin/category.html',{'category':category})
    else:
        return redirect('home')
 

@never_cache
@login_required(login_url='GroceryAdmin')
def categoryUpdate(request,u_id):
    if request.user.is_superuser:
        if request.method == 'POST':
            category = Category.objects.get(id=u_id)
            category.name= request.POST['name']
            category.description = request.POST['description']
            if 'image' in request.FILES and len(request.FILES['image']) > 0:
                img =  request.FILES['image']
                category.image = img
                print(request.FILES['image'])
            category.save()
            return redirect('category')
        else:
            category = Category.objects.get(id=u_id)
            name = str(category.image)
            return render(request,'gAdmin/categoryUpdate.html',{'category':category,'name':name})
    else:
        return redirect('home')
    

@never_cache
@login_required(login_url='GroceryAdmin')
def categorydelete(request,userid):
    if request.user.is_superuser:
        if request.method == 'POST':
            u = Category.objects.get(id=userid)
            u.delete_category = True
            u.save()
            try:
                p = Products.objects.filter(Category__id=userid)
                p.update(delete_product=True)
            except:
                pass

            return redirect('category')
    else:
        return redirect('home')




@never_cache
@login_required(login_url='GroceryAdmin')
def categorycreate(request):
   if request.user.is_superuser:
        if request.method == 'POST':
            name = request.POST['name']
            description = request.POST['description']
            if 'image' in request.FILES and len(request.FILES['image']) > 0:
                image = request.FILES['image']
            category = Category.objects.create(name=name,image=image,description=description)
            return redirect('category')
        return render(request,'gAdmin/add_catagory.html')
   else:
        return redirect('home')
   




@login_required(login_url='GroceryAdmin')
def product(request):
    if request.user.is_superuser:
        product= Products.objects.filter(delete_product=False,Category__delete_category=False)
        category=Category.objects.filter(delete_category = False)
        # paginator = Paginator(product, 5) # paginate products into 10 products per page
        # page = request.GET.get('page')
        # products = paginator.get_page(page)
        # try:
        #     page = int(request.GET.get('page','1'))
        # except:
        #     page=1
        # try:
        #     ord = paginator.page(page)
        # except(EmptyPage,InvalidPage):
        #     ord = paginator.page(paginator.num_pages)
        context = {
            'products':product,
            'category':category
        }
        return render(request,'gAdmin/product.html',context)
    else:
        return redirect('home')










@login_required(login_url='GroceryAdmin')
def add_banner(request):
     if request.user.is_superuser:
        banner=Customer_banner.objects.all()
        return render(request,'gAdmin/add_banner.html',{'banner':banner})
     else:
         return redirect('home')



@never_cache
@login_required(login_url='GroceryAdmin')
def bannerdelete(request,userid):
    if request.user.is_superuser:
        if request.method == 'POST':
            u = Customer_banner.objects.get(id = userid)
            u.delete()
            return redirect('add_banner')
    else:
        return redirect('home')



@never_cache
@login_required(login_url='GroceryAdmin')
def bannercreate(request):
   if request.user.is_superuser:
        if request.method == 'POST':
            name = request.POST['name']
            image = request.FILES['image']
            banner = Customer_banner(name=name, banner_image=image, status=False)
            banner.save()
            return redirect('add_banner')
        return render(request,'gAdmin/bannercreate.html')
   else:
        return redirect('home')







def product_view_detail(request,ord_id):

    order = Order.objects.get(id =ord_id )
    orderitem = Orderitem.objects.filter(order=order)
    orderitemOne = Orderitem.objects.filter(order=order).first()
    context = {
        'order':order,
        'orderitem':orderitem,
        'orderitemOne':orderitemOne
    }
    return render(request,'gAdmin/order_view_details.html',context)





def manage_order(request,order_id):
    if request.method == 'POST':
        ord_status = request.POST.get('option_dt')
        orders = Order.objects.get(id=order_id)
        orders.status = ord_status
        orders.updated_at =timezone.now()
        orders.save()

        if ord_status == 'Returned':
            orderite = Orderitem.objects.filter(order_id=order_id)
            for item in orderite:
                prod = Products.objects.get(id = item.product_id)
                prod.quantity = prod.quantity + item.quantity
                prod.save()
            order_history = Order.objects.get(id =order_id )
            if order_history.discount_price != order_history.total_price:
                wallet.objects.create(mode = 'Refund',amount = order_history.total_price,created_at = timezone.now(),user_id =order_history.user_id)
            else:
                wallet.objects.create(mode = 'Refund',amount = order_history.total_price,created_at = timezone.now(),user_id =order_history.user_id) 
        if ord_status == 'Cancelled':
            orderite = Orderitem.objects.filter(order_id=order_id)
            for item in orderite:
                prod = Products.objects.get(id = item.product_id)
                prod.quantity = prod.quantity + item.quantity
                prod.save()
        return redirect(reverse('product_view_detail', args=[order_id]))
    else:
        return redirect(reverse('product_view_detail', args=[order_id]))


def coupon_managment(request):
    coupon_manag = Coupon.objects.all()

    return render(request,'gAdmin/coupon.html',{'coupon_manag':coupon_manag})


    


def add_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        discount_price = request.POST.get('discountprice')
        minimum_price = request.POST.get('minimum')
        Coupon.objects.create(coupon_code = coupon_code,discount_price = discount_price,min_amount = minimum_price)
        return redirect('coupon_managment')
    return render(request,'gAdmin/add_coupon.html')


# def order_pdf(request):
#     buf  = io.BytesIO()
#     c = canvas.Canvas(buf,pagesize=letter,bottomup=0)
#     textob = c.beginText()
#     textob.setTextOrigin(inch,inch)
#     textob.setFont("Helvetica",14)
#     order = Order.objects.all()
#     lines = []
#     for order in order:
#         lines.append(order.id,order.address.first_name,order.tracking_no,order.address.phone,order.address.pincode,order.total_price,order.payment_mode,order.created_at,order.status)
#     for line in lines:
#         textob.textLine(line)

#     c.drawText(textob)
#     c.showPage()
#     c.save()
#     buf.seek(0)
#     return FileResponse(buf,as_attachment=True,filename='order.pdf')





def order_view(request):
    if request.method == 'POST':
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        order = Order.objects.filter(created_at__range=(fromdate, todate))
        context = {
            'order':order,
            'fromdate':fromdate,
            'todate':todate
        }
        return render(request,'gAdmin/orders.html',context)
    else:
        order = Order.objects.order_by('created_at','updated_at')
        context = {
            'order':order,
            
        }
    return render(request,'gAdmin/orders.html',context)


def order_pdf(request):
    if request.method == 'GET':
        fromdate = request.GET.get('fromdate')
        todate = request.GET.get('todate')
        print("------------------------------------------------------")
        print(todate)
        print("------------------------------------------------------")
        if fromdate != '' and todate != '':
            orders =  Order.objects.filter(created_at__range=(fromdate, todate))
            lines = [['ID', 'First Name', 'Tracking No.', 'Phone', 'Pincode', 'Total Price', 'Payment Mode', 'Created At', 'Status']]
            for order in orders:
                lines.append([order.id, order.address.first_name, order.tracking_no, order.address.phone, order.address.pincode, order.total_price, order.payment_mode,order.created_at.strftime('%Y-%m-%d'), order.status])
            table = Table(lines, colWidths=[40, 65, 65, 65, 50, 65, 80, 65, 80], rowHeights=30)
            table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.green),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                                    ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                                    ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                                    ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            table.wrapOn(p, A4[0]-40, A4[1]-30)
            table.drawOn(p, 9, A4[1]-20-len(lines)*30)
            p.showPage()
            p.save()
            buffer.seek(0)
            return FileResponse(buffer,as_attachment=True,filename="orders.pdf")
        else:
            orders = Order.objects.all()
            lines = [['ID', 'First Name', 'Tracking No.', 'Phone', 'Pincode', 'Total Price', 'Payment Mode', 'Created At', 'Status']]
            for order in orders:
                lines.append([order.id, order.address.first_name, order.tracking_no, order.address.phone, order.address.pincode, order.total_price, order.payment_mode,order.created_at.strftime('%Y-%m-%d'), order.status])
            table = Table(lines, colWidths=[40, 65, 65, 65, 50, 65, 80, 65, 80], rowHeights=30)
            table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.green),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                                    ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                                    ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                                    ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            table.wrapOn(p, A4[0]-40, A4[1]-30)
            table.drawOn(p, 9, A4[1]-20-len(lines)*30)
            p.showPage()
            p.save()
            buffer.seek(0)
            return FileResponse(buffer,as_attachment=True,filename="orders.pdf")





def logout_view(request):
    auth.logout(request)
    return redirect('GeoceryAdmin')
