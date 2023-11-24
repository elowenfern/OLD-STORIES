from django.shortcuts import render
from django.views.decorators.cache import cache_control,never_cache
from django.contrib import messages , auth
from django.shortcuts import redirect,render
from django.contrib.auth import authenticate,  login as auth_login , logout
from django.shortcuts import render, redirect
from .models import *
from django.db.models import Sum 
import smtplib
import re
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import reverse
import secrets
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
import json
from django.db.models import F
import uuid
import string,random
from django.shortcuts import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.template.loader import render_to_string
import io
from django.core.mail import EmailMessage
from xhtml2pdf import pisa
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import A4
import matplotlib.pyplot as plt
import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO
from django.http import FileResponse
from datetime import datetime
from django.http import HttpResponse
from reportlab.lib.styles import getSampleStyleSheet
from .models import Order  # Replace 'yourapp' with the actual name of your Django app
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.units import inch
from email.mime.text import MIMEText
from decimal import Decimal, ROUND_HALF_UP

# Create your views here.
def wallet(request):
    user = request.user
    customer=CustomUser.objects.get(email=user)
    wallet_transactions = Wallet.objects.filter(user=user).order_by('-created_at')
    context = {
        'wallet_transactions': wallet_transactions,
        'customer':customer,
    }
    return render(request, 'wallet.html', context)
# user-side search 
@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def search(request):
    # Get the 'q' parameter from the GET request
    query = request.GET.get('q', '')
    products = Product.objects.all()
    if query:
        products = Product.objects.filter(
            models.Q(product_name__icontains=query) |
            models.Q(category__category_name__icontains=query)  
        )
    else:
        products=Product.objects.all() 
    search_results = Product.objects.filter(product_name__icontains=query)
    context = {
        'products': products,
        'search_results':  search_results,
    }
    return render(request, 'search.html',context)
