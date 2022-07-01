from django.urls import path
from core import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.search, name='search'),
    path('add_item', views.add_item, name='add_item'),
    path('item_description/<int:pk>', views.item_description, name='item_description'),
    path('item_image/<int:pk>', views.item_image, name='item_image'),
    path('add_to_cart/<int:pk>', views.add_to_cart, name='add_to_cart'),
    path('order_list', views.order_list, name='order_list'),
    path('remove_from_cart/<int:pk>', views.remove_from_cart, name='remove_from_cart'),
    path('checkout', views.checkout_page, name='checkout_page'),
    path('payment', views.payment, name='payment'),
    path('handlerequest', views.handlerequest, name='handlerequest'),
    path('invoice', views.invoice, name='invoice'), 
]

