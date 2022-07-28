from django.db import models
from django.contrib.auth.models import AbstractUser
from django_extensions.db.fields import AutoSlugField
from ckeditor_uploader.fields import RichTextUploadingField
from dropgrocer.settings import *
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from django.urls import reverse
import datetime
import requests
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from django.db import transaction
from geolocation.models import *
from geolocation.models import Country


gender = (('Male', 'Male'),('Female', 'Female'),('Other', 'Other'),)
source = (('Website', 'Website'),('Android', 'Android'),('iOS', 'iOS'),('AMP', 'AMP'),('PWA', 'PWA'),('Desktop', 'Desktop'))
status=[('Active','Active'),('Inactive','Inactive'),('Delete','Delete'),]
ostatus=[('PENDING','PENDING'),('CONFIRM','CONFIRM'),('REJECT','REJECT'),('IN TRANSIT','IN TRANSIT'),('DELIVERED','DELIVERED')]
vtype = (('Bike', 'Bike'), ('Car', 'Car'),)
method = (('Online', 'Online'), ('COD', 'COD'),)
sale = (('Yes', 'Yes'), ('No', 'No'),)
wtype = (('kg', 'kg'), ('gm', 'gm'), ('ltr', 'ltr'), ('ml', 'ml'),)
role = (('Admin', 'Admin'), ('Seller', 'Seller'), ('Driver', 'Driver'), ('Customer', 'Customer'),)
paymode = (('PENDING', 'PENDING'),('PAYPAL', 'PAYPAL'),('COD', 'COD'),)
social = (('Facebook', 'Facebook'), ('Gmail', 'Gmail'),('Apple','Apple'),)



class VehicleType(models.Model):
	title = models.CharField(max_length = 160)
	timestamp = models.DateTimeField(auto_now_add = True, editable = False)
	utimestamp = models.DateTimeField(auto_now = True, editable = False)
	track = models.TextField(blank = True, editable = False)
	utrack = models.TextField(blank = True, editable = False)
	status = models.CharField(max_length = 10, choices = status, default = 'Active')

	def __str__(self):
		return self.title

	class Meta:
		verbose_name_plural = _('Vehicle Types')


class User(AbstractUser):
	country = models.ForeignKey(Country, on_delete = models.PROTECT, null = True, blank = True)
	vtype = models.ForeignKey(VehicleType, verbose_name="vehicle type", on_delete=models.PROTECT, blank=True, null=True)
	parent = models.ForeignKey("self", verbose_name="parent", on_delete=models.PROTECT, blank=True, null=True)
	role = models.CharField(max_length = 10, choices = role, default = 'Customer')
	mobile = models.CharField(max_length=12)
	email = models.EmailField(blank = False, max_length = 100)
	gender = models.CharField(max_length=6, choices=gender, default='Male')
	dob = models.DateField(null=True, blank=True)
	image = models.ImageField(upload_to = 'user/', blank=True, null=True, default="default/logo.png")
	about = models.TextField(blank=True)
	store = models.CharField(max_length =100, blank = True, null = True)
	facebook = models.BooleanField(default = False)
	twitter = models.BooleanField(default = False)
	instagram = models.BooleanField(default = False)
	socialid = models.TextField(null = True, blank = True)
	online = models.BooleanField(default=True)
	verified = models.BooleanField(default=False)
	multilogin = models.BooleanField(default=False)
	multilanguage = models.CharField(max_length = 10, choices = LANGUAGES, default =LANGUAGE_CODE)
	latitude = models.FloatField(blank = True, null = True)
	longitute = models.FloatField(blank = True, null = True)
	source = models.CharField(max_length=10, choices=source, default='Website')
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True)
	utrack = models.TextField(blank=True)
	socialtype = models.CharField(max_length = 10, choices = social, default = 'Facebook')
	status = models.CharField(max_length=10, choices=status, default='Active')

class Customer(User):
	class Meta:
		proxy = True

