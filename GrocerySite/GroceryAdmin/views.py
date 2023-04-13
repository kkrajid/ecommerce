from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from Accounts.models import User
from django.contrib import auth
from Accounts.models import Products,Category,Customer_banner
# Create your views here.

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
@login_required(login_url='admin1')
def dashboard(request):
    if request.user.is_superuser:
        return render(request,'gAdmin/dashboard.html')
    else:
        return redirect('home')
    

@login_required(login_url='admin1')
def customer(request):
    if request.user.is_superuser:
        user= User.objects.all().values()
        return render(request,'gAdmin/customer.html',{'user':user})
    else:
        return redirect('home')
    

@never_cache
@login_required(login_url='admin1')
def update_page(request,u_id):
    if request.user.is_superuser:
        if request.method == 'POST':
            user = User.objects.get(id=u_id)
            user.first_name= request.POST['name']
            user.email = request.POST['email']
            user.mobile = request.POST['mobile']
            user.save()
            return redirect('customer')
        else:
            user = User.objects.get(id=u_id)
            return render(request,'gAdmin/update_page.html',{'user':user})
    else:
        return redirect('home')



@never_cache
@login_required(login_url='admin1')
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
@login_required(login_url='admin1')
def db_delete(request,userid):
    if request.user.is_superuser:
        if request.method == 'POST':
            u = User.objects.get(id = userid)
            u.delete()
            return redirect('customer')
    else:
        return redirect('home')





@never_cache
@login_required(login_url='admin1')
def productUpdate(request,u_id):
    if request.user.is_superuser:
        if request.method == 'POST':
            prd = Products.objects.get(id=u_id)
            prd.name= request.POST['name']
            prd.Category.name = request.POST['category']
            prd.vendor = request.POST['Vendor']
            prd.quantity = request.POST['quantity']
            prd.original_price = request.POST['original_price']
            prd.selling_price = request.POST['selling_price']
            prd.description = request.POST['description']
            img =  request.FILES['image']
            prd.product_image = img
            print(request.FILES['image'])
            prd.save()
            return redirect('product')
        else:
            prd = Products.objects.get(id=u_id)
            return render(request,'gAdmin/productEdit.html',{'ob':prd})
    else:
        return redirect('home')
    
    
@never_cache
@login_required(login_url='admin1')
def pdelete(request,userid):
    if request.user.is_superuser:
        if request.method == 'POST':
            u = Products.objects.get(id = userid)
            u.delete()
            return redirect('product')
    else:
        return redirect('home')
    

@never_cache
@login_required(login_url='admin1')
def pcreate(request):
    if request.user.is_superuser:
        categories = Category.objects.all()
        if request.method == 'POST':
            name = request.POST['name']
            role = request.POST['role']
            vendor = request.POST['vendor']
            quantity = request.POST['quantity']
            original_price = request.POST['original_price']
            selling_price = request.POST['selling_price']
            description = request.POST['description']
            image = request.FILES['image']
            category, created = Category.objects.get_or_create(name=role)
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


@login_required(login_url='admin1')
def category(request):
    if request.user.is_superuser:
        category=Category.objects.all()
        return render(request,'gAdmin/category.html',{'category':category})
    else:
        return redirect('home')
 

@never_cache
@login_required(login_url='admin1')
def categoryUpdate(request,u_id):
    if request.user.is_superuser:
        if request.method == 'POST':
            category = Category.objects.get(id=u_id)
            category.name= request.POST['name']
            category.description = request.POST['description']
            img =  request.FILES['image']
            category.image = img
            print(request.FILES['image'])
            category.save()
            return redirect('category')
        else:
            category = Category.objects.get(id=u_id)
            return render(request,'gAdmin/categoryUpdate.html',{'category':category})
    else:
        return redirect('home')
    

@never_cache
@login_required(login_url='admin1')
def categorydelete(request,userid):
    if request.user.is_superuser:
        if request.method == 'POST':
            u = Category.objects.get(id = userid)
            u.delete()
            return redirect('category')
    else:
        return redirect('home')




@never_cache
@login_required(login_url='admin1')
def categorycreate(request):
   if request.user.is_superuser:
        if request.method == 'POST':
            name = request.POST['name']
            description = request.POST['description']
            image = request.FILES['image']
            if  Category.objects.filter(name=name).exists():
                print('already exist')
            else:
                category = Category(name=name,image=image,description=description)
                category.save()
            return redirect('category')
        return render(request,'gAdmin/add_catagory.html')
   else:
        return redirect('home')
   




@login_required(login_url='admin1')
def product(request):
    if request.user.is_superuser:
        product= Products.objects.all()

        return render(request,'gAdmin/product.html',{'objs':product})
    else:
        return redirect('home')










@login_required(login_url='admin1')
def add_banner(request):
     if request.user.is_superuser:
        banner=Customer_banner.objects.all()
        return render(request,'gAdmin/add_banner.html',{'banner':banner})
     else:
         return redirect('home')



@never_cache
@login_required(login_url='admin1')
def bannerdelete(request,userid):
    if request.user.is_superuser:
        if request.method == 'POST':
            u = Customer_banner.objects.get(id = userid)
            u.delete()
            return redirect('add_banner')
    else:
        return redirect('home')



@never_cache
@login_required(login_url='admin1')
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



def logout_view(request):
    auth.logout(request)
    return redirect('GeoceryAdmin')