def search_suggestions(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(product_name__icontains=query)[:5]  # Limiting to 5 suggestions
        suggestions = [product.product_name for product in products]
        return JsonResponse(suggestions, safe=False)
    return JsonResponse([], safe=False)
def invoice(request, id):
    # 1. Fetch the order and items
    user = request.user
    orders = Order.objects.filter(id=id)
    order_items = OrderItem.objects.filter(order=id)
    
    for order in orders:
        address = order.address
        for item in order_items:
            # 2. Render the order and items to an HTML template
            rendered = render_to_string('invoice.html', {'order': order, 'item': item ,'address': address,})

            # 3. Convert the rendered HTML to PDF
            output = io.BytesIO()
            pdf = pisa.CreatePDF(rendered, output)
            pdf_data = output.getvalue()

            # 4. Send the PDF as an email attachment
            msg = MIMEMultipart()
            msg['From'] = 'oldstories076@gmail.com'
            msg['To'] = order.user.email
            msg['Subject'] = 'Invoice from Old stories'

            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(pdf_data)
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', 'attachment; filename=invoice.pdf')
            msg.attach(attachment)

            try:
                smtp_server = 'smtp.gmail.com'
                smtp_port = 587
                smtp_username = 'oldstories076@gmail.com'
                smtp_password = 'vafkburwcxgnoyix'

                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(msg['From'], msg['To'], msg.as_string())
                server.quit()
                messages.success(request, 'Invoice sent successfully!')
            except Exception as e:
                return HttpResponse(f'Email sending failed: {str(e)}')
    return redirect('order_details', id=id)
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def index(request):
   
    section = Section.objects.filter(name='Top Deal Of The Day').first()
    if section:
        product = Product.objects.filter(section=section)
    else:
        product = Product.objects.none()
    context = {
        'product': product,
        'section': section,
    }
    return render(request, 'index.html', context)
def shop(request):
    product=Product.objects.filter(deleted=False,category__active=True)
    variations=Variation.objects.filter(deleted=False)
    unique_colors = Variation.objects.values('color').annotate(count=Count('color')).order_by('color')

    selected_color = request.GET.get('color')
    selected_price = request.GET.get('price')
    selected_category = request.GET.get('category')
    if selected_color:
        variations = variations.filter(color=selected_color)
    if selected_category:
       product = product.filter(category__category_name=selected_category)
    
        # Define price ranges based on selected_price
    price_ranges = {
        
        "price1": (0, 500),
        "price2": (500, 1000),
        "price3": (1000, 5000),
        "price4": (5000, 10000),
        "price5": (10000, 25000),
        "price6": (25000, 50000),
        "price7": (50000, 1000000)  
        }
    if selected_price in price_ranges:
            price_range = price_ranges[selected_price]
            # Filter for products with prices within the selected price range
            variations = variations.filter(price__range=price_range)
     # Now, after all filtering, add discounted_price and offer_price attributes
    variations = variations.order_by('price')
    context={
        'product':product,
        'variations':variations,
        'unique_colors':unique_colors,
        'categories':Category.objects.filter(active=True),
        'selected_price': selected_price,
    }
    return render(request, 'shop.html',context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache    
def pdt_detials(request,id):
    product = get_object_or_404(Product, id=id)
    variation =Variation.objects.filter(product=product)
    for variationn in variation:
        discounted_price = None
        offer_price = None
    if product.category.category_offer:
    # Calculate the discount amount as a percentage of the original price
        discount_amount = (variationn.price * product.category.category_offer) / 100
        # Subtract the discount amount from the original price to get the discounted price
        discounted_price = variationn.price - discount_amount
        variationn.discounted_price = discounted_price
        offer_price = None
    if product.product_offer:
        offer_price = variationn.price - (variationn.price * product.product_offer / 100)
        variationn.offer_price = offer_price

    context = {
        'product': product,
        'variation':variation,
        'discounted_price': discounted_price,
    }
    return render(request, 'product_detials.html', context)


def display_variations(request,variation_id=None):
    if request.method == 'GET':
        selected_product_id = request.GET.get('selected_product_id')
        selected_color = request.GET.get('selected_color')
        if variation_id:
            selected_variation = get_object_or_404(Variation, id=variation_id)
            selected_product_id = selected_variation.product.id  # Use the product associated with the selected variation
            selected_image = Variation_img.objects.filter(variation=selected_variation)
            variations = Variation.objects.filter(product=selected_variation.product)  # Filter variations by the product associated with the selected variation
        if selected_product_id:
            product = get_object_or_404(Product, id=selected_product_id)
            variations = Variation.objects.filter(product=product)
            print(selected_product_id)
            print(variations)
            if selected_color:
                selected_variation = get_object_or_404(Variation, id=selected_color)
                selected_image     = Variation_img.objects.filter(variation_id = selected_color)
                selected_product_id=selected_product_id
        else:
            selected_variation = None
            variations = Variation.objects.all()
        for variation in variations:
            discounted_price = None
            offer_price = None
        
        if selected_variation:
                product = selected_variation.product
                if product.category.category_offer:
                # Calculate the discount amount as a percentage of the original price
                    discount_amount = (variation.price * product.category.category_offer) / 100
                    # Subtract the discount amount from the original price to get the discounted price
                    discounted_price = variation.price - discount_amount
                if product.product_offer:
                    offer_price = variation.price - (variation.price * product.product_offer / 100)
                    # variation.offer_price = offer_price
                final_price = min(discounted_price, offer_price) if discounted_price is not None and offer_price is not None else discounted_price or offer_price
            
                variation.discounted_price = discounted_price
                variation.offer_price = offer_price
                variation.final_price = final_price  # Add a field to store the final discounted/offer price
                variation.save()
        
        context = {
            'selected_variation': selected_variation,
            'variations': variations,
            'selected_images' : selected_image
        }
       
        return render(request, 'display_variation.html', context)
    else:
        return redirect('product_detail')
def color(request):
    selected_product_id = request.GET.get('selected_product_id', None)
    if request.method == 'POST':
        selected_product_id = request.POST.get('selected_product_id')
        selected_color_id = request.POST.get('selected_color')
        if selected_product_id and selected_color_id:
            variation = Variation.objects.filter(product_id=selected_product_id, id=selected_color_id).first()
            if variation:
                # Construct the URL with parameters
                url = reverse('display_variation') + f'?selected_product_id={selected_product_id}&selected_color={selected_color_id}'
                return HttpResponseRedirect(url)
    # Handle any other scenarios or errors here
    # You may want to display a message to the user or return to the product page
    return HttpResponseRedirect(reverse('pdt_detials', args=[selected_product_id]))
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def about(request):
    product=Product.objects.filter(deleted=False,category__active=True)
    context={
        'product':product,
    }
    return render(request,'about.html',context)
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def collection(request):
    categories = Category.objects.all()
    category_product_mapping = {}
    for category in categories:
        products = Product.objects.filter(category=category)
        category_product_mapping[category]=products
        context = {
        'category_product_mapping': category_product_mapping,
    }
    return render(request,'collection.html',context)
@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart_items = Cart.objects.filter(user=user).order_by('id')
        subtotal =Decimal('0.00') 
        total_dict = {}
        quantity_added = request.GET.get('quantity', 0)
        for cart_item in cart_items:
            if cart_item.quantity > cart_item.variation.stock:
                messages.warning(request, f"{cart_item.variation.product.product_name} is out of stock.")
                cart_item.quantity = cart_item.variation.stock
                cart_item.save()
            elif cart_item.variation.product.category.category_offer:
                item_price = (cart_item.variation.price - (cart_item.variation.price * Decimal(cart_item.variation.product.category.category_offer / Decimal(100)))) * cart_item.quantity
                total_dict[cart_item.id] = item_price
                subtotal += item_price
            elif cart_item.variation.product.product_offer:
                item_price = (cart_item.variation.price - (cart_item.variation.price * Decimal(cart_item.variation.product.product_offer / Decimal(100)))) * cart_item.quantity
                total_dict[cart_item.id] = item_price
                subtotal += item_price
            else:
                item_price = cart_item.variation.price * cart_item.quantity
                total_dict[cart_item.id] = item_price
                subtotal += item_price
        shipping_cost = Decimal('1500.00')
        total = subtotal + shipping_cost
        subtotal = subtotal.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        total = total.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        cart_items_combined = [(cart_item, Variation_img.objects.filter(variation=cart_item.variation).first()) for cart_item in cart_items]
        context = {
            'cart_items_combined': cart_items_combined,
            'subtotal': subtotal,
            'total': total, 
            'quantity_added': quantity_added,
            'cart_empty': not cart_items_combined 
        }
    else:
        return redirect('loginpage')
    return render(request, 'cart.html', context)
@login_required
@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_to_cart(request, id):
    try:
        variation = Variation.objects.get(id=id)
    except Variation.DoesNotExist:
        return redirect('product_not_found')
    quantity = request.POST.get('quantity', 1)
    try:
        wishlist_item = Wishlist.objects.get(user=request.user, variation_id=id)
    except Wishlist.DoesNotExist:
        print(f'Wishlist item not found for user {request.user} and variation ID {id}')
    # You can redirect or handle this case appropriately
    else:
        wishlist_item.delete()
    if not quantity:
        quantity = 1
    else:
        cart_item, created = Cart.objects.get_or_create(user=request.user, variation=variation)
        if created:
            cart_item.quantity = int(quantity)
        else:
            cart_item.quantity += int(quantity)
        cart_item.save()
        return redirect('cart')
    
    request.session['cart_pending_variation_id'] = id
    request.session['cart_pending_quantity'] = request.POST.get('quantity', 1)
    return redirect('loginpage')
def update_cart(request, variationId):
    cart_item = None
   
    cart_item = get_object_or_404(Cart, variation_id=variationId, user=request.user)
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity'))
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({'message': 'Invalid quantity.'}, status=400)

    if quantity < 1:
        return JsonResponse({'message': 'Quantity must be at least 1.'}, status=400)
    
    cart_item.quantity = quantity
    cart_item.save()

    return JsonResponse({'message': 'Cart item updated',}, status=200)



@login_required
def order_placed(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    subtotal=0
    for cart_item in cart_items:
        if cart_item.variation.product.category.category_offer:
            item_price = (cart_item.variation.price - (cart_item.variation.price*cart_item.variation.product.category.category_offer/100)) * cart_item.quantity
            subtotal += item_price
        elif cart_item.variation.product.product_offer:
            itemprice =  (cart_item.variation.price - (cart_item.variation.price * cart_item.variation.product.product_offer/100)) * cart_item.quantity
            subtotal=subtotal+itemprice
        else:
            itemprice=(cart_item.variation.price)*(cart_item.quantity)
            subtotal=subtotal+itemprice
    shipping_cost = 1500 
   
    discount = request.session.get('discount', 0)
    total = max(subtotal - discount, 0) + shipping_cost if subtotal else 0
    print(total)
    print("...............................")
    if request.method == 'POST':
        payment       =    request.POST.get('payment')
        address_id    =    request.POST.get('addressId')
        shipping_address_id   =    request.POST.get('shippingId')
    if not address_id and not shipping_address_id:
        messages.info(request, 'Input Address or Shipping method!')
        return redirect('check_out')

    address = None
    shipping = None
   
    
    if address_id or shipping_address_id:
        if address_id:
            try:
                address = Address.objects.get(id=address_id)
                print("Address selected")
            except Address.DoesNotExist:
                messages.error(request, 'Invalid Address!')
                return redirect('check_out')
        if shipping_address_id:
            try:
                shipping = Shipping.objects.get(id=shipping_address_id)
                print("Shipping selected")
            except Shipping.DoesNotExist:
                messages.error(request, 'Invalid Shipping Address!')
                return redirect('check_out')
    else:
        messages.error(request, 'Input Address or Shipping Address!')
        return redirect('check_out')
        
    
    order = Order.objects.create(
        user          =     user,
        address       =     address,
        shipping      =     shipping,
        amount        =     total,
        payment_type  =     payment,
    )

    for cart_item in cart_items:
        variation = cart_item.variation
        variation.stock -= cart_item.quantity
        variation.save()

        variation_img = Variation_img.objects.filter(variation=variation).first()

        order_item = OrderItem.objects.create(
            order         =     order,
            variation      =     cart_item.variation,
            quantity      =     cart_item.quantity,
            image         =     variation_img.image if variation_img else None,
        )
    cart_items.delete()
    return redirect('success')  
@never_cache
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def remove_from_cart(request,id):
    try:
        cart_item = Cart.objects.get(id=id, user=request.user)
        cart_item.delete()
    except Cart.DoesNotExist:
        pass
    
    return redirect('cart')

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def check_out(request):
    request.session['discount'] = 0
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    current_date = timezone.now()
    coupons = Coupon.objects.filter(deleted=False, expiry_date__gte=current_date)
    subtotal =Decimal('0.00') 
    sales_data = []
    for cart_item in cart_items:
        if cart_item.variation.product.category.category_offer:
            item_price = (cart_item.variation.price - (cart_item.variation.price * Decimal(cart_item.variation.product.category.category_offer / Decimal(100)))) * cart_item.quantity
            subtotal += item_price
        elif cart_item.variation.product.product_offer:
            item_price = (cart_item.variation.price - (cart_item.variation.price * Decimal(cart_item.variation.product.product_offer / Decimal(100)))) * cart_item.quantity
            subtotal=subtotal+itemprice
        else:
            itemprice = (cart_item.variation.price) * (cart_item.quantity)
            subtotal = subtotal + itemprice
        sales_data.append({
            'variation': cart_item.variation,
            'quantity_sold': cart_item.quantity,
        })
    shipping_cost = Decimal('1500.00')
    coupon_discount = request.session.get('discount', 0)
    subtotal = subtotal.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
    
    # Calculate the total by subtracting the coupon discount from the subtotal and adding the shipping cost
    total = max(subtotal - coupon_discount, 0) + shipping_cost if subtotal else 0
    for sale_info in sales_data:
        Sales.objects.create(variation=sale_info['variation'], quantity_sold=sale_info['quantity_sold'])
    address = Address.objects.filter(user=user,is_deleted=False)
    shipping =Shipping.objects.filter(user=user,is_deleted=False)
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
        'address': address,
        'shipping':shipping,
        'coupons':coupons
    }
    return render(request, 'checkout.html', context)
#payment
def proceed_to_pay(request):
    cart = Cart.objects.filter(user=request.user)
    total = 0
    shipping = Decimal(1500)
    subtotal =Decimal('0.00') 
    for cart_item in cart:
        if cart_item.variation.product.category.category_offer:
            item_price = (cart_item.variation.price - (cart_item.variation.price * Decimal(cart_item.variation.product.category.category_offer / Decimal(100)))) * cart_item.quantity
            subtotal += item_price
        elif cart_item.variation.product.product_offer:
            item_price = (cart_item.variation.price - (cart_item.variation.price * Decimal(cart_item.variation.product.product_offer / Decimal(100)))) * cart_item.quantity
            subtotal=subtotal+itemprice
        else:
            itemprice=(cart_item.variation.price)*(cart_item.quantity)
            subtotal=subtotal+itemprice
    
    discount = request.session.get('discount', 0)
    # Subtract the coupon discount from the subtotal
    subtotal_after_discount = max(subtotal - discount, 0)
    total=subtotal_after_discount+shipping 
    
    return JsonResponse({
        'total' : total

    })

def razorpay(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    subtotal =Decimal('0.00') 
    for cart_item in cart_items:
        if cart_item.variation.product.category.category_offer:
            item_price = (cart_item.variation.price - (cart_item.variation.price * Decimal(cart_item.variation.product.category.category_offer / Decimal(100)))) * cart_item.quantity
            subtotal += item_price
        elif cart_item.variation.product.product_offer:
            item_price = (cart_item.variation.price - (cart_item.variation.price * Decimal(cart_item.variation.product.product_offer / Decimal(100)))) * cart_item.quantity
            subtotal=subtotal+itemprice  
        else:
            itemprice=(cart_item.variation.price)*(cart_item.quantity)
            subtotal=subtotal+itemprice
    shipping_cost = Decimal(1500) 
    discount = request.session.get('discount', 0)
    # Subtract the coupon discount from the subtotal
    subtotal_after_discount = max(subtotal - discount, 0)
    total=subtotal_after_discount+shipping_cost
    payment  =  'razorpay'
    user     = request.user
    cart_items = Cart.objects.filter(user=user)
     # Retrieve JSON data
    address = Address.objects.filter(user=user)
    if address.exists():
        address = address.first() 
    order = Order.objects.create(
        user          =     user,
        address      =     address,
        amount        =     total,
        payment_type  =     payment,
        )
    for cart_item in cart_items:
        variation = cart_item.variation
        variation.stock -= cart_item.quantity
        variation.save()
        variation_img = Variation_img.objects.filter(variation=variation).first()
        order_item = OrderItem.objects.create(
            order         =     order,
            variation       =     cart_item.variation,
            quantity      =     cart_item.quantity,
            image         =     variation_img.image 
        )          
    cart_items.delete()
    return redirect('success')  
def restock_products(order):
    order_items = OrderItem.objects.filter(order=order)
    for order_item in order_items:
        variation = order_item.variation
        variation.stock += order_item.quantity
        variation.save()
# admin side order
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache     
def order(request):
    if 'admin' in request.session:
        orders = Order.objects.all().order_by('-id')
        paginator = Paginator(orders, per_page=10) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'orders': page_obj,
        }
        
        return render(request, 'order.html', context)
    else:
        return redirect('admin')
def update_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        status = request.POST.get('status')
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return redirect('order') 
        restock_products(order)
        order.status = status
        order.save()   
        messages.success(request, 'Order status updated successfully.')
        return redirect('order') 
    return redirect('admin')
# end admin order
def success(request):
    orders = Order.objects.latest('id')
    context = {
        'orders'  : orders,
    }
    return render(request,'success.html',context)
def changepassword(request):
    if request.method == 'POST':
        old_password = request.POST.get('old')
        new_password = request.POST.get('new_password1')
        confirm_password = request.POST.get('new_password2')
        customer = CustomUser.objects.get(username=request.user.username)
        if customer.check_password(old_password):
            if new_password == confirm_password:
                customer.set_password(new_password)
                customer.save()
                # messages.success(request, 'Password changed successfully.')
                return redirect('index')
            else:
                messages.error(request, 'New password and confirm password do not match.')
                return redirect ('profile')
        else:
            messages.error(request, 'Old password is incorrect.')
            return redirect('profile')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def signup(request):
    if 'email'in request.session:
        return redirect('index') 
    elif request.method=='POST':
        name=request.POST['name']
        email=request.POST['email']
        phone_number=request.POST['phone_no']
        password=request.POST['password']
        confirmpassword=request.POST['confirmpassword']
        user=authenticate(email=email,password=password)
        if not (name and email and password and phone_number and confirmpassword):
            messages.info(request,"PLease Fill Required field")
            return redirect('signup')       
        elif password != confirmpassword:
            messages.info(request,"Password Mismatch")
            return redirect('signup')        
        else:
            if not validate_email(email):
                messages.error(request, 'Please enter a valid email address.')
                return redirect('signup')            
            if CustomUser.objects.filter(email = email).exists():
                messages.info(request,"Email Already Taken")
                return redirect('signup')
            if not re.match(r'^[789]\d{9}$', phone_number):
                messages.error(request, 'Please enter a valid 10-digit phone number starting with 7,8 or 9.')
                return redirect('signup')
            elif CustomUser.objects.filter(phone_number = phone_number).exists():
                messages.info(request,"phone number already taken")
                return redirect('signup')
            else:
                my_user=CustomUser.objects.create_user(username=name,email=email,password=password,phone_number=phone_number)
                my_user.save()    
        message = generate_otp()
        sender_email = "oldstories076@gmail.com"
        receiver_mail = email
        password_email = "vafkburwcxgnoyix"
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, password_email)
                server.sendmail(sender_email, receiver_mail, message)
        except smtplib.SMTPAuthenticationError:
            messages.error(request, 'Failed to send OTP email. Please check your email configuration.')
            return redirect('signup')
        # user = CustomUser.objects.create_user(name=name, password=password, email=email,phone_number=phone_number)
        # user.save()

        request.session['email'] =  email
        request.session['otp']   =  message
        messages.success(request,'OTP is sent to your email')
        return redirect('verify_signup')
    
    return render(request,'signup.html')
def validate_email(email):
    return '@' in email and '.' in email
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def verify_signup(request):
    context = {
        'messages': messages.get_messages(request)
    }
    if request.method == "POST":
        user      = CustomUser.objects.get(email=request.session['email'])
        x         =  request.session.get('otp')
        OTP       =  request.POST['otp']     
        if OTP == x:
            user.is_verified = True
            user.save()
            del request.session['email'] 
            del request.session['otp']        
            auth.login(request,user)
            messages.success(request, "Signup successful!")
            return redirect('loginpage')
        else:
            user.delete()
            messages.info(request,"invalid otp")
            del request.session['email']
            return redirect('signup')
        
    return render(request,'verifysignup.html',context)

def generate_otp(length = 6):
    return ''.join(secrets.choice("0123456789") for i in range(length))
@never_cache
def loginpage(request):
    if 'email' in request.session:
        return redirect('index')
    else: 
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request, email=email, password=password)     
            if user is not None and user.is_verified:
                auth_login(request, user)
                request.session['email'] = email
                variation_id = request.session.get('cart_pending_product_id')
                quantity = request.session.get('cart_pending_quantity')
                if variation_id and quantity:
                    try:
                        variation = Variation.objects.get(id=variation_id)
                    except Variation.DoesNotExist:
                        pass
                    else:
                        cart_item, created = Cart.objects.get_or_create(user=request.user, variation=variation)

                        if not created:
                            cart_item.quantity += int(quantity)
                        else:
                            cart_item.quantity = int(quantity)
                        cart_item.save()
                return redirect('index')  
            else:
                error_message = 'Invalid email or password.'
                return render(request, 'login.html', {'error_message': error_message})
        else:
            return render(request, 'login.html')