class Seller(User):
	class Meta:
		proxy = True


	def save(self, *args, **kwargs):
		self.is_staff = True
		self.is_superuser = True
		
		super().save(*args, **kwargs)

class Driver(User):
	class Meta:
		proxy = True

	def clean(self, *args, **kwargs):
		if self.role == 'Driver':
			if self.dob:
				if (datetime.datetime.now().date() - self.dob).days < 6570:
					raise ValidationError({'dob':_('Age must be 18+')})
		super().clean(*args, **kwargs)

	# def save(self, *args, **kwargs):
	# 	age = (datetime.now() - self.dob).days/365
	# 	print(date.today())
	# 	if age < 18:
	# 		raise forms.ValidationError('Must be at least 18 years old to register')
	# 	super().save(*args, **kwargs)

class VehicleDocType(models.Model):
	vtype = models.ForeignKey(VehicleType, verbose_name = 'Vehicle Type' ,on_delete = models.PROTECT, null = True, blank = True)
	title = models.CharField(max_length = 160)
	timestamp = models.DateTimeField(auto_now_add = True, editable = False)
	utimestamp = models.DateTimeField(auto_now = True, editable = False)
	track = models.TextField(blank = True, editable = False)
	utrack = models.TextField(blank = True, editable = False)
	status = models.CharField(max_length = 10, choices = status, default = 'Active')

	def __str__(self):
		return self.title

	class Meta:
		verbose_name_plural = _('Vehicle Document Type')


class Address(models.Model):
	user = models.ForeignKey(User, on_delete = models.PROTECT, verbose_name = 'User')
	title = models.CharField(_('title'), max_length = 100)
	country = models.ForeignKey(Country, on_delete = models.PROTECT, verbose_name = 'Country')
	state = models.ForeignKey(State, on_delete = models.PROTECT, verbose_name = 'State')
	city = models.CharField(_('city'), max_length = 50)
	address = models.TextField(_('address'),)
	postcode = models.CharField(_('postcode'), max_length = 6)
	latitude = models.FloatField(blank = True, null = True)
	longitute = models.FloatField(blank = True, null = True)
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.title

	class Meta:
		verbose_name_plural = _('Address')

class DocType(models.Model):
	title = models.CharField(max_length = 160)
	timestamp = models.DateTimeField(auto_now_add = True, editable = False)
	utimestamp = models.DateTimeField(auto_now = True, editable = False)
	track = models.TextField(blank = True, editable = False)
	utrack = models.TextField(blank = True, editable = False)
	status = models.CharField(max_length = 10, choices = status, default = 'Active')

	def __str__(self):
		return self.title

	class Meta:
		verbose_name_plural = _('Document Types')

class Document(models.Model):
	user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Driver")
	doctype = models.ForeignKey(DocType, verbose_name="Document Type", on_delete=models.PROTECT)
	image = models.ImageField(_('image'), upload_to = 'document/')
	timestamp = models.DateTimeField(auto_now_add = True, editable = False)
	utimestamp = models.DateTimeField(auto_now = True, editable = False)
	track = models.TextField(blank = True, editable = False)
	utrack = models.TextField(blank = True, editable = False)
	status = models.CharField(max_length = 10, choices = status, default = 'Active')

	def __str__(self):
		return str(self.doctype)

	class Meta:
		verbose_name_plural = _('Document')
		unique_together = ('user', 'doctype',)

class Vehicle(models.Model):
	vtype = models.ForeignKey(VehicleType, verbose_name="Vehicle Type", on_delete=models.PROTECT, blank=True, null=True)
	user = models.ForeignKey(User, on_delete = models.PROTECT, verbose_name = 'User')
	number = models.CharField(_('number'), max_length = 25)
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.number

	class Meta:
		verbose_name_plural = _('Vehicle')

class VehicleDocument(models.Model):
	vehicle = models.ForeignKey(Vehicle, on_delete = models.PROTECT, blank = True, null = True)
	image = models.ImageField(upload_to = 'vehicle/document/')
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.vehicle.number

	class Meta:
		verbose_name_plural = _('Vehicle Document')

