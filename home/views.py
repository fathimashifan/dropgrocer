from django.shortcuts import render,get_object_or_404,redirect
from rest_framework import generics, serializers, viewsets, mixins, status as status_code
from django.views import generic
from .models import *
from django.core.mail import send_mail
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.utils.translation import gettext as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from .forms import *
from django.core import serializers
from rest_framework import viewsets
import json
from .serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework import mixins
import datetime

# Create your views here.

class CartListView(APIView):
	permission_classes = ((AllowAny,))
	def post(self, request):
		# ordr = Order.objects.last()
		# ordr.note=str(request.data)
		# ordr.save()
		# return Response({'response':request.data})
		method = 'http'
		if request.is_secure():
			method = 'https'

		data = str(request.data['products']).replace("'",'"')
		data = json.loads(data)
		customer = request.data['customer']
		if int(customer) > 0:
			user = User.objects.get(id=int(customer))
		items = []
		if len(data) == 0:
			return Response({'count':1, 'next':None, 'previous':None, 'results':{'total':0, 'itemlist':[]} })
		total_amount = 0
		charges = DeliveryCharge.objects.filter(status='Active').last()
		tax = Tax.objects.filter(status='Active').last()
		for prod in data:
			prd = Product.objects.filter(id=prod['product_id']).last()
			if prd != None:
				total_amount += round(prd.price*int(prod['qty']),2) 
				items.append({'id':0, 'price':prd.price, 'quantity':int(prod['qty']), 'total':round(prd.price*int(prod['qty']),2), 'products':{ 'id':prd.id, 'title':prd.title, 'content':prd.content, 'short_description':prd.short_description, 'price':prd.price, 'adult':prd.adult, 'weight':prd.weight, 'weight_type':prd.weight_type, 'min_limit':prd.min_limit, 'max_limit':prd.max_limit, 'utimestamp':prd.utimestamp, 'utimestamp':prd.utimestamp, 'image':method+'://'+request.get_host()+prd.image.url, 'rating':{'total':0, 'average':0, '1':0, '2':0, '3':0, '4':0, '5':0} } })
			if int(customer) > 0 and prd != None:
				Wishlist.objects.create(product=prd, user=user, quantity=int(prod['qty']), cart=True)
		return Response({'count':1, 'next':None, 'previous':None, 'results':{'total':total_amount, 'charges':{'amount':charges.amount}, 'tax':{'percentage':tax.percentage},'itemlist':items} })

class UsersViewSet(viewsets.ModelViewSet):
	queryset = User.objects.filter(is_active=True).all()
	serializer_class = UserSerializer
	filter_fields = ['email', 'mobile', 'parent']
	http_method_names = ['get','post','put','patch']
	# filter_backends = [filters.SearchFilter]
	# search_fields = ['username', 'email',]

class UserLoginView(APIView):
	permission_classes = ((AllowAny,))
	def post(self, request):
		serializer = UserLoginSerializer(data=request.data)
		if serializer.is_valid():
			user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'],)
			if user is not None:
				try:
					token = Token.objects.get(user=user).delete()
				except:
					pass

				token = Token.objects.create(user=user)
				token = Token.objects.get(user=user)
				if user.dob is None:
					user.dob = ''
				vtype = 0
				if user.vtype != None:
					vtype = user.vtype.id
				country = 0
				if user.country != None:
					country = user.country.id

				user_data = dict(username=user.username, first_name=user.first_name, last_name=user.last_name, role =user.role, email=user.email, mobile=user.mobile, vtype =vtype, country=country,  dob = user.dob, token=token.key, id=user.pk)
				return Response({'success':True,'data':user_data})
			else:
				return Response({'error':_('Given credentials do not match')}, status=status_code.HTTP_400_BAD_REQUEST)
		# return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		return Response({'error':_('Given credentials do not match')}, status=status_code.HTTP_400_BAD_REQUEST)

class SocialUserLoginView(APIView):
	permission_classes = ((AllowAny,))
	def post(self, request):
		serializer = SocialUserSignupSerializer(data = request.data)
		if serializer.is_valid():
			password = User.objects.make_random_password()
			try:
				email = serializer.validated_data['email']
			except:
				email = ''
			socialid = serializer.validated_data['socialid']
			username = socialid
			if not email or email == '':
				email = str(socialid)+'@dgr.com'
			try:
				user = User.objects.create_user(socialid = socialid, first_name = serializer.validated_data['first_name'], last_name = serializer.validated_data['last_name'],email = email,username = username, password = password)
			except Exception as e:
				try:
					user = User.objects.get(socialid = socialid)
				except:
					user = User.objects.filter(username = username)
					user.update(socialid = socialid)
					user = user.last()

			if user:
				try:
					token = Token.objects.get(user=user.id).delete()
				except:
					pass
				token = Token.objects.create(user=user)

				if user.dob is None:
					user.dob = ''
				vtype = 0
				if user.vtype != None:
					vtype = user.vtype.id
				country = 0
				if user.country != None:
					country = user.country.id

				user_data = dict(username=user.username, first_name=user.first_name, last_name=user.last_name, role =user.role, email=user.email, mobile=user.mobile, vtype =vtype, country=country,  dob = user.dob, token=token.key, id=user.pk)
				return Response({'success':True,'data':user_data})
			return Response({'error':_('Something went wrong.')}, status=status_code.HTTP_400_BAD_REQUEST)
		return Response({'error':_('Please provide all required data.')}, status=status_code.HTTP_400_BAD_REQUEST)

class SocialUserCreationView(generics.GenericAPIView,mixins.CreateModelMixin):
	permission_classes = ((AllowAny,))
	queryset = User.objects.all()
	serializer_class = SocialUserSignupSerializer

	def post(self, request, *args, **kwargs):
		return self.create(request, *args, **kwargs)

class UserCreationView(generics.GenericAPIView,mixins.CreateModelMixin):
	permission_classes = ((AllowAny,))
	queryset = User.objects.all()
	serializer_class = UserCreationSerializer

	def post(self, request, *args, **kwargs):
		if request.data['password'] != request.data['cpassword']:
			raise serializers.ValidationError(_('Passwords do not match'))
		return self.create(request, *args, **kwargs)

class DriverCreationView(generics.GenericAPIView,mixins.CreateModelMixin):
	permission_classes = ((AllowAny,))
	queryset = User.objects.all()
	serializer_class = DriverCreationSerializer

	def post(self, request, *args, **kwargs):
		if request.data['password'] != request.data['cpassword']:
			raise serializers.ValidationError(_('Passwords do not match'))
		return self.create(request, *args, **kwargs)

