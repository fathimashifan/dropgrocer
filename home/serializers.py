from rest_framework.authtoken.models import Token
from rest_framework import serializers
# from fcm_django.models import FCMDevice
from .models import *
from geolocation.models import *

class VehicleTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model = VehicleType
		exclude = ('timestamp', 'track', 'utrack')

class VehicleDocTypeSerializer(serializers.ModelSerializer):
	vehicles = VehicleTypeSerializer(source = 'vtype', read_only=True)
	class Meta:
		model = VehicleDocType
		exclude = ('timestamp', 'track', 'utrack')

class UserSerializer(serializers.ModelSerializer):
	vehicles = VehicleTypeSerializer(source = 'vtype', read_only=True)
	class Meta:
		model = User
		exclude = ('user_permissions','groups','password','is_staff','is_superuser','date_joined', 'track', 'utrack',)

class UserLoginSerializer(serializers.Serializer):
	username = serializers.CharField()
	password = serializers.CharField(style={'input_type': 'password'})


class SocialUserSignupSerializer(serializers.Serializer):
	# username = serializers.CharField()
	# socialtype = serializers.CharField()
	first_name = serializers.CharField()
	last_name = serializers.CharField()
	email = serializers.EmailField(required=False)
	socialid = serializers.CharField()
	token = serializers.CharField(source='auth_token.key',read_only=True)

	class Meta:
		model = User
		fields = ('username','role','password','cpassword','email','mobile','first_name','last_name','token','id', 'vtype' ,'country', 'type', 'socialid', 'socialtype', 'registration_id')

	def create(self, validated_data):
		password = User.objects.make_random_password()
		user = User.objects.create_user(username=validated_data['email'] ,email=validated_data['email'], socialid=validated_data['socialid'], password=password)
		user.first_name = validated_data['first_name']
		user.last_name = validated_data['last_name']
		user.save()
		return user

class UserForgotSerializer(serializers.Serializer):
	mobile = serializers.CharField()
	# password = serializers.CharField(style={'input_type': 'password'})

class UserCreationSerializer(serializers.ModelSerializer):
	password = serializers.CharField(style={'input_type': 'password'},write_only=True)
	cpassword = serializers.CharField(style={'input_type': 'password'},write_only=True)
	registration_id = serializers.CharField(style={'input_type': 'text'},write_only=True)
	device_id = serializers.CharField(style={'input_type': 'text'},write_only=True)
	type = serializers.CharField(style={'input_type': 'text'},write_only=True)
	token = serializers.CharField(read_only=True)
	# id = serializers.CharField(read_only=True)

	class Meta:
		model = User
		fields = ('username','role','password','cpassword','email','mobile','first_name','last_name','token','id', 'vtype' ,'country', 'type', 'device_id', 'registration_id')

	def create(self, validated_data):
		user = User.objects.create_user(username=validated_data['username'], role=validated_data['role'], email=validated_data['email'], password=validated_data['password'], mobile=validated_data['mobile'], country=validated_data['country'])
		user.first_name = validated_data['first_name']
		user.last_name = validated_data['last_name']
		user.save()
		try:
			token = Token.objects.create(user=user)
		except:
			token = Token.objects.get(user=user)
		user.token = token
		if len(validated_data['registration_id']) >5:
			FCMDevice.objects.create(name=validated_data['username'], registration_id=validated_data['registration_id'], device_id=validated_data['device_id'], type=validated_data['type'] )
		# id = int(user.pk)
		return user