class Banner(models.Model):
	title = models.CharField(_('title'), max_length = 100)
	content = RichTextUploadingField(_('content'),)
	image = models.ImageField(_('image'), upload_to = 'banner/', help_text = '920 x 450 pixels')
	web = models.BooleanField(_('web'), default = False)
	mobile = models.BooleanField(_('mobile'), default = False)
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.title

	class Meta:
		verbose_name_plural = _('Banner')

class Category(models.Model):
	parent = models.ForeignKey('self', on_delete = models.PROTECT, null = True, blank = True, related_name = 'subcategory')
	title = models.CharField(_('title'), max_length = 160)
	slug = AutoSlugField(populate_from = 'title', max_length = 160, editable = True)
	content = RichTextUploadingField(_('content'), )
	image = models.ImageField(_('image'), upload_to = 'category/')
	# icon = models.ImageField(upload_to = 'category/icon/', help_text = 'icon size = 182 X 105 pixel')
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		display = self.title
		# if self.parent != None:
		# 	display = str(self.parent)+" => "+str(self.title)
		return display

	class Meta:
		verbose_name_plural = _('Categories')

	def subcategory(self):
		return Category.objects.filter(parent = self, status = 'Active')

class Manufacturer(models.Model):
	title = models.CharField(max_length = 160)
	slug = AutoSlugField(populate_from = 'title', editable = True, max_length = 160)
	content = RichTextUploadingField()
	estd = models.DateField()
	logo = models.ImageField(upload_to = 'manufacturer/', help_text = 'logo size 200 x 200')
	email = models.EmailField(max_length = 100)
	mobile = models.CharField(max_length = 12)
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.title

class Tax(models.Model):
	title = models.CharField(max_length = 50)
	code = models.PositiveIntegerField(default = 0)
	percentage = models.FloatField(default = 0)
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.title

	class Meta:
		verbose_name_plural = _('Taxes')

class Product(models.Model):
	admin = models.ForeignKey(User, on_delete = models.PROTECT)
	category = models.ManyToManyField(Category, verbose_name = 'category')
	manufacturer = models.ForeignKey(Manufacturer, on_delete = models.PROTECT, null = True, blank = True)
	tax = models.ForeignKey(Tax, on_delete = models.PROTECT, null = True, blank = True)
	title = models.CharField(_('title'), max_length = 160)
	slug = AutoSlugField(populate_from = 'title', editable = True, max_length = 260)
	content = RichTextUploadingField(_('content'), )
	short_description = models.TextField()
	image = models.ImageField(_('image'), upload_to = 'product/')
	# image = models.ImageField(_('image'), upload_to = 'product/', help_text = 'image = 500 x 500 pixel')
	# ptype = models.CharField(max_length = 160, verbose_name = 'Product Type')
	fsale = models.CharField(max_length = 10, choices = sale, default = 'No', verbose_name = 'Flash Sale')
	gross_price = models.FloatField(default = 0)
	price = models.FloatField(default = 0)
	discount = models.FloatField(default = 0, help_text="Discount must be less then product price")
	min_limit = models.PositiveIntegerField(default = 1, verbose_name = 'Minimum Order Limit')
	max_limit = models.PositiveIntegerField(default = 10, blank = True, verbose_name = 'Maximum Order Limit')
	weight = models.FloatField(default = 0)
	weight_type = models.CharField(max_length = 10, choices = wtype, default = 'gm')
	seasonal = models.BooleanField(default=False)
	adult = models.BooleanField(default=False)
	view = models.PositiveIntegerField(_('view'), default = 0)
	like = models.PositiveIntegerField(_('like'), default = 0)
	unlike = models.PositiveIntegerField(_('unlike'), default = 0)
	impression = models.PositiveIntegerField(_('impression'), default = 0)
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.title

	class Meta:
		verbose_name_plural = _('Product')

	def get_absolute_url(self):
		return reverse('home:product', kwargs={'slug':str(self.slug)})

	def avg_rating(self):
		ratings = Rating.objects.filter(product = self.id)
		total_star = ratings.aggregate(Sum('star'))['star__sum']
		if total_star == None:
			return 0
		else:
			return round(total_star/len(ratings),2)

	def stock_availbility(self):
		stock = Availability.objects.filter(product__id = self.id).aggregate(Sum('quantity'))['quantity__sum']
		if stock and stock >= self.min_limit:
			return True
		return False

	def stock_num(self):
		stock = Availability.objects.filter(product__id = self.id).aggregate(Sum('quantity'))['quantity__sum']
		return stock

