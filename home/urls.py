from .views import *
from . import views
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('invoice/<pk>/', InvoiceDetails.as_view(), name='invoice'),
    path('order/<pk>/', OrderDetails.as_view(), name='order-details'),
    path('order/', MyOrder.as_view(), name = 'order'),
    path('rating/<slug>/', productrating, name='productrating'),
    path('order/<int:pk>/success/', ordertsuccess, name = 'order-successful'),
	path('', HomeListView.as_view(), name='home'),
    path('track/<pk>/', ordertrack, name = 'track'),
	path('rating/', views.rating, name='rating'),
	path('signup/', userregistration, name = 'signup'),
	path('login/', auth_views.LoginView.as_view(template_name = 'login.html'), name = 'login'),
	path('logout/', auth_views.LogoutView.as_view(), name = 'logout'),
	path('shop/', ProductList.as_view(), name = 'products'),
	path('category/<slug>/products/', subcategoryproduct, name = 'subcategory'),
	path('shop/<slug>/', ProductDetailView.as_view(), name = 'product'),
	path('categories/', CategoryListView.as_view(), name = 'category_list'),
	path('account/', MyAccount.as_view(), name = 'account'),
	path('profile/', UserProfileView.as_view(), name = 'profile'),
    path('user/',user_edit,name='user_edit'),
	path('address/', CurrentAddressList.as_view(), name = 'address'),
	path('address-edit/<int:pk>/', addressedit, name = 'addressedit'),
	path('checkout/', checkoutview, name = 'checkout'),
	path('newaddress/', newaddressadd, name = 'new_address'),
	path('wishlist/', WishListView.as_view(), name = 'wishlist'),
	path('category/<slug>/products/', subcategoryproduct, name = 'subcategory'),
	path('add_wishlist',add_wishlist, name = 'add_wishlist'),
	path('wishorder/<int:uid>', wishorder, name = 'wishorder'),
	path('wishlist/delete-wishlist', delete_wishlist, name = 'delete-wishlist'),
	path('cart/', CartListView.as_view(), name = 'cart'),
	path('add-to-cart', add_to_cart, name = 'add-to-cart'),
	path('shop/add-to-cart', add_to_cart, name = 'add-to-cart'),
	path('cart/decrement', wishlist_quantity_minus, name = 'decrement'),
	path('shop/decrement', wishlist_quantity_minus, name = 'decrement'),
	path('star-rating', starrating, name = 'star-rating'),
	path('payment/<int:order>/', payment, name = 'payment'),
	path('category/<slug>/', subcategory, name = 'category'),
    path('how-it-work/', howitwork, name = 'howitwork'),
	path('business/', business, name = 'business'),
    path('selling-policies/', sellingpolicy, name = 'sellingpolicy'),
    path('terms/', termsandcondition, name = 'terms'),
    path('search/', searchproduct, name = 'search'),
    path('searchlive', searchlive, name = 'searchlive'),
	path('shop/add_wishlist',add_wishlist, name = 'add_wishlist'),
	path('order/<int:pk>/success/', ordertsuccess, name = 'order-successful'),
	path('shop/<slug>/decrement', wishlist_quantity_minus_pro, name = 'decrement'),
	path('shop/<slug>/add-to-cart', add_to_cart_pro, name = 'add-to-cart'),
	path('decrement', wishlist_quantity_minus, name = 'decrement'),
	path('sign/', sign, name = 'sign'),
	path('subscribe/', SubscribeView.as_view(), name = 'subscribe'),
	path('paypal/', paypal, name = 'paypal'),
    
]