def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            customer = CustomUser.objects.get(email=email)
           
            if customer.email == email:
            
                message = generate_otp()
                sender_email = "oldstories076@gmail.com"
                receiver_mail = email
                password = "vafkburwcxgnoyix"

                try:
                    with smtplib.SMTP("smtp.gmail.com", 587) as server:
                        server.starttls()
                        server.login(sender_email, password)
                        server.sendmail(sender_email, receiver_mail, message)

                except smtplib.SMTPAuthenticationError:
                    messages.error(request, 'Failed to send OTP email. Please check your email configuration.')
                    return redirect('signup')
                
                request.session['email'] =  email
                request.session['otp']   =  message
                messages.success (request, 'OTP is sent to your email')
                return redirect('reset_password')   
            
        except CustomUser.DoesNotExist:
            messages.info(request,"Email is not valid")
            return redirect('loginpage')
    else:
        return redirect('loginpage')


def reset_password(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        stored_otp = request.session.get('otp')
        if entered_otp == stored_otp:
            if new_password == confirm_password:
                email = request.session.get('email')
                try:
                    customer = CustomUser.objects.get(email=email)
                    customer.set_password(new_password)
                    customer.save()
                    del request.session['email'] 
                    del request.session['otp']
                    messages.success(request, 'Password reset successful. Please login with your new password.')
                    return redirect('loginpage')
                except CustomUser.DoesNotExist:
                    messages.error(request, 'Failed to reset password. Please try again later.')
                    return redirect('loginpage')
            else:
                messages.error(request, 'New password and confirm password do not match.')
                return redirect('reset_password')
        else:
            messages.error(request, 'Invalid OTP. Please enter the correct OTP.')
            return redirect('reset_password')
    else:
        return render(request, 'passwordreset.html')
    
@login_required
@user_passes_test(lambda u: not u.is_staff, login_url='loginpage') 
def profile(request):
    user=request.user
    context={
        'user':user,
    }
    return render(request,'profile.html',context)
def update_profile(request):
    if request.method=='POST':
        user=request.user
    # retrive  data  from form
        new_name=request.POST['name']
        new_mail=request.POST['email']
        new_phone_number=request.POST['phone_number']
        if not is_valid_email(new_mail):
            messages.error(request, 'Please enter a valid email address.')
            return redirect('profile')
        # Validate phone number
        if not re.match(r'^[789]\d{9}$', new_phone_number):
            messages.error(request, 'Please enter a valid 10-digit phone number starting with 7,8 or 9.')
            return redirect('profile')

    # update the users info
        user.username=new_name
        user.email=new_mail
        user.phone_number=new_phone_number
        user.save()
        messages.success(request,'Profile updated successfully!!!')
        return redirect('profile')
    return render(request,'profile.html')
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email)
def address(request):
    # Assuming you have a foreign key from Address to the User model
    user = request.user
    addresses = Address.objects.filter(user=user,is_deleted=False)
    context={
        'addresses':addresses,
    }
    return render(request,'address.html',context)

