from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from . models import *
from . utils import cookieCart, cartData, guestOrder
from django.contrib.auth.models import User
from django.contrib import messages, auth
from django.contrib.auth import login, authenticate, logout
from .forms import CustomRegistrationForm

# Create your views here.

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

    customer = request.user.customer
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


def registerPage(request):
    page = 'register'
    form = CustomRegistrationForm()

    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            user = authenticate(
                request, username=user.username, password=request.POST['password1'])
            
            if user is not None:
                login(request, user)
                return redirect('store')

    context = {'form': form, 'page': page}
    return render(request, 'store/register_page.html', context)


def loginPage(request):
    page = 'login'
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        print('USER:', user)
        if user is not None:
            login(request, user)
            return redirect('store')
    return render(request, 'store/login_page.html', {'page':page})

def logoutPage(request):
    logout(request)
    return redirect('store')
