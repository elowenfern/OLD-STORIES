from django.contrib import admin
from django.urls import path
from app1 import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('',views.index,name='index'),
    #shop
    path('shop/',views.shop,name='shop'),
    path('shop/<int:category_id>/', views.shop, name='products_by_category'),
    path('product_detials/<int:id>/',views.pdt_detials,name='pdt_detials'),
    path('display_variations/',views.display_variations,name='display_variations'),
    path('display_variations/<int:variation_id>/', views.display_variations, name='display_variations'),
    path('color/',views.color,name='color'),
    path('about/',views.about,name='about'),
    #category page
   
    #salesreprt
    path('report-pdf-order/', views.report_pdf_order, name='report_pdf_order'),
    path('chart-demo/', views.chart_demo, name='chart_demo'),
    path('report_generator/<int:id/',views.report_generator,name='report_generator'),
    #wallet
    path('wallet/',views.wallet,name='wallet'),
    #cart
    path('cart/',views.cart,name='cart'),
    path('add_to_cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:variationId>/', views.update_cart, name='update_cart'),
    path('order_placed/',views. order_placed,name='order_placed'),
    path('checkout/',views.check_out,name='check_out'),
    #razorpay
    path('proceed-to-pay',views.proceedtopay,name='proceedtopay'),
    path('razorpay/',views.razorpay,name='razorpay'),
    path('success/', views.success, name='success'),
    #contact
    path('contact/',views.contact,name='contact'),
    #wishlist
    path('wish/',views.wish,name='wish'),
    path('add_to_wishlist/<int:id>/',views.add_to_wishlist,name='add_to_wishlist'),
    path('remove_to_wishlist<int:id>/',views.remove_from_wishlist,name='remove_from_wishlist'),

    path('signup/',views.signup,name='signup'),
    path('verify/',views.verify_signup,name='verify_signup'),
    path('loginpage/',views.loginpage,name='loginpage'),
    path('forget/',views.forgotpassword,name='forgotpassword'),
    path('reset/',views.reset_password,name='reset_password'),
    path('logout',views.logoutpage,name='logoutpage'),
    # profile
    path('profile/',views.profile,name='profile'),
    path('update_profile/',views.update_profile,name='update_profile'),
    path('changepassword/',views.changepassword,name='changepassword'),
    path('customorder/',views.customer_order,name='customer_order'),
    path('order_detials/<int:id>',views.order_details,name='order_details'),
    path('cancelorder/<int:id>',views.cancel_order,name='cancel_order'),
    path('returnorder/<int:id>',views.return_order,name='return_order'),
    # address
    path('address/',views.address,name='address'),
    path('add_address/',views.add_address,name='add_address'),
    path('edit_address/<int:id>/',views.edit_address, name='edit_address'),
    path('delete_address/<int:id>/',views.delete_address, name='delete_address'),
    # shipping address
    path('shipping_address/',views.shipping_address,name='shipping_address'),
    path('shipping_add_address/',views.shipping_add_address,name='shipping_add_address'),
    path('shipping_edit_address/<int:id>/',views.shipping_edit_address, name='shipping_edit_address'),
    path('shipping_delete_address/<int:id>/',views.shipping_delete_address, name='shipping_delete_address'),
    #admin
    path('adminn/',views.admin,name='admin'),
    path('adminlogout/',views.adminlogout,name='adminlogout'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('customer/',views.customer,name='customer'),
    #category
    path('category/',views.category,name='category'),
    path('addcategory/',views.addcategory,name='addcategory'),
    path('editcategory/<int:category_id>/',views.editcategory,name='editcategory'),
    path('updatecategory/<int:category_id>/',views.update_category,name='update_category'),
    path('deletecategory/<int:category_id>/',views.delete_category,name='delete_category'),
    #sub category
    path('subcategory/',views.sub_category,name='sub_category'),
    path('addsubcategory/',views.add_sub_category,name='add_sub_category'),
    path('editsubcategory/<int:sub_category_id>/',views.edit_sub_category,name='edit_sub_category'),
    path('updatesubcategory/<int:sub_category_id>/',views.update_sub_category,name='update_sub_category'),
    path('deletesubcategory/<int:sub_id>/',views.delete_sub_category,name='delete_sub_category'),
    #search
    path('search/',views.search,name='search'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    #invoice
    path('invoice/<int:id>',views.invoice,name='invoice'),
    path('order/',views.order,name='order'),
    path('update_order/',views.update_order,name='update_order'),
    #variations
    # path('variations/',views.variations,name='variations'),
    path('variations/<int:product_id>/',views.variations,name='variations'),
    path('addvariation/',views.add_variation,name='add_variation'),
    path('editvariation/<int:id>/',views.edit_variation,name='edit_variation'),
    path('update_variation/<int:id>/',views.update_variation,name='update_variations'),
    path('delete_variation/<int:id>',views.delete_variation,name='delete_variation'),
    path('restore_variation/<int:variation_id>/', views.restore_variation, name='restore_variation'),
    #product
    path('product/',views.product,name='product'),
    path('addproduct/',views.addproduct,name='addproduct'),
    path('product/<int:product_id>/edit_product/',views.editproduct,name='editproduct'),
    path('product/<int:product_id>/update_product/',views.update,name='update'),
    path('product/<int:product_id>/delete_product/',views.delete_product,name='delete_product'),
    path('restore_product/<int:product_id>/', views.restore_product, name='restore_product'),
    #section
    path('section/',views.section, name = 'section'),
    path('addsection/',views.addsection,name= 'add_section'),
    path('section/<int:id>/update_section/', views.update_section, name='update_section'),
    path('section/<int:section_id>/delete/', views.delete_section, name='delete_section'),
    path('section/<int:section_id>/edit/', views.editsection, name='edit_section'),
    #coupon
    path('coupon/',views.coupon,name = 'coupon'),
    path('addcoupon/',views.addcoupon,name='addcoupon'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('coupon/<int:coupon_id>/edit/', views.editcoupon, name='edit_coupon'), 
    path('coupon/<int:id>/update_coupon/', views.update_coupon, name='update_coupon'),
    path('coupon/<int:coupon_id>/delete/', views.delete_coupon, name='delete_coupon'),
    path('block/<int:customer_id>/',views.block_customer,name='block_customer'),
    path('unblock/<int:customer_id>/',views.unblock_customer,name='unblock_customer'),
    #coupon
    path('coupon/',views.coupon,name = 'coupon'),
    path('addcoupon/',views.addcoupon,name='addcoupon'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('coupon/<int:coupon_id>/edit/', views.editcoupon, name='edit_coupon'), 
    path('coupon/<int:id>/update_coupon/', views.update_coupon, name='update_coupon'),
    path('coupon/<int:coupon_id>/delete/', views.delete_coupon, name='delete_coupon'),
    #contact
    path('adminside_message/',views.adminside_message,name='adminside_message'),
    path('reply/',views.reply,name='reply'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)