def add_address(request):
    if request.method == 'POST':
        # Retrieve data from the POST request
        full_name = request.POST['full_name']
        house_no = request.POST['house_no']
        post_code = request.POST['post_code']
        state = request.POST['state']
        street = request.POST['street']
        phone_no = request.POST['phone_no']
        city = request.POST['city']
        if not full_name or not house_no or not post_code or not state or not street or not phone_no or not city:
                messages.error(request, 'Please fill in all required fields.')     
        elif post_code and not re.match(r'^\d{6}$', post_code):
                messages.error(request, 'Please enter a valid 6-digit post code.')
        elif not re.match(r'^[789]\d{9}$', phone_no):
                messages.error(request, 'Please enter a valid 10-digit phone number starting with 7,8 or 9.')
        else:
            user=request.user
            address = Address(
                    user=user,
                    full_name=full_name,
                    house_no=house_no,
                    post_code=post_code,
                    state=state,
                    street=street,
                    phone_no=phone_no,
                    city=city,
                )
            address.save()
            return redirect('address')
        request.session['user_input'] = {
            'full_name': full_name,
            'house_no': house_no,
            'post_code': post_code,
            'state': state,
            'street': street,
            'phone_no': phone_no,
            'city': city,
        } 
    user_input = request.session.get('user_input', {})
       
    return render(request,'add_address.html', {'user_input': user_input}) 
    
def edit_address(request,id):
    address= Address.objects.get(id=id)
    if request.method == 'POST':
        # Retrieve data from the POST request
        full_name = request.POST['full_name']
        house_no = request.POST['house_no']
        post_code = request.POST['post_code']
        state = request.POST['state']
        street = request.POST['street']
        phone_no = request.POST['phone_no']
        city = request.POST['city']

        # Update the Address object with the edited data
        address.full_name = full_name
        address.house_no = house_no
        address.post_code = post_code
        address.state = state
        address.street = street
        address.phone_no = phone_no
        address.city = city

        # Save the updated address to the database
        address.save()

        return redirect('address')
    else:
        context = {
            'address': address
        }
    return render(request,'editaddress.html',context)


def delete_address(request,id):
    try:
        address = Address.objects.get(id=id)
        address.soft_delete()
    except Address.DoesNotExist:
        return render(request, 'Address_not_found.html')
    return redirect('address')
def shipping_address(request):
    # Assuming you have a foreign key from Address to the User model
    user = request.user
    shipping = Shipping.objects.filter(user=user,is_deleted=False)
    context={
        'shipping':shipping,
    }
    return render(request,'shipping.html',context)

