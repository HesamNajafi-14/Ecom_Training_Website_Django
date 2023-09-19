from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from . models import *
from . utils import cookieCart, cartData, guestOrder
from django.contrib.auth.models import User
from django.contrib import messages, auth
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages


# Create your views here.

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('store')
    else:
        form = CreateUserForm()

        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                user = form.save()  # Save the user object

                # Create a Customer linked to the user
                customer, created = Customer.objects.get_or_create(user=user)

                # If the customer was just created, you can set additional fields here
                if created:
                    customer.name = user.username  # Set a default name
                    customer.email = user.email  # Set the email from the user
                    customer.save()

                messages.success(request, 'Account was created for ' + user.username)
                # Log in the user after registration
                return redirect('login')  # Redirect to the desired page after registration

        context = {'form': form}
        return render(request, 'store/register_page.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('store') 
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('store')
            else:
                messages.info(request,'Username or Password incorrect!')
                

        context = {}
        return render(request, 'store/login_page.html', context)

def logoutPage(request):
    logout(request)
    return redirect('store')

def store(request):
    
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products':products, 'cartItems':cartItems}
    return render(request, 'store/store.html', context)

def cart(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    
   
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('ProductId:', productId)

    if request.user.is_authenticated:
        customer = request.user.customer
    else:
        # Handle the guest user case here, if needed
        customer, order = guestOrder(request, data)

    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was updated', safe=False)
# from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        

        
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],

        )


    return JsonResponse('Payment complete!', safe=False)