class ProductImage(models.Model):
	product = models.ForeignKey(Product, on_delete = models.PROTECT, related_name = 'productimage')
	image = models.ImageField(upload_to = 'product_image/')
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.product.title

class Availability(models.Model):
	product = models.ForeignKey(Product, on_delete = models.PROTECT)
	seller = models.ForeignKey(User, on_delete = models.PROTECT)
	quantity = models.PositiveIntegerField(default = 0)
	sales = models.PositiveIntegerField(default = 0)
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.product.title+' >= '+ self.seller.username

	class Meta:
		verbose_name_plural = _('Availabilities')
		unique_together = ("product", "seller")


class Discount(models.Model):
	title = models.CharField(_('title'), max_length = 100)
	code = models.CharField(_('code'), max_length = 100)
	amount = models.FloatField(_('amount'), help_text = 'value in percentage')
	valid = models.DateField(_('valid'), )
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.title

	class Meta:
		verbose_name_plural = _('Discount')

class DeliveryCharge(models.Model):
	title = models.CharField(max_length = 160)
	amount = models.PositiveIntegerField(default = 0)
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.title

	class Meta:
		verbose_name_plural = _('Delivery Charge')

class Wishlist(models.Model):
	product = models.ForeignKey(Product, on_delete = models.PROTECT, verbose_name = 'product', related_name = 'wproduct')
	user = models.ForeignKey(User, on_delete = models.PROTECT, verbose_name = 'user')
	quantity = models.PositiveIntegerField(_('quantity'), default = 0)
	price = models.FloatField(_('price'), default = 0)
	total = models.FloatField(_('total'), default = 0.0)
	cart = models.BooleanField(default = False)
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.product.title+' >= '+self.user.username

	class Meta:
		verbose_name_plural = _('Wishlist')

	def save(self, *args, **kwargs):
		self.price = self.product.price
		self.total = round(float(self.quantity) * self.price,2)
		super().save(*args, **kwargs)