def shipping_add_address(request):
    if request.method == 'POST':
        # Retrieve data from the POST request
        full_name = request.POST['full_name']
        house_no = request.POST['house_no']
        post_code = request.POST['post_code']
        state = request.POST['state']
        street = request.POST['street']
        phone_no = request.POST['phone_no']
        city = request.POST['city']
        if not full_name or not house_no or not post_code or not state or not street or not phone_no or not city:
                messages.error(request, 'Please fill in all required fields.')
                return redirect('check_out')
        if post_code and not re.match(r'^\d{6}$', post_code):
                messages.error(request, 'Please enter a valid 6-digit post code.')
                return redirect('check_out')
        if not re.match(r'^[89]\d{9}$', phone_no):
                messages.error(request, 'Please enter a valid 10-digit phone number starting with 9 or 8.')
                return redirect('check_out')

        # Create a new Address object and save it to the database
        user=request.user
        shipping = Shipping(
            user=user,
            full_name=full_name,
            house_no=house_no,
            post_code=post_code,
            state=state,
            street=street,
            phone_no=phone_no,
            city=city,
        )
        shipping.save()
        return redirect('check_out') # Redirect to the address list page or any other page
    return render(request,'checkout.html') 
    
def shipping_edit_address(request,id):
    shipping= Shipping.objects.get(id=id)
    if request.method == 'POST':
        # Retrieve data from the POST request
        full_name = request.POST['full_name']
        house_no = request.POST['house_no']
        post_code = request.POST['post_code']
        state = request.POST['state']
        street = request.POST['street']
        phone_no = request.POST['phone_no']
        city = request.POST['city']

        # Update the Address object with the edited data
        shipping.full_name = full_name
        shipping.house_no = house_no
        shipping.post_code = post_code
        shipping.state = state
        shipping.street = street
        shipping.phone_no = phone_no
        shipping.city = city

        # Save the updated address to the database
        shipping.save()
        return redirect('shipping_address')
    else:
        context = {
            'shipping': shipping
        }
    return render(request,'editaddress.html',context)
def shipping_delete_address(request,id):
    try:
        shipping = Shipping.objects.get(id=id)
        shipping.soft_delete()
    except Shipping.DoesNotExist:
        return render(request, 'Address_not_found.html')
    return redirect('shipping_address')
def restock_products(order):
    order_items = OrderItem.objects.filter(order=order)
    for order_item in order_items:
        variation = order_item.variation
        variation.stock += order_item.quantity
        variation.save()
# costumer side
def customer_order(request):
    user = request.user 
    orders = Order.objects.filter(user = user).order_by('-id')
    print(orders)
    context ={
         'orders':orders,
        }
    return render(request,'customer_order.html',context)
def order_details(request,id):
    orders = Order.objects.filter(id=id)
    print(orders)
    context ={
         'orders':orders,
        }
    return render(request,'order_details.html',context)
def cancel_order(request, id):
    user=request.user
    usercustm=CustomUser.objects.get(email=user)
    order = Order.objects.get(id=id)
    order.status = 'cancelled'
    order.save()
    if  order.status == 'cancelled' and  order.payment_type=='cod':
        wallet= Wallet.objects.create(
        user=user,
        order= order,
        amount= order.amount,
        status='Credited',
        )
        wallet.save()
        order.status='cancelled'
        order.save()
        Order_item_amount = Decimal(order.amount)
        usercustm.wallet_bal+=Order_item_amount
        usercustm.save()
    elif  order.payment_type=='razorpay':
        wallet= Wallet.objects.create(
        user=user,
        order= order,
        amount= order.amount,
        status='Credited',
        )
        wallet.save()
        order.status='cancelled'
        order.save()
        Order_item_amount = Decimal(order.amount)
        usercustm.wallet_bal+=Order_item_amount
        print('wallte:',usercustm.wallet_bal)
        usercustm.save()
    restock_products(order)
    order.status = 'cancelled'
    order.save()
    return redirect('order_details',id)
def return_order(request,id):
    user=request.user
    usercustm=CustomUser.objects.get(email=user)
    order = Order.objects.get(id=id)
    order.status='return'
    order.save()
    restock_products(order) 
    if order.status == 'return' and order.payment_type == 'cod':
        print("..................................")
        wallet=Wallet.objects.create(
            user=user,
            order=order,
            amount=order.amount,
            status='Credited',
        )
        wallet.save()
        Order_item_amount=Decimal(order.amount)
        usercustm.wallet_bal+=Order_item_amount
        usercustm.save()
    elif order.status=='return' and order.payment_type=='razorpay':
        wallet=Wallet.objects.create(
        user=user,
        order= order,
        amount= order.amount,
        status='Credited',
        )
        wallet.save()
        order.status='return'
        order.save()
        Order_item_amount=Decimal(order.amount)
        usercustm.wallet_bal+=Order_item_amount
        usercustm.save()
        return redirect('order_details',id)
    else:
        return HttpResponse("Cannot return the order.")


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache    
def logoutpage(request):
    if 'email' in request.session:
        request.session.flush()
    logout(request)
    return redirect('index')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def admin(request):
    if 'admin' in request.session:
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(request, username = email, password=password)
            if user is not None and user.is_superuser:
                auth_login(request, user)  
                request.session['admin'] = email
                return redirect('dashboard')  
            else:
                messages.error(request, 'Email or password is invalid')
                return render(request, 'admin.html')
    return render(request, 'admin.html')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def dashboard(request):
    if 'admin' in request.session:
        # Fetch top 5 products
        products = Product.objects.order_by('-id')[:5]
        # Fetch sales data for each product variation
        sales_data = []
        order_labels = []
        order_amounts = []
        stock_labels = []
        stock_amounts = []
        for product in products:
            variations = Variation.objects.filter(product=product)
            for variation in variations:
                total_sales = Sales.objects.filter(variation=variation).aggregate(Sum('quantity_sold'))['quantity_sold__sum'] or 0
                sales_data.append({
                    'product_name': product.product_name,
                    'variation_id': variation.id,
                    'color': variation.color,
                    'size': variation.size,
                    'total_sales': total_sales,
                })
        
         # Process data for bar chart (order distribution)
                order_labels.append(f'Order {variation.id}')
                order_amounts.append(variation.price)  # Use any field you want for the order amount

                # Process data for pie chart (stock distribution)
                stock_labels.append(f'{product.product_name} - {variation.color} - {variation.size}')
                stock_amounts.append(variation.stock)

        # Convert data to JSON format for JavaScript
        sales_data_json = json.dumps(sales_data)
        order_data = json.dumps(order_amounts)
        stock_data = json.dumps(stock_amounts)
        context = {
            'sales_data': sales_data_json,
            'order_labels': order_labels,
            'order_data': order_data,
            'stock_labels': stock_labels,
            'stock_data': stock_data,
        }
        return render(request, 'dashboard.html', context)
    else:
        return redirect('admin')
# Create bar chart function
def create_bar_chart(labels, data, title):
    plt.figure(figsize=(8, 6))
    plt.bar(labels, data, color='skyblue')
    plt.xlabel('Variations')
    plt.ylabel('Total Sales')
    plt.title(title)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    chart_image = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    return f'data:image/png;base64,{chart_image}'

