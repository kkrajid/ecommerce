from django.urls import path,include
from . import views
urlpatterns = [
    path('login',views.login,name="login" ),
    path('registration',views.registration,name="registration" ),
    path('otp',views.otp,name="otp" ),
    path('mobile_verification',views.mobile_verification,name="mobile_verification" ),
    path('Password_reset',views.Password_reset,name="Password_reset" ),
    path('logout',views.logout,name="logout" ),

    path('Myaccounts', views.Myaccounts,name="Myaccounts" ),

    path('Myaddress', views.Myaddress,name="Myaddress" ),
    path('add_address', views.add_address,name="add_address" ),
    path('delete_address/<int:add_id>', views.delete_address,name="delete_address" ),
    path('update_address/<int:up_id>', views.update_address,name="update_address" ),
    


    # path('add_address',views.add_address,name="add_address" ),

    # path('Myaddress/<int:addressId>', views.DeleteMyaddress,name="Myaddress" ),
    # path('Myaddress/<int:editaddress>', views.EditMyaddress,name="Myaddress" ),
]