class Order(models.Model):
	discount = models.ForeignKey(Discount, on_delete = models.PROTECT, blank = True, null = True, related_name = 'orderd')
	wishlist = models.ManyToManyField(Wishlist, verbose_name = 'wishlist')
	address = models.ForeignKey(Address, on_delete = models.PROTECT, verbose_name = 'address', related_name = 'ordera')
	driver = models.ForeignKey(User, on_delete = models.PROTECT, null = True, blank = True, related_name = 'driver')
	seller = models.ForeignKey(User, on_delete = models.PROTECT, null = True, blank = True, related_name = 'seller')
	price = models.FloatField(default = 0)
	total = models.FloatField(_('total'), default = 0)
	date = models.DateTimeField(_('date'), blank = True, null = True, help_text = 'Select your time slot')
	confirm = models.BooleanField(default = False)
	adult = models.BooleanField(default = False)
	driverconfirm = models.BooleanField(default = False)
	note = models.TextField(_('note'), blank = True)
	paymode = models.CharField(max_length = 15, choices = paymode, default = 'PENDING')
	latitude = models.FloatField(blank = True, null = True)
	longitute = models.FloatField(blank = True, null = True)
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	status = models.CharField(max_length=10, choices=ostatus, default='PENDING')

	def __str__(self):
		return self.address.title

	# def get_product(self):
	# 	return ",".join([str(p) for p in self.wishlist.product.title])
	# get_product.short_description='Product'

	class Meta:
		verbose_name_plural = _('Order')

	def clean(self, *args, **kwargs):
		if self.driver and self.status:
			if self.status == 'PENDING':
				raise ValidationError({'status':_('Status cannot be PENDING if driver assigned.')})
		if self.seller:
			for wl in self.wishlist.all():
				availability = Availability.objects.filter(product=wl.product, seller=self.seller).first()
				if not availability:
					raise ValidationError({'seller':_(wl.product.title+' is not avaiable for selected seller.')})
				else:
					if wl.quantity < availability.quantity:
						raise ValidationError({'seller':_(wl.product.title+' - required quantity is not avaiable for selected seller.')})

		super().clean(*args, **kwargs)

	def save(self, *args, **kwargs):
		deliverych = DeliveryCharge.objects.filter(status = 'Active').values('amount').last()
		if self.discount:
			self.total = self.price - self.discount.amount
		else:
			self.total = self.price - 0

		if deliverych != None:
			self.total = self.total+deliverych['amount']

		if self.seller:
			if self.id != None and self.seller.id !=None:
				try:
					address = Address.objects.filter(user = self.seller.id)
					# print(address, 'seller address')
					order =Order.objects.get(id =self.id)
					if order.seller:
						if order.seller.id != self.seller.id and len(self.address) >0:
							self.latitude = self.address.latitude
							self.longitute = self.address.longitute
				except: pass
		if self.seller:
			if self.seller and self.confirm == False:
			# if 'CONFIRM' in self.status and self.seller.id and self.confirm == False:
				try:
					with transaction.atomic():
						wishlist = self.wishlist.all()
						for wish in wishlist:
							availbl = Availability.objects.filter(product = wish.product.id, seller = self.seller.id).last()
							availbl.quantity = availbl.quantity - wish.quantity
							availbl.sales = availbl.sales + wish.quantity
							availbl.save()
				except Exception as e:
					print(e)
					pass
		super().save(*args, **kwargs)

class Dispatcher(Order):
	class Meta:
		proxy = True

from geolocation.models import *
class Over18(models.Model):
	order = models.ForeignKey(Order, on_delete = models.PROTECT, verbose_name = 'order')
	country = models.ForeignKey(Country, on_delete = models.PROTECT, verbose_name = 'country')
	dob = models.DateField()
	document = models.ImageField(upload_to='adult/')
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return str(self.order)

	class Meta:
		verbose_name_plural = _('Over18')

class Payment(models.Model):
	order = models.ForeignKey(Order, on_delete = models.PROTECT, verbose_name = 'order')
	method = models.CharField(_('method'), max_length = 10, choices = method, default = 'Online')
	transaction = models.CharField(max_length=50)
	email = models.EmailField(max_length=50)
	name = models.CharField(max_length=20)
	amount = models.FloatField(_('amount'), )
	payed = models.FloatField(_('payed'), )
	currency = models.CharField(max_length=20)
	rawdata = models.TextField(_('rawdata'), blank = True, null = True, editable=False)
	source = models.CharField(max_length=10, choices=source, default='Website')
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	# def __str__(self):
	# 	return self.order.wishlist.product.title

	class Meta:
		verbose_name_plural = _('Payment')

	def save(self, *args, **kwargs):
		order = Order.objects.filter(id = self.order.id).update(paymode = 'PAYPAL')
		# print(order)
		super().save(*args, **kwargs)


class Support(models.Model):
	order = models.ForeignKey(Order, on_delete = models.PROTECT, related_name = 'supports', verbose_name = 'order')
	user = models.ForeignKey(User, on_delete = models.PROTECT, verbose_name = 'users')
	parent = models.ForeignKey('self', on_delete = models.CASCADE, related_name = 'replies', blank= True, null=True)
	title = models.CharField(_('title'), max_length = 100)
	content = RichTextUploadingField(_('content'), )
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.title

	class Meta:
		verbose_name_plural = _('Support')