class DriverCreationSerializer(serializers.ModelSerializer):
	password = serializers.CharField(style={'input_type': 'password'},write_only=True)
	cpassword = serializers.CharField(style={'input_type': 'password'},write_only=True)
	registration_id = serializers.CharField(style={'input_type': 'text'},write_only=True)
	device_id = serializers.CharField(style={'input_type': 'text'},write_only=True)
	type = serializers.CharField(style={'input_type': 'text'},write_only=True)
	token = serializers.CharField(read_only=True)
	# id = serializers.CharField(read_only=True)

	class Meta:
		model = User
		fields = ('username','role','password','cpassword','email','mobile','first_name','last_name','dob','token','id', 'vtype', 'country', 'type', 'device_id', 'registration_id')

	def create(self, validated_data):
		user = User.objects.create_user(username=validated_data['username'], role=validated_data['role'], email=validated_data['email'], dob=validated_data['dob'], password=validated_data['password'], mobile=validated_data['mobile'], vtype=validated_data['vtype'], country=validated_data['country'])
		user.first_name = validated_data['first_name']
		user.last_name = validated_data['last_name']
		user.vtype = validated_data['vtype']
		user.save()
		try:
			token = Token.objects.create(user=user)
		except:
			token = Token.objects.get(user=user)
		user.token = token
		# print(validated_data)
		if len(validated_data['registration_id']) >5:
			# print(user.pk)
			FCMDevice.objects.create(user = user, name=validated_data['username'], registration_id=validated_data['registration_id'], device_id=validated_data['device_id'], type=validated_data['type'] )
		# id = int(user.pk)
		return user

class AddressSerializer(serializers.ModelSerializer):
	countries = serializers.SerializerMethodField('c_title')
	states = serializers.SerializerMethodField('s_title')
	class Meta:
		model = Address
		# fields = '__all__'
		exclude = ('timestamp', 'track', 'utrack')

	def c_title(self,obj):
		tit = Country.objects.filter(id = obj.country.id).values('name')[0]['name']
		return tit

	def s_title(self,obj):
		name = State.objects.filter(id = obj.state.id).values('title')[0]['title']
		return name

class DocTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model = DocType
		exclude = ('timestamp', 'track', 'utrack')

class DocumentSerializer(serializers.ModelSerializer):
	category = serializers.SerializerMethodField('cat')
	class Meta:
		model = Document
		exclude = ('timestamp', 'track', 'utrack')

	def cat(self, obj):
		return obj.doctype.title

class VehicleSerializer(serializers.ModelSerializer):
	# users = UserSerializer(source = 'user', read_only=True)
	vehicles = VehicleTypeSerializer(source = 'vtype', read_only=True)
	class Meta:
		model = Vehicle
		# fields = '__all__'
		exclude = ('timestamp', 'track', 'utrack')

class VehicleDocumentSerializer(serializers.ModelSerializer):
	vehicles = VehicleSerializer(source = 'vehicle', read_only=True)
	class Meta:
		model = VehicleDocument
		exclude = ('timestamp', 'track', 'utrack')


class BannerSerializer(serializers.ModelSerializer):
	class Meta:
		model = Banner
		# fields = '__all__'
		exclude = ('timestamp', 'track', 'utrack')

class CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = Category
		# fields = '__all__'
		exclude = ('timestamp', 'track', 'utrack')

class ManufacturerSerializer(serializers.ModelSerializer):
	class Meta:
		model = Manufacturer
		# fields = '__all__'
		exclude = ('timestamp', 'track', 'utrack')


class TaxSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tax
		# fields = '__all__'
		exclude = ('timestamp', 'track', 'utrack')

class ProductImageSerializer(serializers.ModelSerializer):
	class Meta:
		model = ProductImage
		fields = ('id','image','utimestamp')

