from django.urls import path,include
from . import views
urlpatterns = [
    path('GroceryAdmin', views.GroceryAdmin,name='GeoceryAdmin'),

    path('dashboard', views.dashboard,name='dashboard'),

    path('customer', views.customer,name='customer'),
    path('createuser', views.createuser,name='createuser'),
    path('update_page/<int:u_id>', views.update_page,name='update_page'),
    path('db_delete/<int:userid>', views.db_delete,name='db_delete'),

    path('category', views.category,name='category'),
    path('categorycreate', views.categorycreate,name='categorycreate'),
    path('categorydelete/<str:userid>', views.categorydelete,name='categorydelete'), 
    path('categoryUpdate/<int:u_id>', views.categoryUpdate,name='categoryUpdate'),

    path('product', views.product,name='product'),
    path('pcreate', views.pcreate,name='pcreate'),
    path('pdelete/<int:userid>', views.pdelete,name='pdelete'),
    path('productUpdate/<int:u_id>', views.productUpdate,name='productUpdate'),
    
    path('add_banner', views.add_banner,name='add_banner'),
    path('bannercreate', views.bannercreate,name='bannercreate'),
    path('bannerdelete/<int:userid>', views.bannerdelete,name='bannerdelete'),

    path('logout_view', views.logout_view,name='logout_view'),
]