class Rating(models.Model):
	product = models.ForeignKey(Product, on_delete = models.PROTECT, null =True, blank = True, related_name = 'rating', verbose_name = 'product')
	user = models.ForeignKey(User, on_delete = models.PROTECT, verbose_name = 'user')
	star = models.PositiveIntegerField(_('star'), default = 0)
	review = models.TextField(_('review'), blank = True)
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.user.username

	class Meta:
		verbose_name_plural = _('Rating')
		unique_together = ("product", "user")
		

class Faq(models.Model):
	title = models.CharField(_('title'), max_length = 160)
	slug = AutoSlugField(populate_from = 'title', editable = True, max_length = 160)
	content = RichTextUploadingField(_('content'), )
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.title

	class Meta:
		verbose_name_plural = _('Faq')

class Subscribe(models.Model):
	email=models.EmailField(max_length=50)
	url=models.URLField(max_length=100, blank=True)
	timestamp=models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp=models.DateTimeField(auto_now=True, editable=False)
	track=models.TextField(blank=True)
	utrack=models.TextField(blank=True)
	status=models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.email

	class Meta:
		verbose_name_plural = _('Subscribe')

class Page(models.Model):
	title = models.CharField(_('title'), max_length = 160)
	slug = AutoSlugField(populate_from = 'title', editable = True, max_length = 160)
	content = RichTextUploadingField(_('content'), )
	keyword = models.CharField(max_length=160)
	meta_title = models.CharField(max_length = 160)
	meta_description = models.TextField()
	timestamp=models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp=models.DateTimeField(auto_now=True, editable=False)
	track=models.TextField(blank=True)
	utrack=models.TextField(blank=True)
	status=models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.title

	class Meta:
		verbose_name_plural = _('Page')

class Popup(models.Model):
	title = models.CharField(max_length = 160)
	image = models.ImageField(upload_to = 'popup/', help_text = '500 x300 pixels')
	timestamp = models.DateTimeField(auto_now_add = True, editable = False)
	utimestamp = models.DateTimeField(auto_now = True, editable = False)
	track = models.TextField(blank = True)
	utrack = models.TextField(blank = True)
	status = models.CharField(max_length = 10, choices = status, default = 'Active')

	def __str__(self):
		return self.title

@receiver(m2m_changed, sender = Order.wishlist.through)
def wishlist(sender, instance, action, **kwargs):
	totalwish = instance.wishlist.all()
	pricess = 0
	for wishtol in totalwish:
		pricess += wishtol.total
	instance.price = pricess
	if action == 'post_add':
		try:
			sellerid = instance.seller.id
		except:
			pass
		wishpro = instance.wishlist.all()
		for wishid in wishpro:
			wishid.status ='Inactive'
			wishid.save()
			try:
				ava = Availability.objects.get(product = wishid.product.id, seller = sellerid)
				ava.quantity = ava.quantity - wishid.quantity
				ava.sales = ava.sales + wishid.quantity
				ava.save()
			except:
				pass
	instance.save()

@receiver(post_save, sender=Order)
def order_update(sender, instance=None, created=False, **kwargs):
	user = instance.address.user
	wish = Wishlist.objects.filter(user=user)
	order = Order.objects.get(id=instance.id)
	# for wl in wish:
	# 	print(wl)
		# order.wishlist.add(wl)
	# print("Hello", user, wish, order)
	# result = requests.get('http://127.0.0.1:8000/wishorder/'+str(instance.address.user.id))
	# result = requests.get('http://dropgrocer.mydevpartner.website/wishorder/'+str(instance.address.user.id))
	# print(result)
	if created:
		# print(instance)
		# send_email()
		print("Send Email to Signup User with Login Details")
	# instance.save()

# @receiver(post_save, sender=User)
# def create_auth_token(sender, instance=None, created=False, **kwargs):
# 	if created:
# 		Token.objects.create(user=instance)