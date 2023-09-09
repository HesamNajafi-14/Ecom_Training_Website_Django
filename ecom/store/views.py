from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from . models import *
from . utils import cookieCart, cartData, guestOrder

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
    # Load JSON data from the request body
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    # Print action and productId for debugging
    print('Action:', action)
    print('productId:', productId)

    # Get the customer and product objects
    customer = request.user.customer
    product = Product.objects.get(id=productId)

    # Get or create an order for the customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    # Get or create the order item for the product in the current order
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    # Update the quantity based on the action
    if action == 'add':
        order_item.quantity += 1
    elif action == 'remove':
        order_item.quantity -= 1

    # Save the order item
    order_item.save()

    # If the quantity becomes <= 0, delete the order item
    if order_item.quantity <= 0:
        order_item.delete()

    # Return a response indicating success
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