class ProductSerializer(serializers.ModelSerializer):
	# users = UserSerializer(source = 'admin')
	categories = CategorySerializer(source = 'category', many = True, read_only=True)
	manufacturers = ManufacturerSerializer(source = 'manufacturer', read_only=True)
	taxes = TaxSerializer(source = 'tax', read_only=True)
	rating = serializers.SerializerMethodField('rtng')
	ratings = serializers.SerializerMethodField('rtngs')
	images = serializers.SerializerMethodField('imgs')
	discounted_price = serializers.SerializerMethodField('discount')
	availability = serializers.SerializerMethodField('available')
	is_favorite = serializers.SerializerMethodField('get_is_favorite')

	class Meta:
		model = Product
		# fields = '__all__'
		exclude = ('timestamp', 'track', 'utrack', 'view', 'like', 'unlike', 'impression', 'admin')

	def get_is_favorite(self, obj):
		request = self.context['request']
		if str(request.user) == 'AnonymousUser':
			return False
		else:
			fav = Wishlist.objects.filter(product=obj, user=request.user, status='Active', cart=False)
			if fav.count() > 0:
				return True
		return False

	def rtng(self, obj):
		avg = Rating.objects.filter(product=obj.id)
		total = avg.aggregate(Sum('star'))['star__sum']
		if total == None:
			return {'total':0, 'average':0, '1':0, '2':0, '3':0, '4':0, '5':0}
		average = round(total/len(avg),2)
		one = avg.filter(star=1)
		two = avg.filter(star=2)
		three = avg.filter(star=3)
		four = avg.filter(star=4)
		five = avg.filter(star=5)
		return {'total':len(avg), 'average':average, '1':len(one), '2':len(two), '3':len(three), '4':len(four), '5':len(five)}

	def rtngs(self, obj):
		return RatingSerializer(Rating.objects.filter(product=obj.id), many=True, read_only=True).data

	def imgs(self, obj):
		return ProductImageSerializer(ProductImage.objects.filter(product=obj.id), many=True, read_only=True).data

	def available(self, obj):
		aval = Availability.objects.filter(product=obj.id).aggregate(Sum('quantity'))['quantity__sum']
		return aval

	def discount(self, obj):
		return obj.price - obj.discount

class ProductSerializer2(serializers.ModelSerializer):
	class Meta:
		model = Product
		# fields = '__all__'
		exclude = ('timestamp', 'track', 'utrack', 'view', 'like', 'unlike', 'impression', 'admin', 'manufacturer', 'category', 'tax')

class AvailabilitySerializer(serializers.ModelSerializer):
	sellers = UserSerializer(source = 'seller', read_only=True)
	products = ProductSerializer(source = 'product', read_only=True)
	class Meta:
		model = Availability
		# fields = '__all__'
		exclude = ('timestamp', 'track', 'utrack')

class DiscountSerializer(serializers.ModelSerializer):
	class Meta:
		model = Discount
		# fields = '__all__'
		exclude = ('timestamp', 'track', 'utrack')

class WishlistSerializer(serializers.ModelSerializer):
	# users = UserSerializer(source = 'user', read_only=True)
	products = ProductSerializer(source = 'product', read_only=True)

	class Meta:
		model = Wishlist
		# fields = '__all__'
		exclude = ('timestamp', 'track', 'utrack')

	def create(self, validated_data):
		product = validated_data.get('product', None)
		user = validated_data.get('user', None)
		quantity = validated_data.get('quantity', None)
		cart = validated_data.get('cart', None)
		current_wishlist = Wishlist.objects.filter(product = product, user = user, status='Active')
		product_obj = product
		if current_wishlist.exists():
			wishlist = current_wishlist.first()
			qty = wishlist.quantity+quantity
			if qty > product_obj.max_limit:
				qty = product_obj.max_limit
			if qty < product_obj.min_limit:
				qty = product_obj.min_limit
			wishlist.quantity = qty
			if cart:
				wishlist.cart = True
			else:
				wishlist.cart = False
			wishlist.save()
			return wishlist

		if cart and quantity:
			wishlist = Wishlist.objects.create(product= product, user = user, cart=cart, quantity=quantity)
		else:
			wishlist = Wishlist.objects.create(product= product, user = user, quantity=1)

		qty = wishlist.quantity
		if qty > product_obj.max_limit:
			qty = product_obj.max_limit
		if qty < product_obj.min_limit:
			qty = product_obj.min_limit
		wishlist.quantity = qty
		wishlist.save()
		return wishlist

