"""dropgrocer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from home.views import *
from home import views
router = DefaultRouter()


router.register('users', views.UsersViewSet)
router.register('vehicledoctype', views.VehicleDocTypeViewSet)
router.register('address', views.AddressViewSet, basename='address')
router.register('nearbyaddress', views.NearByAddressViewSet, basename='nearbyaddress')
router.register('vehicle', views.VehicleViewSet)
router.register('vehicledoucment',views.VehicleDocumentViewSet)
router.register('dg/v/banner', views.BannerViewSet)
router.register('category', views.CategoryViewSet)
router.register('manufacturer',views.ManufacturerViewSet)
router.register('tax', views.TaxViewSet)
router.register('product', views.ProductViewSet)
router.register('recentbought', views.RecentBoughtViewSet, basename = 'recentbought')
router.register('availability', views.AvailabilityViewSet)
router.register('discount', views.DiscountViewSet)
router.register('wishlist', views.WishlistViewSet, basename='wishlist')
router.register('cart', views.CartViewSet, basename='cart')
router.register('order', views.OrderViewSet, basename='order')
router.register('payment', views.PaymentViewSet)
router.register('support', views.SupportViewSet)
router.register('rating', views.RatingViewSet)
router.register('faqs', views.FaqViewSet)
router.register('continent', views.ContinentViewSet)
router.register('language', views.LanguageViewSet)
router.register('country', views.CountryViewSet)
router.register('state', views.StateViewSet)
router.register('region', views.RegionViewSet)
router.register('page', views.PageViewSet)
router.register('vehicletype', views.VehicleTypeViewSet)
router.register('doctype', views.DocTypeViewSet)
router.register('document', views.DocumentViewSet)
router.register('popup', views.PopupViewSet)
router.register('delivercharge', views.DeliveryChargeViewSet)
router.register('over18', views.Over18ViewSet)


    
urlpatterns = [
   
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('dropgrocer/',include('home.urls')),
    path('ckeditor',include('ckeditor_uploader.urls')),
    path('login/', views.UserLoginView.as_view(), name='UserLoginView'),
	path('sociallogin/', views.SocialUserLoginView.as_view(), name='SocialUserLoginView'),
	path('socialsignup/', views.SocialUserCreationView.as_view(), name='SocialUserCreationView'),
	path('signup/', views.UserCreationView.as_view(), name='UserCreationSerializer'),
	path('driver-signup/', views.DriverCreationView.as_view(), name='DriverCreationSerializer'),
	path('changepassword/', views.ChangePasswordView.as_view(), name='ChangePasswordView'),
	path('forgotpassword/', views.ForgotPasswordView.as_view(), name='ForgotPasswordView'),
	path('verifymobile/', views.VerifyMobileView.as_view(), name='VerifyMobileView'),
	path('cartlist/', views.CartListView.as_view(), name='CartListView'),
	path('cancel-order/<int:pk>/', views.CancelOrderView.as_view(), name='cancel-order'),
   
 ]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