# pie chart function
def create_pie_chart(labels, data, title):
    plt.figure(figsize=(8, 8))
    plt.pie(data, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title(title)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    chart_image = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    return f'data:image/png;base64,{chart_image}'

styles = getSampleStyleSheet()
style = styles["Normal"]
def report_generator(request, orders):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    story = []

    data = [["ID", "Date", "Total Quantity", "Product IDs", "Product Names", "Amount"]]

    for order in orders:
        # Retrieve order items associated with the current order
        order_items = OrderItem.objects.filter(order=order)
        total_quantity = sum(item.quantity for item in order_items)

        if order_items.exists():
            product_ids = ", ".join([str(item.variation.product.id) for item in order_items])
            product_names = ", ".join([f"{item.variation.product.product_name} - {item.variation.color}" for item in order_items])

        else:
            product_ids = "N/A"
            product_names = "N/A"

        data.append([order.id, order.date.strftime('%Y-%m-%d'), total_quantity, product_ids, Paragraph(product_names, style), order.amount])
    # Create a table with the data
    table = Table(data, colWidths=[0.7 * inch, 1.3 * inch, 1.5 * inch, 1.5 * inch, 2.5 * inch, 1 * inch])
    # Style the table
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(table_style)

    # Add the table to the story and build the document
    story.append(table)
    doc.build(story)

    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename='orders_report.pdf')

def report_pdf_order(request):
    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        except ValueError:
            return HttpResponse('Invalid date format.')
        orders = Order.objects.filter(date__range=[from_date, to_date]).order_by('-id')
        return report_generator(request, orders)

def chart_demo(request):
    orders = Order.objects.order_by('-id')[:5]
    labels = []
    data = []
    for order in orders:
        labels.append(str(order.id))
        data.append(order.amount)
    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(data),
    }
    return render(request, 'chart_demo.html', context)
def contact(request):
    context = {}  
    if request.method=='POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        if not v_email(email):
            messages.error(request, 'Please enter a valid email address.')
            return redirect('contact')
        # Save the message to the database
        contact = Contact(name=name, email=email, message=request.POST.get('message'))
        contact.save()
        messages.success(request, 'Thank you for contacting us!')
        return redirect('contact') 
    return render(request,'contact.html',context)
def v_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email)
def adminside_message(request):
    customer_messages=Contact.objects.all()
    context={
        'customer_messages':customer_messages
    }
    return render(request,'customer_message.html',context)
def reply(request):
    if request.method == 'POST':
        user_email = request.POST.get('email')
        message_content = request.POST.get('message')
        subject = 'Message from OLDSTORIES'
        from_email = 'oldstories076@gmail.com'
        to_email = user_email.strip()
        try:
            # Check if the email exists in your Contact model
            contact = Contact.objects.filter(email__iexact=to_email).first()
            if contact is not None:
                # Create the MIME message
                msg = MIMEMultipart()
                msg['From'] = from_email
                msg['To'] = to_email
                msg['Subject'] = subject
                msg.attach(MIMEText(message_content, 'plain'))
                # Connect to the server and send the email
                smtp_server = 'smtp.gmail.com'
                smtp_port = 587
                smtp_username = 'oldstories076@gmail.com'
                smtp_password = 'vafkburwcxgnoyix'
                
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
                server.quit()
                messages.success(request, 'Email sent successfully.')
            else:
                messages.error(request, 'Invalid email address. Please check the email.')
        except Exception as e:
            messages.error(request, f'Error sending email: {e}')
    return redirect('adminside_message')
@never_cache
def adminlogout(request):
    if 'admin' in request.session:
        request.session.flush()
    logout(request)
    return redirect('admin')
@never_cache 
@cache_control(no_cache=True,must_revalidate=True,no_store=True)  
def customer(request):
    if 'admin' in request.session:    
        customer_list = CustomUser.objects.filter(is_staff=False).order_by('id')
        paginator = Paginator(customer_list,10)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'page_obj': page_obj,
        }
        return render(request, 'customer.html', context)
    else:
        return redirect('admin')
@never_cache 
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def category(request):
    if 'admin' in request.session:
        categories = Category.objects.all().order_by('id')              
        paginator = Paginator(categories, per_page=10)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)       
        context = {
            'categories': page_obj,
        }
        return render(request, 'category.html', context)
    else:
        return redirect('admin')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def update_category(request, id):
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        return render(request, 'category_not_found.html')
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        if category_name:
            category.category_name           =  category_name
            
            image                                =  request.FILES.get('image')
            category.category_offer_description  =  request.POST.get('offer_details')
            category.category_offer              =  request.POST.get('offer_price')
        if image:
            category.image = image
        category.save()
        return redirect('category')
    context = {'category': category}
    return render(request, 'edit_category.html', context)
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache 
def addcategory(request):
    if 'admin' in request.session:
        if request.method  == 'POST':
            category_name       =   request.POST['category_name'] 
            category_offer_description=request.POST.get('category_offer_description')
            category_offer=request.POST.get('category_offer')
            

            category = Category.objects.create(
                category_name                =  category_name,
                category_offer_description   =  category_offer_description,
                category_offer               =  category_offer
            
            )           
            category.save() 
            return redirect('category')  
        return render(request, 'addcategory.html') 
    else:
        return redirect ('admin')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache 
def editcategory(request,category_id):
    if 'admin' in request.session:
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return render(request, 'category_not_found.html')

        context = {'category': category}
        return render(request, 'editcategory.html', context)
    else:
        return redirect ('admin')
def delete_category(request, category_id):
    try:
         category = Category.objects.get(id=category_id)
         category.active = not category.active
         category.save()
    except Category.DoesNotExist:
         return render(request, 'category_not_found.html')
    category = Category.objects.all()
    context={'category':category}
    
    return redirect('category')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def update_category(request,category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return render(request, 'category_not_found.html')

    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        category_offer_description  =request.POST.get('category_offer_description')
        category_offer  =request.POST.get('category_offer')
        if category_name:
            category.category_name           =  category_name
            category.category_offer_description  = category_offer_description
            category.category_offer              =category_offer
           # Check for None or empty offer_price before assignment
            category.save()
        return redirect('category')
    context = {'category': category}
    return render(request, 'edit_category.html', context)


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def sub_category(request):
    if 'admin' in request.session:
        subcategories = Sub_category.objects.all()
        maincategories = Category.objects.all()
        maincategory_names = {}
        maincategory_ids = {}
        for sub in subcategories:
            maincategory_names[sub.id] = sub.main_category.category_name
            maincategory_ids[sub.id] = sub.main_category.id
                  
        paginator = Paginator(subcategories, per_page=3)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'categories': page_obj,
            'subcategories' : subcategories,
            'maincategories' :maincategories,
            'maincategory_names': maincategory_names,
            'maincategory_ids': maincategory_ids,
        }
        

        return render(request,'subcategory.html',context)
    else:
        return redirect('admin')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def add_sub_category(request):
    main_category=Category.objects.all()
    context={
        'main_category':main_category
    }
       
    if 'admin' in request.session: 
        if request.method  == 'POST':
            cat      = request.POST.get('categories')
            print(cat)
            sub_category_name   =request.POST.get('name')
            main = Category.objects.get(id=cat)

            
            sub = Sub_category.objects.create(main_category=main,sub_category_name=sub_category_name)
            sub.save() 

            return redirect('sub_category')  
        return render(request,'addsubcategory.html',context)
    else:
        return redirect ('admin')
       
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def edit_sub_category(request, sub_category_id):
    cat = Category.objects.all()
    if 'admin' in request.session:
        try:
            sub_category =  Sub_category.objects.get(id=sub_category_id)
        except  Sub_category.DoesNotExist:
            return render(request, 'category_not_found.html')

        context = {'sub_category': sub_category,'cat':cat,
        }
        return render(request, 'edit_subcategory.html', context)
    else:
        return redirect ('admin')
    

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def update_sub_category(request, sub_category_id):
    main_category = Category.objects.all()
    sub_category = Sub_category.objects.get(id=sub_category_id)  # Use get() instead of filter()

    if request.method == 'POST':
        new_name = request.POST.get('sub_category_name')
        new_main_id = request.POST.get('main_category')
        sub_category.sub_category_name = new_name
        # sub_category.main_category_id = new_main_id
        sub_category.save()

        return redirect('sub_category')

    return render(request, 'edit_sub_category.html')
