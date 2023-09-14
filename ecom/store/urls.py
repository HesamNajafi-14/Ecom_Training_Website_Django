from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('register/', views.registerPage, name="register_page"),
    path('login/', views.loginPage, name="login_page"),
    path('logout/', views.logoutPage, name="logout"),
]