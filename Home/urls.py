from django.urls import path,include
from . import views
urlpatterns = [
    path('', views.Home,name="Home" ),
    path('Categories', views.Categories,name="Categories" ),
    path('Categories/<str:name>', views.CategoriesView,name="Categories" ),
    path('Categories/<str:categoryName>/<str:productName>', views.ProductDetails,name="ProductDetails" ),
    
    path('add_to_cart', views.add_to_cart,name="add_to_cart" ),
    path('Cart_page', views.Cart_page,name="Cart_page" ),

    # path('Cart_page_count', views.Cart_page_count,name="Cart_page_count" ),

    path('delete_cart_item', views.delete_cart_item,name="delete_cart_item" ),
    path('update_cart', views.update_cart,name="update_cart" ),

    path('default_set/<int:def_id>', views.default_set,name="default_set" ),
    
    path('checkout', views.checkout,name="checkout" ),
    path('checkout_add_address', views.checkout_add_address,name="checkout_add_address" ),
    path('placeorder', views.placeorder,name="placeorder" ),

    path('cancel_order/<int:order_id>', views.cancel_order,name="cancel_order" ),
    path('returnorder/<int:order_id>', views.returnorder,name="returnorder" ),

    path('my_orders', views.my_orders,name="my_orders" ),
    path('orderview/<str:tracking_no>', views.orderview,name="orderview" ),
    path('successful',views.successful,name="successful" ),

    path('proceed_to_pay', views.razorpay,name="proceed_to_pay" ),

    path('product_list', views.product_list,name="product_list" ),
    
    path('searchproduct',views.searchproduct,name="searchproduct" ),

    path('allproducts', views.allproducts,name="allproducts" ),

    path('walletDetails', views.walletDetails,name="walletDetails" ),

    path('pdf_invoice/<str:tracking_no>', views.pdf_invoice,name="pdf_invoice" ),


    path('base', views.base,name="base" ),


    path('listing', views.listing,name="listing" ),
    

    path('coupon_discount',views.coupon_discount,name="coupon_discount" ),










   
   



    


    

    
    
    
    

    


    



    
 
]
