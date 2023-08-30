from django.shortcuts import render
from django.http import JsonResponse
import json
from .models import *

# Create your views here.

def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']

    products = Product.objects.all()
    context = {'products':products, 'cartItems':cartItems}
    return render(request, 'store/store.html', context)

def cart(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']

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