class ChangePasswordView(APIView):
	def post(self, request):
		serializer = UserLoginSerializer(data=request.data)
		if serializer.is_valid():
			user = authenticate(backend='home.backends.MyMobileBackend', username=serializer.validated_data['username'], password=serializer.validated_data['password'],)
			if user is not None and request.data['npassword'] == request.data['cpassword']:
				user.set_password(request.data['npassword'])
				user.save()
				return Response({'success':True,'message':_('Password changed Successfully.')})
		return Response({'error':'Authentication Missmatch...!'}, status=status_code.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
	permission_classes = ((AllowAny,))
	def post(self, request):
		serializer = UserForgotSerializer(data=request.data)
		# print(serializer, "Demo", status_code)
		if serializer.is_valid():
			user = User.objects.filter(mobile=serializer.validated_data['mobile']).last()
			if user is not None and request.data['npassword'] == request.data['cpassword']:
				user.set_password(request.data['npassword'])
				user.save()
				return Response({'success':True,'message':_('Password changed Successfully.')})
		return Response({'error':_('Authentication Missmatch...!')}, status=status_code.HTTP_400_BAD_REQUEST)

class VerifyMobileView(APIView):
	permission_classes = ((AllowAny,))
	def post(self, request):
		serializer = UserForgotSerializer(data=request.data)
		# print(serializer, "Demo", status_code)
		if serializer.is_valid():
			user = User.objects.filter(mobile=serializer.validated_data['mobile'])
			if len(user)>0:
				return Response({'success':True,'message':_('Mobile Number exist.')})
		return Response({'success':False,'message':_('Mobile Number not exist.')}, status=status_code.HTTP_400_BAD_REQUEST)


class VehicleDocTypeViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = VehicleDocType.objects.filter(status = 'Active')
	serializer_class = VehicleDocTypeSerializer
	filter_fields = ['title', 'vtype',]
	http_method_names = ['get','post','put','patch']

class AddressViewSet(viewsets.ModelViewSet):
	# queryset = Address.objects.filter(status = 'Active')
	serializer_class = AddressSerializer
	filter_fields = ['user', 'country', 'state', 'title', 'city', 'postcode',]
	http_method_names = ['get','post','put','patch']

	def get_queryset(self):
		user = self.request.user
		return Address.objects.filter(user=user)

class NearByAddressViewSet(viewsets.ModelViewSet):
	serializer_class = AddressSerializer
	filter_fields = ['postcode',]
	http_method_names = ['get','post','put','patch']

	def get_queryset(self):
		user = self.request.user
		return Address.objects.filter(user__role = 'Seller', status = 'Active')

class DocTypeViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = DocType.objects.filter(status = 'Active')
	serializer_class = DocTypeSerializer
	filter_fields = ['title']
	http_method_names = ['get']

class DocumentViewSet(viewsets.ModelViewSet):
	queryset = Document.objects.filter(status = 'Active')
	serializer_class = DocumentSerializer
	filter_fields = ['user', 'doctype']
	http_method_names = ['get','post','put','patch','delete']

class VehicleViewSet(viewsets.ModelViewSet):
	queryset = Vehicle.objects.filter(status = 'Active')
	serializer_class = VehicleSerializer
	filter_fields = ['user','vtype','number',]
	http_method_names = ['get','post','put','patch']

class VehicleDocumentViewSet(viewsets.ModelViewSet):
	queryset = VehicleDocument.objects.filter(status = 'Active')
	serializer_class = VehicleDocumentSerializer
	filter_fields = ['vehicle',]
	http_method_names = ['get','post','put','patch']

class BannerViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = Banner.objects.filter(status = 'Active')
	print("resrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
	print(queryset)
	serializer_class = BannerSerializer
	filter_fields = ['title', 'web', 'mobile',]
	http_method_names = ['get','post','put','patch']

class CategoryViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = Category.objects.filter(status = 'Active')
	serializer_class = CategorySerializer
	# filter_fields = ['title','parent']
	filter_fields = {'title': ['startswith', 'exact'], 'parent':['exact']}
	http_method_names = ['get','post','put','patch']

class ManufacturerViewSet(viewsets.ModelViewSet):
	queryset = Manufacturer.objects.filter(status = 'Active')
	serializer_class = ManufacturerSerializer
	filter_fields = ['title', 'estd' , 'email', 'mobile',]
	http_method_names = ['get','post','put','patch']

class TaxViewSet(viewsets.ModelViewSet):
	queryset = Tax.objects.filter(status = 'Active')
	serializer_class = TaxSerializer
	filter_fields = ['title', 'code' , 'percentage',]
	http_method_names = ['get','post','put','patch']


class ProductViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = Product.objects.filter(status = 'Active')
	serializer_class = ProductSerializer
	filter_fields = {
				'title': ['startswith', 'exact', 'icontains'], 
				'category':['exact']
				}

	http_method_names = ['get','post','put','patch']

	def get_queryset(self, *args, **kwargs):
		queryset = super().get_queryset()
		sort_by = self.request.GET.get('sort_by', None)
		if sort_by and sort_by != '':
			if sort_by == 'alphabate':
				queryset = queryset.order_by('title')
			if sort_by == 'offers':
				queryset = queryset.order_by('-discount')
			if sort_by == 'daily-deal':
				queryset = queryset.filter(fsale=True)
			if sort_by == 'recently-bought':
				if self.request.user.is_authenticated:
					queryset = queryset.filter(id__in = Wishlist.objects.filter(user=self.request.user).values_list('product', flat=True))
				else:
					queryset = queryset.none()
			if sort_by == 'seasonal':
				queryset = queryset.filter(seasonal=True)
		return queryset

class RecentBoughtViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	serializer_class = ProductSerializer
	queryset = Product.objects.filter(status = 'Active')
	filter_fields = ['category', 'title',]
	http_method_names = ['get','post','put','patch']

class AvailabilityViewSet(viewsets.ModelViewSet):
	queryset = Availability.objects.filter(status = 'Active')
	serializer_class = AvailabilitySerializer
	filter_fields = ['product','seller', 'quantity', 'sales',]
	http_method_names = ['get','post','put','patch']

class DiscountViewSet(viewsets.ModelViewSet):
	today = datetime.datetime.now()
	queryset = Discount.objects.filter(status = 'Active', valid__gte=today)
	serializer_class = DiscountSerializer
	filter_fields = ['title', 'code',]
	http_method_names = ['get','post','put','patch']

class WishlistViewSet(viewsets.ModelViewSet):
	# queryset = Wishlist.objects.filter(cart = False, status = 'Active')
	serializer_class = WishlistSerializer
	filter_fields = ['user','product','quantity', 'price', 'total', 'cart',]
	http_method_names = ['get','post','put','patch', 'delete']

	def get_queryset(self):
		user = self.request.user
		return Wishlist.objects.filter(cart = False, status = 'Active', user=user).order_by('id')

class CartViewSet(viewsets.ModelViewSet):
	# queryset = Wishlist.objects.filter(cart = True, status = 'Active')
	serializer_class = WishlistSerializer
	filter_fields = ['user','product','quantity', 'price', 'total', 'cart',]
	http_method_names = ['get','post','put','patch', 'delete']

	def get_queryset(self):
		user = self.request.user
		return Wishlist.objects.filter(cart = True, status = 'Active', user=user)

	
	def list(self, request, *args, **kwargs):
		queryset = self.filter_queryset(self.get_queryset())

		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			final = serializer.data
			total = Wishlist.objects.filter(cart=True, status = 'Active', user = self.request.user).aggregate(Sum('total'))['total__sum']
			tax = Tax.objects.filter(status= 'Active').values('percentage').last()
			charge = DeliveryCharge.objects.filter(status = 'Active').values('amount').last()
			if tax == None:
				tax = 0
			if charge == None:
				charge = 0
			if total == None:
				total = 0
			return self.get_paginated_response({'total':total,'tax':tax,'charges':charge,'itemlist':final})

		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)

class OrderViewSet(viewsets.ModelViewSet):
	# queryset = Order.objects.all().order_by('-id')
	serializer_class = OrderSerializer
	filter_fields = ['discount', 'wishlist', 'address', 'total', 'seller', 'driver', 'price', 'date', 'status']
	http_method_names = ['get','post','put','patch']

	def get_queryset(self):
		user = self.request.user
		if user.role == 'Customer':
			return Order.objects.filter(address__user=user).order_by('-id')
		if user.role == 'Driver':
			return Order.objects.filter(driver=user).order_by('-utimestamp')
		if user.role == 'Seller':
			return Order.objects.filter(seller=user).order_by('-id')
		return Order.objects.all().order_by('-id')

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		wishorder(request,serializer.data['addresss']['user'])
		new_S = OrderSerializer(Order.objects.get(id=serializer.data['id']), context={'request': request})
		
		return Response(new_S.data, status=status_code.HTTP_201_CREATED, headers=headers)

class DeliveryChargeViewSet(viewsets.ModelViewSet):
	queryset = DeliveryCharge.objects.filter(status = 'Active')
	serializer_class = DeliveryChargeSerializer
	filter_fields = ['title','amount',]
	http_method_names = ['get','post','put','patch']

class Over18ViewSet(viewsets.ModelViewSet):
	queryset = Over18.objects.filter(status = 'Active')
	serializer_class = Over18Serializer
	filter_fields = ['order','country', 'dob',]
	http_method_names = ['get','post','put','patch']

class PaymentViewSet(viewsets.ModelViewSet):
	queryset = Payment.objects.filter(status = 'Active')
	serializer_class = PaymentSerializer
	filter_fields = ['order', 'method', 'amount', 'payed',]
	http_method_names = ['get','post','put','patch']


class SupportViewSet(viewsets.ModelViewSet):
	queryset = Support.objects.filter(status = 'Active')
	serializer_class = SupportSerializer
	filter_fields = ['user','order','parent', 'title',]
	http_method_names = ['get','post','put','patch']

class RatingViewSet(viewsets.ModelViewSet):
	queryset = Rating.objects.filter(status = 'Active')
	serializer_class = RatingSerializer
	filter_fields = ['product','user','star',]
	http_method_names = ['get','post','put','patch']

	# def create(self, validated_data):
	# 	product = validated_data.pop('product')
	# 	user = validated_data.pop('user')
	# 	rating = Rating.objects.get_or_create(**validated_data)
	# 	return **validated_data

class FaqViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = Faq.objects.filter(status = 'Active')
	serializer_class = FaqSerializer
	filter_fields = ['title',]
	http_method_names = ['get','post','put','patch']

class ContinentViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = Continent.objects.filter(status = 'Active')
	serializer_class = ContinentSerializer
	filter_fields = ['title', 'area', 'population',]
	http_method_names = ['get','post','put','patch']

class LanguageViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = Language.objects.filter(status = 'Active')
	serializer_class = LanguageSerializer
	filter_fields = ['code', 'name', 'pattern',]
	http_method_names = ['get','post','put','patch']

class CountryViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = Country.objects.filter(status = 'Active')
	serializer_class = CountrySerializer
	filter_fields = ['continent', 'name', 'local', 'code', 'code2', 'code3', 'capital', 'gdp', 'area', 'population',]
	http_method_names = ['get','post','put','patch']

class StateViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = State.objects.filter(status = 'Active')
	serializer_class = StateSerializer
	filter_fields = ['country', 'title', 'capital', 'local', 'area', 'population',]
	http_method_names = ['get','post','put','patch']

class RegionViewSet(viewsets.ModelViewSet):
	queryset = Region.objects.filter(status = 'Active')
	serializer_class = RegionSerializer
	filter_fields = ['state', 'title',]
	http_method_names = ['get','post','put','patch']

class PageViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = Page.objects.filter(status = 'Active')
	serializer_class = PageSerializer
	filter_fields = ['title',]
	http_method_names = ['get','post','put','patch']

class VehicleTypeViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = VehicleType.objects.filter(status = 'Active')
	serializer_class = VehicleTypeSerializer
	filter_fields = ['title',]
	http_method_names = ['get','post','put','patch']

class PopupViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = Popup.objects.filter(status = 'Active')
	serializer_class = PopupSerializer
	filter_fields = ['title',]
	http_method_names = ['get','post','put','patch']


class CancelOrderView(APIView):
	def get(self, request, pk):
		try:
			order = Order.objects.filter(pk=pk).first()
			wishlist = order.wishlist.all()
			for wl in wishlist:
				wl.status = 'Active'
				wl.save()
			Over18.objects.filter(order=order).delete()
			order.delete()
			return Response({'details':_('Order cancelled successfully.')}, status=status_code.HTTP_200_OK)
		except Exception as e:
			print(e)
			return Response({'error':_('Something went wrong.')}, status=status_code.HTTP_400_BAD_REQUEST)



def sign(request):
	return render(request, 'sign.html',)

def business(request):
	country = Country.objects.filter(name = 'UAE', status = 'Active')
	state = State.objects.filter(country__name = 'UAE', status = 'Active')
	language =LANGUAGES
	if request.method == 'POST':
		store = request.POST.get('store')
		latitude = request.POST.get('latitude')
		longitute = request.POST.get('longitute')
		postcode = request.POST.get('postcode')
		address = request.POST.get('address')
		city = request.POST.get('city')
		state = request.POST.get('state')
		country = request.POST.get('country')
		if state == 'State' or country == 'Country' or latitude == '' or longitute == '':
			return redirect('business')
		else:
			ucountry = Country.objects.get(name = country)
			ustate = State.objects.get(title = state) 
			locationad = Address.objects.create(user = request.user, title = store, latitude = latitude, longitute = longitute, postcode = postcode, address = address, city = city, state = ustate, country = ucountry)
			locationad.save()
			return redirect('admin:index')
	return render(request, 'business.html', {'country':country, 'state':state, 'language':language})

class HomeListView(generic.TemplateView):
	template_name = 'home.html'

	# def get(self, request):
	# 	if request.user.is_authenticated:
	# 		if request.user.role == 'Admin' or request.user.role == 'Seller':
	# 			return redirect('/dgr/')

	# 	return super().get(request)

	def get_context_data(self, **kwargs):
        
		context = super(HomeListView, self).get_context_data(**kwargs)
		# print(self.request.user.auth_token)
		context['product_list'] = Product.objects.filter(status = 'Active').order_by('title')
		context['category_list'] = Category.objects.filter(status = 'Active', ).order_by('title')
		context['subcategory_list'] = Category.objects.exclude(parent = None).filter(status = 'Active').order_by('title')
		# context['rating'] = Rating.objects.filter(status = 'Active', user = self.request.user, product=context['product'].id)
		context['banner'] = Banner.objects.filter(status = 'Active', web = True)
        
		# context['product_wishlist']
		return context


def rating(request):
    p= Category.objects.filter(status = 'Active', ).order_by('title')
    print(p)

    return render(request, 'rating.html',)



def userregistration(request):
	stdcode = Country.objects.filter(status = 'Active')
	if request.method == 'POST':
		print("27268298777777777777777")
		username = request.POST.get('username')
		print(username)
		email = request.POST.get('email')
		password = request.POST.get('password1')
		confirm_psd = request.POST.get('password2')
		mobile = request.POST.get('mobile')
		code = request.POST.get('ccode')
		if password == confirm_psd:
			if User.objects.filter(username = username).exists():
				messages.info(request, _('username already exists...!'))
				return redirect('signup')
			elif User.objects.filter(email = email).exists():
				messages.info(request, _('Email already exists...!'))
				return redirect('signup')
			elif User.objects.filter(mobile = mobile).exists():
				messages.info(request, _('mobile number already exists...!'))
				return redirect('signup')
			else:
				print("sdkahghdhasgggggggggggg")
				if code:
					print("44444444444444444333333333333333333")
					user = User.objects.create_user(username = username, email = email, password = password, mobile = mobile)
					# user.is_active = False
					print("11111111111111111111111")
					user.save()
					user = authenticate(username = username, password = password)
					login(request, user)
					print("rrrrrrrrrrrrrrrrrrrrr")
					return redirect('login')
				else:
					messages.info(request, _('select country code'))
					return redirect('signup')
					print("[[[[[[[[[[[[[[[[[[")
		else:
			messages.info(request, _('password mismatch...!'))
			return redirect('signup')
	else:
		print("555555555555555")
		return render(request, 'signup.html', {'stdcode':stdcode})

class ProductList(generic.ListView):
	template_name = 'product.html'
	context_object_name = 'products'
	paginate_by = 2
	queryset = Product.objects.filter(status = 'Active').order_by('title')

	def get_context_data(self, **kwargs):
		context = super(ProductList, self).get_context_data(**kwargs)
		context['category_list'] =  Category.objects.filter(status = 'Active', ).order_by('title')
		context['wishlist'] = Wishlist.objects.filter(status = 'Active')
		return context

		
	
def subcategoryproduct(request, slug):
	# category = get_object_or_404(Category, slug = slug, status = 'Active')
	subcategory =  Category.objects.get(slug = slug, status = 'Active')
	product = Product.objects.filter(category = subcategory, status = 'Active')
	category_list = Category.objects.filter(status = 'Active').order_by('title')
	paginator=Paginator(product, 12)
	page=request.GET.get('page', 1)
	try:
		users = paginator.page(page)
	except PageNotAnInteger:
		users = paginator.page(1)
	except EmptyPage:
		users = paginator.page(paginator.num_pages)
	return render(request, 'subcategory.html',{'category':subcategory, 'users':users, 'category_list':category_list})

class ProductDetailView(generic.DetailView):
	model = Product
	template_name = 'product_details.html'
	context_object_name = 'product'

	def get_context_data(self, **kwargs):
		context = super(ProductDetailView, self).get_context_data(**kwargs)
		context['category_list'] = Category.objects.exclude(parent = None).filter(status = 'Active').order_by('title')
		context['product_image'] = ProductImage.objects.filter(product = context['product'].id)
		return context
class CategoryListView(generic.ListView):
	template_name = 'category_list.html'
	slug_field = 'slug'
	paginate_by = 10

	queryset = Category.objects.filter(status = 'Active', parent__isnull = True).order_by('title')

	def get_context_data(self, **kwargs):
        
		context = super(CategoryListView, self).get_context_data(**kwargs)
	
		
		context['category_list'] = Category.objects.filter(status = 'Active', ).order_by('title')
		
		return context


		

class MyAccount(generic.TemplateView):
	template_name = 'main-account.html'	


class UserProfileView(generic.ListView):
	context_object_name = 'category_list'
	template_name = 'profile.html'
	queryset = Category.objects.exclude(parent = None).filter(status = 'Active').order_by('title')
@login_required
def user_edit(request):
	if request.method == 'POST':
		form = UserProfileForm(request.POST, request.FILES, instance=request.user)
		print('5555555555555', form.is_valid())
		if form.is_valid():
			form.save()
			return redirect('/dropgrocer/profile/')
	else:
		form = UserProfileForm(None, instance=request.user)
	return render(request,'user_edit.html', {'form': form})
class CurrentAddressList(generic.ListView):
	model = Address
	template_name = 'address.html'
	context_object_name = 'addresslist'

	def get_queryset(self):
		queryset = super(CurrentAddressList, self).get_queryset()
		if self.request.user.is_authenticated:
			queryset = Address.objects.filter(user = self.request.user, status = 'Active')
			return queryset
		else:
			return Address.objects.none()
def addressedit(request, pk):
	address = get_object_or_404(Address, pk=pk)
	if request.method == 'POST':
		form = NewDeliverAddress(request.POST, instance = address)
		if form.is_valid():
			addr = form.save(commit = False)
			addr.user = request.user
			addr.save()
			return redirect('address')
	else:
		form = NewDeliverAddress(instance = address)
		return render(request, 'address_edit.html', {'form':form})
@login_required
def checkoutview(request):
	category_list = Category.objects.filter(status = 'Active', parent = None).order_by('-utimestamp')
	currentadd = Address.objects.filter(user = request.user)
	country = Country.objects.filter(status = 'Active', name = 'UAE')
	state = State.objects.filter(country__name = 'UAE', status = 'Active')
	wishlistitem = Wishlist.objects.filter(status = 'Active', cart = True, user = request.user)
	print(wishlistitem)
	# a = Wishlist.objects.filter(user=context['request'].user.id , status = 'Active', cart = True)
	
	if request.method == 'POST':
		note = request.POST.get('note')
		# print(note)
		date = request.POST.get('orderdate')
		time = request.POST.get('ordertime')
		addressid = request.POST.get('addressid')
		# Wishlist.status='Active'
		# Wishlist.save()
		
		if not addressid:
			messages.info(request, _('address not selected'))
			return redirect('checkout')
		else:
			currentadd = Address.objects.get(id = addressid, user = request.user)
	    
		
		try:
			promdis = request.session['discount']
		except:
			promdis = ''
		
		adult = False
		if not wishlistitem:
			return redirect('home')
		else:
			try:
				addtime = datetime.strptime(date+' '+time, '%Y-%m-%d %H:%M')
				current_order = Order.objects.create(address = currentadd, date = addtime)
				print(wishlistitem)
			except:
				current_order = Order.objects.create(address = currentadd)
			if note:
				current_order.note = note
				current_order.save()
			if promdis != '':
				try:
					discountt = Discount.objects.get(code = promdis)
					current_order.discount = discountt
					current_order.save()
					del request.session['discount']
				except: pass

			for ids in wishlistitem:
				current_order.wishlist.add(ids)
				if ids.product.adult:
					adult = True
			current_order.adult = adult
			current_order.save()
			
			


			
			
			if current_order.adult:
				form = Over18Form(request.POST, request.FILES)
				if form.is_valid():
					over18 = form.save(commit=False)
					over18.order = current_order
					over18.country = current_order.address.country
					over18.save()
                    
			return redirect('payment', order=current_order.id)

	else:
		print(wishlistitem)	
		
		adult = False
		for ids in wishlistitem:
			if ids.product.adult:
				adult = True
		if adult:
			form = Over18Form()
		else:
			form = None
    	
	return render(request, 'checkout.html', {'category_list':category_list, 'currentadd':currentadd, 'country':country, 'state':state, 'form':form})



def newaddressadd(request):
	country = Country.objects.filter(status = 'Active', name = 'UAE')
	state = State.objects.filter(country__name = 'UAE', status = 'Active')
	if request.method == 'POST':
		title = request.POST.get('title')
		address = request.POST.get('address')
		city = request.POST.get('city')
		pincode = request.POST.get('pincode')
		state = request.POST.get('state')
		country = request.POST.get('country')
		if 'select state' in state or 'select country' in country:
			messages.info(request, _('select state and country'))
			return redirect('new_address')
		cinst = Country.objects.get(name = country)
		sinst = State.objects.get(title = state)
		f= Address(user =request.user , title = title, address = address, city = city, postcode = pincode ,state = sinst, country = cinst)
		f.save()
		return redirect('checkout')
	return render(request, 'new_address.html', {'country':country, 'state':state})

class WishListView(generic.ListView):
	model = Wishlist
	template_name = 'wishlist.html'
	context_object_name = 'wishlists'
	# paginate_by = 10

	def get_queryset(self):
		queryset = super(WishListView, self).get_queryset()
		if self.request.user.is_authenticated:
			queryset = queryset.filter(user = self.request.user, status = 'Active', cart = False).order_by('product__title')
			return queryset
			print("8888888888")
			print(queryset)
		else:
			return Wishlist.objects.none()

	def get_context_data(self, **kwargs):
		context = super(WishListView, self).get_context_data(**kwargs)
		context['category_list'] =  Category.objects.filter(status = 'Active', ).order_by('title')
		
		if self.request.user.is_authenticated:
			context['wishlist_sum'] = Wishlist.objects.filter(user = self.request.user, status = 'Active', cart = False).aggregate(Sum('total'))['total__sum']
		return context
		print("55555555555555")
		print(context)

def subcategoryproduct(request, slug):
	# category = get_object_or_404(Category, slug = slug, status = 'Active')
	subcategory =  Category.objects.get(slug = slug, status = 'Active')
	product = Product.objects.filter(category = subcategory, status = 'Active')
	category_list = Category.objects.filter(status = 'Active').order_by('title')
	paginator=Paginator(product, 12)
	page=request.GET.get('page', 1)
	try:
		users = paginator.page(page)
	except PageNotAnInteger:
		users = paginator.page(1)
	except EmptyPage:
		users = paginator.page(paginator.num_pages)
	return render(request, 'subcategory.html',{'category':subcategory, 'users':users, 'category_list':category_list})


@login_required
def add_wishlist(request):
	addclass = False
	pid = request.POST.get('prodid')
	product = get_object_or_404(Product, id = pid)
	wl = Wishlist.objects.filter(product = product, user = request.user, cart = False, status = 'Active')
	if wl.exists():
		wl.delete()
		addclass = False
	else:
		if Wishlist.objects.filter(product = product, user = request.user, cart = True, status = 'Active').exists():
			addclass = False
		else:
			wishlist_item = Wishlist.objects.create(product = product, user = request.user, cart = False)
			addclass = True
	allwishlist = Wishlist.objects.filter(status = 'Active', user = request.user, cart = False)
	ser_wishlist = serializers.serialize('json', allwishlist)
	return JsonResponse({"wishlist12": ser_wishlist, 'addclass':addclass}, safe = False)

def wishorder(request,uid):
	wishlist = Wishlist.objects.filter(user=uid, status='Active')
	order = Order.objects.filter(address__user=uid).last()
	adult = False
	for wish in wishlist:
		order.wishlist.add(wish)
		if wish.product.adult:
			adult = True
	order.adult = adult
	order.save()
	wishlist.update(status='Inactive')
	return HttpResponse("Success")
@login_required
def delete_wishlist(request):
	pid = request.POST.get('deletepid')
	print(pid)
	print("ggggggg")
	cartnm = request.POST.get('cartpname')
	print("cartnm")
	product = get_object_or_404(Product, id = pid)
	print("ssssssssssssssss")
	wl = Wishlist.objects.get(product = product, user = request.user, cart = False, status = 'Active')
	if cartnm:
		if wl:
			wl.cart = True
			wl.quantity =1
		wl.save()
	else:
		wl.delete()
	allwishlist = Wishlist.objects.filter(status = 'Active', user = request.user, cart = True)
	ser_wishlist = serializers.serialize('json', allwishlist)
	totalcunt = allwishlist.aggregate(Sum('total'))['total__sum']
	updated_wishl = serializers.serialize('json', [wl,])
	deliverych = DeliveryCharge.objects.filter(status = 'Active').values('amount').last()
	return JsonResponse({'dcharge':deliverych['amount'],'wishlist':updated_wishl,"wishlistdel": ser_wishlist, 'totalcunt':totalcunt}, safe = False)
class CartListView(generic.ListView):
	model = Wishlist
	template_name = 'cart.html'
	context_object_name = 'wishlists'
	# paginate_by = 10

	def get_queryset(self):
		queryset = super(CartListView, self).get_queryset()
		if self.request.user.is_authenticated:
			queryset = queryset.filter(user = self.request.user, status = 'Active', cart = True).order_by('product__title')
			return queryset
		else:
			return Wishlist.objects.none()

	def get_context_data(self, **kwargs):
		context = super(CartListView, self).get_context_data(**kwargs)
		context['category_list'] = Category.objects.exclude(parent = None).filter(status = 'Active').order_by('title')
		context['product_list'] = Product.objects.filter(status = 'Active').order_by('title')[:8]
		context['delvery_charge'] = DeliveryCharge.objects.filter(status = 'Active').last()

		if self.request.user.is_authenticated:
			context['wishlist_sum'] = Wishlist.objects.filter(user = self.request.user, status = 'Active', cart = True).aggregate(Sum('total'))['total__sum']
		return context
@login_required
def add_to_cart(request):
	
	
	data = request.POST.get('prodid')
	print(data)
	print("tttttttttttt")
	name = request.POST.get('pname')
	print(name)
	prodquantity = request.POST.get('quantity')
	print(prodquantity)
	product = get_object_or_404(Product, id = data)

	if str(request.user)=='AnonymousUser':
		if request.session.has_key('product'):
			request.session['product'] = request.session['product']+"|"+str(request.POST.get('prodid'))
			request.session['quantity'] = request.session['quantity']+"|"+str(request.POST.get('quantity'))
			# print('Update old')add_to_cart
		else:
			request.session['product'] = str(request.POST.get('prodid'))
			request.session['quantity'] = str(request.POST.get('quantity'))
		
		# print(request.session['product'])
		products = request.session['product'].split("|")
		quantity = request.session['quantity'].split("|")
		ser_wishlist = []
		total = 0
		for index, pdt in enumerate(products):
			product = Product.objects.get(pk=pdt)
			total += round(product.price*int(quantity[index]),2)
			ser_wishlist.append({'model':'home.wishlist', 'pk':product.id, 'fields':{'product':product.id, 'quantity':quantity[index]} })
		return JsonResponse({"wishlist": ser_wishlist, 'wishlist-count':total, 'currentwishlist':ser_wishlist, "user_auth":request.user.is_authenticated}, safe = False)
	
	if product.stock_availbility():
		try:
			wishlist_data = Wishlist.objects.get(product = product, user = request.user, status='Active')
		except:
			wishlist_data = None

	if wishlist_data is None and product.stock_availbility():
		wishlist_data = Wishlist.objects.create(product = product, user = request.user, cart=True)
	
	if wishlist_data.cart:
		if int(prodquantity) > 0:
			if product.stock_availbility() and int(prodquantity) <= product.stock_num():
				wishlist_data.quantity = int(prodquantity)
		else:
			if product.stock_availbility() and (wishlist_data.quantity + 1) <= product.stock_num():
				wishlist_data.quantity += 1

		if product.stock_availbility():
			qty = wishlist_data.quantity
			if qty > product.max_limit:
				qty = product.max_limit
			if qty < product.min_limit:
				qty = product.min_limit
			if qty <= product.stock_num():
				wishlist_data.quantity = qty
			wishlist_data.save()

	currentwishlist = serializers.serialize('json', [wishlist_data,])
	allwishlist = Wishlist.objects.filter(status = 'Active', user = request.user, cart = True)
	totalcunt = allwishlist.aggregate(Sum('total'))['total__sum']
	ser_wishlist = serializers.serialize('json', allwishlist)
	return JsonResponse({"wishlist": ser_wishlist, 'wishlist-count':totalcunt, 'currentwishlist':currentwishlist, "user_auth":request.user.is_authenticated}, safe = False)
@login_required
def wishlist_quantity_minus(request):
	data = request.POST.get('minusval')
	print(data)
	product_id = request.POST.get('product_id')
	print(product_id)
	cartname = request.POST.get('cartdele')
	print(cartname)
	minus = request.POST.get('classname')
	print(minus)
	product = 	get_object_or_404(Product, id = product_id)
	is_less = False
	wishlist = Wishlist.objects.filter(product = product, user = request.user, cart = True, status = 'Active')
	deliverych = DeliveryCharge.objects.filter(status = 'Active').values('amount').last()
	
	if wishlist.exists():
		wishlist = wishlist.first()
		if cartname:
			wishlist.delete()
		else:
			if int(data) == 0:
				wishlist.quantity = 0
				wishlist.delete()
			else:
				if product.stock_availbility() and int(data) <= product.stock_num():
					wishlist.quantity = int(data)
					wishlist.save()
				else:
					is_less = True
					

		ser_wishlist = serializers.serialize('json', [wishlist,])
		wishlistd = Wishlist.objects.filter(status = 'Active', user = request.user, cart = True)
		delete_wishlist = serializers.serialize('json', wishlistd)
		totalcunt = wishlistd.aggregate(Sum('total'))['total__sum']
		return JsonResponse({'dcharge':deliverych['amount'],"wishlist": ser_wishlist, 'totalcunt':totalcunt, 'delete_wishlist':delete_wishlist, 'stock_num':product.stock_num(), 'is_less':is_less}, safe = False)
	wl = Wishlist.objects.filter(status = 'Active', user = request.user, cart = True)
	totalcunt = wl.aggregate(Sum('total'))['total__sum']
	if not totalcunt:
		totalcunt = 0
	# ser_wishlist = serializers.serialize('json', [wishlist,])
	return JsonResponse({"error": _('product not found'), 'dcharge':deliverych['amount'],"wishlist": [], 'totalcunt':totalcunt}, safe = False)

@login_required
def starrating(request):
	starrate = request.POST.get('rating')
	productid = request.POST.get('productid')
	starcreate = Rating.objects.create(user = request.user, product_id = productid, star = starrate)
	ser_wishlist = serializers.serialize('json', [starcreate,])
	return JsonResponse({"wishlist": ser_wishlist}, safe = False)
def ordertrack(request, pk):
	order = Order.objects.filter(pk = pk, address__user = request.user.id).last()
	try:
		address = Address.objects.filter(user = order.seller.id).last()
		return render(request, 'track.html', {'order':order, 'address':address})
	except:
		return render(request, 'track.html', {'order':order})    

class MyOrder(generic.ListView):
	model = Order
	template_name = 'order.html'
	context_object_name = 'orderlist'

	def get_queryset(self):
		queryset = super(MyOrder, self).get_queryset()
		if self.request.user.is_authenticated:
			queryset = Order.objects.filter(address__user = self.request.user.id).order_by('-utimestamp')
			return queryset
		else:
			return Order.objects.none()

class OrderDetails(generic.DetailView):
	model = Order
	template_name = 'order-details.html'
	context_object_name = 'order'

	def get_context_data(self, **kwargs):
		context = super(OrderDetails, self).get_context_data(**kwargs)
		context['delivery_charge'] = DeliveryCharge.objects.last()
		return context

	def post(self, request, *args, **kwargs):
		if request.method == 'POST':
			order = request.POST.get('orderid')
			ratingnum = request.POST.get('rating')
			customer = request.POST.get('username')
			productid = request.POST.get('product')
			review = request.POST.get('message')
			curr_prd = Product.objects.get(id = productid)
			curr_user = User.objects.get(id = customer)
			rateing = Rating.objects.create(product = curr_prd, user = curr_user, star = ratingnum, review = review)
			return redirect('order-details', pk = int(order))
class InvoiceDetails(generic.DetailView):
	model = Order
	template_name = 'invoice.html'
	context_object_name = 'order'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['delivery_charge'] = DeliveryCharge.objects.last()
		return context
def productrating(request, slug):
	product=Product.objects.get(slug=slug)
	if request.method == 'POST':
		ratingnum = request.POST.get('rating')
		customer = request.POST.get('username')
		productid = request.POST.get('product')
		review = request.POST.get('message')
		curr_prd = Product.objects.get(id = productid)
		curr_user = User.objects.get(id = customer)
		if Rating.objects.filter(product = curr_prd, user = curr_user, status= 'Active').exists():
			messages.info(request, _('already given rating on product'))
			return redirect('productrating', product.slug)
		else:
			if int(ratingnum) >=1 and int(ratingnum) <=5:
				rateing = Rating.objects.get_or_create(product = curr_prd, user = curr_user, star = ratingnum, review = review)
			else:
				messages.info(request, _('rating value input 1 to 5'))
				return redirect('productrating', product.slug)
		return redirect('order')
	return render(request, 'product-rating.html',{'product':product})            

def ordertsuccess(request, pk):
	order = Order.objects.filter(pk = pk).last()
	try:
		if request.method == 'POST':
			paypal = request.POST.get('paypal')
			order.paymode = paypal
			order.save()
		address = Address.objects.filter(user = order.seller.id).last()
		return render(request, 'order_successful.html', {'order':order, 'address':address})
	except Exception as e:
		print(e)
		return render(request, 'order_successful.html', {'order':order})        
def payment(request, order=None):
	if order:
		orderid = Order.objects.filter(id=order).first()
	else:
		orderid = Order.objects.filter(address__user = request.user.id).last()
	if orderid.adult:
		form = Over18Form()
	else:
		form = None
	if request.method == 'POST':
		wishlistitem = Wishlist.objects.filter(status = 'Active', cart = True, user = request.user)
		print(wishlistitem)
		print("555555555555")
		payp = request.POST.get('paypal')
		if 'COD' in payp:
			orderid.paymode = 'COD'
		else:
			orderid.paymode = 'PAYAPL'
		orderid.save()
		wishlistitem = Wishlist.objects.filter(status = 'Active', cart = True, user = request.user)
		Wishlist.status = 'Active'
		Wishlist.save()
		
		
		print(wishlistitem)
		print("555555555555")
	else:
		wishlistitem = Wishlist.objects.filter(status = 'Active', cart = True, user = request.user)
		print(wishlistitem)
		print("rrrrrrrrrrrr")

	return render(request, 'payment.html', {'orderid':orderid, 'form':form})

def subcategory(request, slug):
	category = get_object_or_404(Category, slug = slug, status = 'Active')
	subcategory =  Category.objects.filter(parent = category, status = 'Active')
	category_list = Category.objects.exclude(parent = None).filter(status = 'Active').order_by('title')
	if request.method == 'GET':
		selecttype = request.GET.get('orderby')
		if selecttype == None:
			pass
		elif 'alphabatically' in selecttype:
			subcategory.order_by('title')
		elif 'offers' in selecttype:
			subcategory.order_by('timestamp')
		elif 'daily-deal' in selecttype:
			subcategory.order_by('timestamp')
		elif 'recently-bought' in selecttype:
			print('recently-bought')
		elif 'seasonal' in selecttype:
			print('seasonal')

	paginator=Paginator(subcategory, 12)
	page=request.GET.get('page', 1)
	try:
		users = paginator.page(page)
	except PageNotAnInteger:
		users = paginator.page(1)
	except EmptyPage:
		users = paginator.page(paginator.num_pages)
	return render(request, 'category.html',{'category':category,'users':users, 'category_list':category_list, 'subcategory':subcategory})

def howitwork(request):
	try:
		cpage = Page.objects.get(slug = 'how-it-work', status = 'Active')
		return render(request, 'staticpage.html', {'cpage':cpage})
	except:
		return render(request, 'staticpage.html')
def sellingpolicy(request):
	try:
		cpage = Page.objects.get(slug = 'selling-policies', status = 'Active')
		return render(request, 'staticpage.html', {'cpage':cpage})
	except:
		return render(request, 'staticpage.html')
def termsandcondition(request):
	try:
		cpage = Page.objects.get(slug = 'terms', status = 'Active')
		return render(request, 'staticpage.html', {'cpage':cpage})
	except:
		return render(request, 'staticpage.html')

def searchproduct(request):
	categoryl = Category.objects.exclude(parent = None).filter(status = 'Active').order_by('title')
	if request.method == 'GET':
		inuputty = request.GET.get('inputtext')
		categoryna = request.GET.get('categoryname')
		products = Product.objects.filter(title__icontains = inuputty)
		if categoryna and categoryna != '':
			products = products.filter(category__id = int(categoryna))
		return render(request, 'search-product.html', {'plist':products, 'category_list':categoryl})        

def searchlive(request):
	category = request.POST.get("category")
	print(category)
	search = request.POST.get("search")
	print(search)
	products = Product.objects.filter(title__icontains=search)
	print(products)
	result = ''
	print(result)
	if len(category)>0:
		print("tttttttttttttttttt")
		products.filter(category=category)
		print("oooooooooooooooooooooo")
	for product in products:
		print("99999999999999999")
		result += '<li><a href="/shop/'+product.slug+'/">'+product.title+'</a></li>'
		print(result)
	return JsonResponse({'success':True,'data':result})
def ordertsuccess(request, pk):
	order = Order.objects.filter(pk = pk).last()
	try:
		if request.method == 'POST':
			paypal = request.POST.get('paypal')
			order.paymode = paypal
			order.save()
		address = Address.objects.filter(user = order.seller.id).last()
		return render(request, 'order_successful.html', {'order':order, 'address':address})
	except Exception as e:
		print(e)
		return render(request, 'order_successful.html', {'order':order})
@login_required
def add_to_cart_pro(request,slug):
	
	print(slug)
	data = request.POST.get('prodid')
	print(data)
	print("tttttttttttt")
	name = request.POST.get('pname')
	print(name)
	prodquantity = request.POST.get('quantity')
	print(prodquantity)
	product = get_object_or_404(Product, id = data)

	if str(request.user)=='AnonymousUser':
		if request.session.has_key('product'):
			request.session['product'] = request.session['product']+"|"+str(request.POST.get('prodid'))
			request.session['quantity'] = request.session['quantity']+"|"+str(request.POST.get('quantity'))
			# print('Update old')add_to_cart
		else:
			request.session['product'] = str(request.POST.get('prodid'))
			request.session['quantity'] = str(request.POST.get('quantity'))
		
		# print(request.session['product'])
		products = request.session['product'].split("|")
		quantity = request.session['quantity'].split("|")
		ser_wishlist = []
		total = 0
		for index, pdt in enumerate(products):
			product = Product.objects.get(pk=pdt)
			total += round(product.price*int(quantity[index]),2)
			ser_wishlist.append({'model':'home.wishlist', 'pk':product.id, 'fields':{'product':product.id, 'quantity':quantity[index]} })
		return JsonResponse({"wishlist": ser_wishlist, 'wishlist-count':total, 'currentwishlist':ser_wishlist, "user_auth":request.user.is_authenticated}, safe = False)
	
	if product.stock_availbility():
		try:
			wishlist_data = Wishlist.objects.get(product = product, user = request.user, status='Active')
		except:
			wishlist_data = None

	if wishlist_data is None and product.stock_availbility():
		wishlist_data = Wishlist.objects.create(product = product, user = request.user, cart=True)
	
	if wishlist_data.cart:
		if int(prodquantity) > 0:
			if product.stock_availbility() and int(prodquantity) <= product.stock_num():
				wishlist_data.quantity = int(prodquantity)
		else:
			if product.stock_availbility() and (wishlist_data.quantity + 1) <= product.stock_num():
				wishlist_data.quantity += 1

		if product.stock_availbility():
			qty = wishlist_data.quantity
			if qty > product.max_limit:
				qty = product.max_limit
			if qty < product.min_limit:
				qty = product.min_limit
			if qty <= product.stock_num():
				wishlist_data.quantity = qty
			wishlist_data.save()

	currentwishlist = serializers.serialize('json', [wishlist_data,])
	allwishlist = Wishlist.objects.filter(status = 'Active', user = request.user, cart = True)
	totalcunt = allwishlist.aggregate(Sum('total'))['total__sum']
	ser_wishlist = serializers.serialize('json', allwishlist)
	return JsonResponse({"wishlist": ser_wishlist, 'wishlist-count':totalcunt, 'currentwishlist':currentwishlist, "user_auth":request.user.is_authenticated}, safe = False)
@login_required
def wishlist_quantity_minus_pro(request,slug):
	data = request.POST.get('minusval')
	print(data)
	product_id = request.POST.get('product_id')
	print(product_id)
	cartname = request.POST.get('cartdele')
	print(cartname)
	minus = request.POST.get('classname')
	print(minus)
	product = 	get_object_or_404(Product, id = product_id)
	is_less = False
	wishlist = Wishlist.objects.filter(product = product, user = request.user, cart = True, status = 'Active')
	deliverych = DeliveryCharge.objects.filter(status = 'Active').values('amount').last()
	
	if wishlist.exists():
		wishlist = wishlist.first()
		if cartname:
			wishlist.delete()
		else:
			if int(data) == 0:
				wishlist.quantity = 0
				wishlist.delete()
			else:
				if product.stock_availbility() and int(data) <= product.stock_num():
					wishlist.quantity = int(data)
					wishlist.save()
				else:
					is_less = True
					

		ser_wishlist = serializers.serialize('json', [wishlist,])
		wishlistd = Wishlist.objects.filter(status = 'Active', user = request.user, cart = True)
		delete_wishlist = serializers.serialize('json', wishlistd)
		totalcunt = wishlistd.aggregate(Sum('total'))['total__sum']
		return JsonResponse({'dcharge':deliverych['amount'],"wishlist": ser_wishlist, 'totalcunt':totalcunt, 'delete_wishlist':delete_wishlist, 'stock_num':product.stock_num(), 'is_less':is_less}, safe = False)
	wl = Wishlist.objects.filter(status = 'Active', user = request.user, cart = True)
	totalcunt = wl.aggregate(Sum('total'))['total__sum']
	if not totalcunt:
		totalcunt = 0
	# ser_wishlist = serializers.serialize('json', [wishlist,])
	return JsonResponse({"error": _('product not found'), 'dcharge':deliverych['amount'],"wishlist": [], 'totalcunt':totalcunt}, safe = False)
class SubscribeView(generic.FormView):
	template_name = 'subscribe.html'
	form_class = SubscribeForm

	def form_valid(self, form):
		email=form.cleaned_data.get('email')
		form.save()
		subject=_('Thank you for subscribing to dropgrocer')
		message=_('dropgrocer welcomes you.')
		email_from = EMAIL_HOST_USER
		send_mail(subject, message, email_from, [email], fail_silently=False)
		return super(SubscribeView, self).form_valid(form)

	def get_success_url(self, *args, **kwargs):
		return reverse('subscribe')

def paypal(request):
	rowdata = request.POST.get('data')
	data = json.loads(rowdata)

	order = Order.objects.filter(address__user=request.user.id).last()
	payment = Payment.objects.create(order=order, transaction=data['id'], amount=data['purchase_units'][0]['amount']['value'], payed=data['purchase_units'][0]['amount']['value'], currency=data['purchase_units'][0]['amount']['currency_code'], email=data['payer']['email_address'], name=str(data['payer']['name']['given_name'])+' '+data['payer']['name']['surname'], rawdata=rowdata)
	return JsonResponse({'success':True, 'order':order.id})		