def delete_sub_category(request,sub_id):
    try:
        sub_category = Sub_category.objects.get(id=sub_id)
        sub_category.active = not sub_category.active
        sub_category.save()
    except Sub_category.DoesNotExist:
         return render(request, 'sub_category_not_found.html')
    
   

    sub_category = Sub_category.objects.all()
    context = {'categories': sub_category}
    
    return redirect('sub_category')
         




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def product(request):
    if 'admin' in request.session:
        
        products = Product.objects.all().order_by('id')
               
        paginator = Paginator(products, 5)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
           
        }
        return render(request, 'product.html', context)
    else:
        return redirect('admin')
    




def variations(request, product_id=None):
    products = Product.objects.all()

    if product_id:
        product = get_object_or_404(Product, pk=product_id)
        variations = Variation.objects.filter(product=product)
        variation_images = []  
        for variation in variations:
            # Get the first image associated with the variation, if available.
            first_variation_image = Variation_img.objects.filter(variation=variation).first()
            variation_images.append(first_variation_image)
    else:
        variations = Variation.objects.all()
        variation_images = []

    paginator = Paginator(products, 5)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': products,
        'variations': variations,
        'variation_images': variation_images,
        'page_obj': page_obj,
       
        
    }

    return render(request, 'variation.html', context)


def add_variation(request):
        if 'admin' in request.session:
            
            if request.method == 'POST':
                product_id=request.POST['product_id']
                product = get_object_or_404(Product, id=product_id)

                color = request.POST['color']
                size = request.POST['size']
                stock          =  int(request.POST['stock'])
                price = request.POST['price']
                variation_images = request.FILES.getlist('images')
                image_ids = []
                
                if stock < 0:
                    messages.error(request, "Stock cannot be a negative number.")
                    return redirect('add_variation')
                
                variation = Variation.objects.create(

                    product=product,
                    color=color,
                    size=size,
                    stock=stock,
                    price=price,
                   
                )  
                variation_id = variation.id
                print(variation_id,"....................")

                for img in variation_images:
                    image_obj = Variation_img.objects.create(variation=variation, image=img)
                    image_ids.append(image_obj.id)


                             
                return redirect('product') 
            
            products = Product.objects.all()

            context = {'products':products}
            return render(request,'addvariation.html',context)
        else:
            return redirect('admin')
        
def edit_variation(request,id):
    if 'admin' in request.session:
        try:
            variation = Variation.objects.get(id=id)
            variation_images = Variation_img.objects.filter(variation=variation)
        except Variation.DoesNotExist:
            return HttpResponse('variation_not_found')
       
        
        context = {
            
            'variations': variation,
            'variation_images': variation_images,
            
        }
        return render(request, 'edit_variation.html', context)
    else:
        return redirect('admin')
    
def update_variation(request,id):
    variations = Variation.objects.get(id=id)
    
    if request.method == 'POST':
        color = request.POST['color']
        size = request.POST['size']
        stock =   request.POST['stock']
        price = request.POST['price']
        if int(stock) < 0:
            messages.error(request, "Stock cannot be a negative number.")
            return redirect('edit_variation', id=id)
        
        variations.color = color
        variations.size = size
        variations.stock = stock
        variations.price = price
        variations.price = variations.price
        variations.save()
        if 'multimage' in request.FILES:
           for image_file in request.FILES.getlist('multimage'):
                variation_img = Variation_img()
                variation_img.variation = variations
                variation_img.image = image_file
                variation_img.save()

        return redirect('variations',product_id=variations.product.id)  
def delete_variation(request,id):
    try:
        variation = Variation.objects.get(id=id)
        variation.deleted = True
        variation.save()
    except Variation.DoesNotExist:
         return render(request, 'variation_not_found.html')

    return redirect('variations')
def restore_variation(request, id):
    try:
        variation = Variation.objects.get(id=id)
        variation.deleted = False  
        variation.save()
    except Variation.DoesNotExist:
        pass
    return redirect('variations')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache 
def addproduct(request):
    if 'admin' in request.session:
        categories=Category.objects.filter(active=True)
        sections = Section.objects.all()
        if request.method == 'POST':
            product_name   =  request.POST.get('product_name')
            description    =  request.POST.get('description')
            subcategory_id =request.POST.get('subcategory_id')
            section_name = request.POST.get('section')
            min_price      = request.POST.get('min_price')  
            max_price      = request.POST.get('max_price')
            offer = request.POST.get('offer')
            image          =  request.FILES.get('image') 
            try:
                subcategory_id=Sub_category.objects.get(id=subcategory_id)
                main_category_id=subcategory_id.main_category_id
                section = Section.objects.get(name=section_name)
            except Sub_category.DoesNotExist:
                return HttpResponse("sub category not found")  
            product = Product.objects.create(
                product_name   =product_name,
                description    =  description,
                Sub_category   =subcategory_id, 
                category_id    =main_category_id,
                min_price      =min_price,  
                max_price      =max_price,
                image          =image,
                product_offer  =offer,
            )
            return redirect('product')
        context = {'categories': categories,
                    'sections': sections
                   }
        return render(request, 'addproduct.html', context)
    else:
        return redirect('admin')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache 
def editproduct(request,product_id):
    if 'admin' in request.session:
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
        
            return render(request, 'product_not_found.html')
        
        categories = Category.objects.all()
        section = Section.objects.all()
        context = {
            'product'    : product,
            'categories' : categories,
            'section'    : section,
        }

        return render(request, 'edit_product.html', context)
    else:
        return redirect('admin')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def update(request, product_id):
    product = Product.objects.get(id=product_id)
   
    if request.method == 'POST':
        product.product_name    =   request.POST.get('product_name')
        product.description     =   request.POST.get('description')
        category_name           =   request.POST.get('category')
        category                =   Category.objects.get(category_name=category_name)
        product.category        =   category
        name                    =   request.POST.get('section')
        section                 =   get_object_or_404(Section, name=name)
        product.section         =   section
        product.min_price               =   request.POST.get('min_price')  
        product.max_price               =   request.POST.get('max_price')
        
        
        image                   =   request.FILES.get('image')
        product.product_offer          =   request.POST.get('offer') 
        images                  =   request.FILES.getlist('mulimage')

        if image:
            product.image = image
        
        product.save()
        for img in images:
            product_image = Images(product=product)
            product_image.images = img
            product_image.save()   
        return redirect('product') 
    else:
        context = {
            'product': product
        }
    return render(request, 'products.html', context)
   



def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.deleted = True
        product.save()
    except Product.DoesNotExist:
         return render(request, 'product_not_found.html')
    return redirect('product')

def restore_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.deleted = False  
        product.save()
    except Product.DoesNotExist:
        pass
    return redirect('product')


def unblock_customer(request, customer_id):
    try:
        customer =CustomUser.objects.get(id=customer_id)
    except ObjectDoesNotExist:
        return redirect('customer')  
    
    customer.is_active = not customer.is_active
    customer.save()

    return redirect('customer')


def block_customer(request, customer_id):
    try:
        customer = CustomUser.objects.get(id=customer_id)
    except CustomUser.DoesNotExist:
        return redirect('customer')  
    customer.is_active = False
    customer.save()
    return redirect('customer')