class WishlistSerializer2(serializers.ModelSerializer):
	# products = ProductSerializer2(source = 'product', read_only=True)
	productid = serializers.SerializerMethodField('pid')
	product = serializers.SerializerMethodField('prdtc')
	image = serializers.SerializerMethodField('img')
	content = serializers.SerializerMethodField('get_content')
	
	class Meta:
		model = Wishlist
		# fields = '__all__'
		exclude = ('timestamp', 'track', 'utrack')

	def pid(self, obj):
		return obj.product.id

	def prdtc(self, obj):
		return obj.product.title

	def get_content(self, obj):
		return obj.product.content

	def img(self, obj):
		method = 'http'
		if self.context['request'].is_secure():
			method = 'https'
		return method+'://'+self.context['request'].get_host()+obj.product.image.url

class OrderSerializer(serializers.ModelSerializer):
	items = WishlistSerializer2(source = 'wishlist', many = True, read_only=True)
	# discounts = DiscountSerializer(source = 'discount', read_only=True)
	addresss = AddressSerializer(source = 'address', read_only=True)
	drivers = UserSerializer(source = 'driver', read_only=True)
	# sellers = UserSerializer(source = 'seller', read_only=True)
	shop = serializers.SerializerMethodField('shops')

	class Meta:
		model = Order
		# fields = '__all__'
		exclude = ('track', 'utrack', 'wishlist')

	def shops(self, obj):
		if obj.seller != None:
			return AddressSerializer(Address.objects.filter(user=obj.seller.id).last(), read_only=True).data
		else:
			return None

class DeliveryChargeSerializer(serializers.ModelSerializer):
	class Meta:
		model = DeliveryCharge
		exclude = ('timestamp', 'track', 'utrack')
 
class Over18Serializer(serializers.ModelSerializer):
	orders = OrderSerializer(source = 'order', read_only=True)
	class Meta:
		model = Over18
		exclude = ('timestamp', 'track', 'utrack')

class PaymentSerializer(serializers.ModelSerializer):
	orders = OrderSerializer(source = 'order', read_only=True)
	class Meta:
		model = Payment
		# fields = '__all__'
		exclude = ('timestamp', 'track', 'utrack')

class SupportSerializer(serializers.ModelSerializer):
	orders = OrderSerializer(source = 'order', read_only=True)
	users = UserSerializer(source = 'user', read_only=True)
	class Meta:
		model = Support
		# fields = '__all__'
		exclude = ('timestamp', 'track', 'utrack')

class RatingSerializer(serializers.ModelSerializer):
	users = UserSerializer(source = 'user', read_only=True)
	class Meta:
		model = Rating
		# fields = '__all__'
		exclude = ('timestamp', 'track', 'utrack')

		
class FaqSerializer(serializers.ModelSerializer):
	class Meta:
		model = Faq
		# fields = '__all__'
		exclude = ('timestamp', 'track', 'utrack')

		
class ContinentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Continent
		# fields = '__all__'
		exclude = ('timestamp', 'track', 'utrack')

class LanguageSerializer(serializers.ModelSerializer):
	class Meta:
		model = Language
		# fields = '__all__'
		exclude = ('timestamp', 'track', 'utrack')

class CountrySerializer(serializers.ModelSerializer):
	class Meta:
		model = Country
		# fields = '__all__'
		exclude = ('timestamp', 'track')

class StateSerializer(serializers.ModelSerializer):
	class Meta:
		model = State
		# fields = '__all__'
		exclude = ('timestamp', 'track', 'utrack')

class RegionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Region
		# fields = '__all__'
		exclude = ('timestamp', 'track', 'utrack')

class PageSerializer(serializers.ModelSerializer):
	class Meta:
		model = Page
		exclude = ('timestamp', 'track', 'utrack')

class PopupSerializer(serializers.ModelSerializer):
	class Meta:
		model = Popup
		exclude = ('timestamp', 'track', 'utrack')