#section

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def section(request):
    if 'admin' in request.session:
        sections = Section.objects.all().order_by('id')
        
        
        paginator = Paginator(sections, per_page=3)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'sections': page_obj,
        }
        return render(request, 'section.html', context)
    else:
        return redirect('admin')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache          
def addsection(request):
    if 'admin' in request.session:
        if request.method  == 'POST':
            name   =   request.POST['name']
            

            section = Section.objects.create(
             name  =  name,
                
                  
            )
            section.save() 

            return redirect('section')  
        return render(request, 'addsection.html') 
    else:
        return redirect ('admin')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def editsection(request, section_id):
    if 'admin' in request.session:
        try:
            section = Section.objects.get(id=section_id)
        except Section.DoesNotExist:
            return render(request, 'subcategory_not_found.html')

        context = {'section': section}
        return render(request, 'editsection.html', context)
    else:
        return redirect ('admin')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def update_section(request, id):
    try:
        section = Section.objects.get(id=id)
    except Section.DoesNotExist:
        return render(request, 'category_not_found.html')

    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            section.name           =  name
        
        section.save()
        return redirect('section')

    context = {'section': section}
    return render(request, 'edit_section.html', context)
def delete_section(request, section_id):
    try:
         section = Section.objects.get(id=section_id)
         section.active = not section.active
         section.save()
    except Section.DoesNotExist:
         return render(request, 'section_not_found.html')
    section = Section.objects.all()
    context={'section':section}
    return redirect('section')
#wishlist

def wish(request):
    user = request.user
    if not user.is_authenticated:
        # Redirect to the signup page
        return redirect('signup')
    wishlist_items = Wishlist.objects.filter(user=user)
    variation_images = []
    for item in wishlist_items:
        # Retrieve the variation associated with the wishlist item
        variation = item.variation
        # Get the first image associated with the variation, if available.
        first_variation_image = Variation_img.objects.filter(variation=variation).first()
        variation_images.append(first_variation_image)
    items_with_images = list(zip(wishlist_items, variation_images))
    context = {
        'items_with_images': items_with_images
    }
    return render(request, 'wishlist.html', context)
def add_to_wishlist(request, id):
    try:
        variation = Variation.objects.get(id=id)
    except variation.DoesNotExist:
        return redirect('product_not_found')
    
    user = request.user
    wishlist, created = Wishlist.objects.get_or_create(variation=variation, user=user)
    if created:
        pass
    wishlist.save()
    return redirect('wish')
def remove_from_wishlist(request,id):
    try:
        if request.user.is_authenticated:
            wishlist_item = Wishlist.objects.get(id=id, user=request.user)
        wishlist_item.delete()
    except Wishlist.DoesNotExist:
        pass
    return redirect('wish')
#coupon
@never_cache
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def coupon(request):
    if 'admin' in request.session:
        coupons = Coupon.objects.all().order_by('id')
        context = {'coupons': coupons}
        return render(request, 'coupon.html', context)
    else:
        return redirect('admin')
def addcoupon(request):
    if request.method == 'POST':
        coupon_code    = request.POST.get('Couponcode')
        discount_price  = request.POST.get('dprice')
        minimum_amount = request.POST.get('amount')
        expiry_date = request.POST.get('date')
        print(f"Expiry Date: {expiry_date}")
        if float(discount_price) < 0:
            messages.error(request, 'Discount price cannot be less than 0')
            return redirect('coupon')
        if float(minimum_amount) < 0:
            messages.error(request, 'Minimum price cannot be less than 0')
            return redirect('coupon')
        coupon = Coupon(coupon_code=coupon_code, discount_price=discount_price, minimum_amount=minimum_amount,expiry_date=expiry_date)
        coupon.save()
        return redirect('coupon')
def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        try:
            coupon = Coupon.objects.get(coupon_code=coupon_code)
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code')
            request.session['discount'] = 0
            return redirect('checkout')
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        subtotal =Decimal('0.00') 
        shipping_cost = Decimal('1500.00')
        total_dict = {}
        coupons = Coupon.objects.all()
        request.session['discount'] = coupon.discount_price
        for cart_item in cart_items:
            if cart_item.quantity > cart_item.variation.stock:
                messages.warning(request, f"{cart_item.variation.product.product_name} is out of stock.")
                cart_item.quantity = cart_item.variation.stock
                cart_item.save()
            if cart_item.variation.product.category.category_offer:
                item_price = (cart_item.variation.price - (cart_item.variation.price * Decimal(cart_item.variation.product.category.category_offer / Decimal(100)))) * cart_item.quantity
                total_dict[cart_item.id] = item_price
                subtotal += item_price
            elif cart_item.variation.product.product_offer:
                item_price = (cart_item.variation.price - (cart_item.variation.price * Decimal(cart_item.variation.product.product_offer / Decimal(100)))) * cart_item.quantity
                total_dict[cart_item.id] = item_price
                subtotal += item_price
            else:
                item_price = cart_item.variation.price * cart_item.quantity
                total_dict[cart_item.id] = item_price
                subtotal += item_price
        if subtotal >= coupon.minimum_amount:
            messages.success(request, 'Coupon applied successfully')
            request.session['discount'] = coupon.discount_price
            total = subtotal - coupon.discount_price + shipping_cost
        else:
            messages.error(request, 'Coupon not available for this price')
            request.session['discount'] = 0
            total = subtotal + shipping_cost

        for cart_item in cart_items:
            cart_item.total_price = total_dict.get(cart_item.id, 0)
            cart_item.save()
        address = Address.objects.filter(user=user,is_deleted=False)
        shipping = Shipping.objects.filter(user=user,is_deleted=False)
        context = {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'total': total,
            'coupons': coupons,
            'discount_amount': coupon.discount_price,
            'user': user, 
            'address': address,
            'shipping': shipping,
        }
        return render(request, 'checkout.html', context)
    return redirect('checkout')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def editcoupon(request,coupon_id):
    if 'admin' in request.session:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
        except Section.DoesNotExist:
            return render(request, 'subcategory_not_found.html')
        context = {'coupon': coupon}
        return render(request, 'edit_coupon.html', context)
    else:
        return redirect ('admin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def update_coupon(request, id):
    # Use get_object_or_404 to retrieve the coupon or return a 404 page if it doesn't exist
    coupon = get_object_or_404(Coupon, id=id)

    if request.method == 'POST':
        coupon_code = request.POST.get('Couponcode')
        discount_price = request.POST.get('price')
        minimum_amount = request.POST.get('amount')
        expiry_date = request.POST.get('date')
        
        # Check if coupon_code and discount_price are not null before updating
        if coupon_code:
            coupon.coupon_code = coupon_code
        if discount_price:
            coupon.discount_price = discount_price
        if expiry_date:
            coupon.expiry_date = expiry_date

        coupon.minimum_amount = minimum_amount
        
        coupon.save()  # Save the updated coupon object here

        return redirect('coupon')

    context = {'coupon': coupon}
    return render(request, 'edit_coupon.html', context)

def delete_coupon(request,coupon_id):
    try:
        coupon= Coupon.objects.get(id=coupon_id)
    except Coupon.DoesNotExist:
        return render(request, 'category_not_found.html')

    coupon.deleted = True
    coupon.save()

    coupons = Coupon.objects.filter(deleted=False)
    context = {'coupons': coupons}

    return redirect('coupon')
def restock_coupon(order):
    order_items = OrderItem.objects.filter(order=order)
    for order_item in order_items:
        variation = order_item.variation
        variation.stock += order_item.quantity
        variation.save()



    