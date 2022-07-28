from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from .models import *
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from datetime import datetime
from django.http import HttpResponse
import csv
from django.forms import Textarea, TextInput
from .forms import CustomerAdminForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class UserCustomAdmin(UserAdmin):
	ordering = ('-id',)
	list_display = ('id','username', 'multilanguage', 'role', 'email', 'mobile', 'first_name', 'last_name', 'verified',)
	search_fields = ('username', 'email', 'mobile', 'first_name', 'last_name', 'gender', 'vtype__title')
	list_filter = ()
	autocomplete_fields = ('country',)

	add_fieldsets = (
		(None, {
			'classes': ('wide', 'extrapretty'),
			'fields': ('first_name', 'last_name', 'email', 'mobile', 'username', 'role', 'password1', 'password2' ),
		}),
	)
	fieldsets = [
		(None, {'fields': ('email', 'username', 'role', 'mobile', 'first_name', 'last_name', 'password',)}),
		('Personal info', {'fields': ('image', 'gender', 'dob', 'about', 'country',)}),
		('Social Detail', {'classes': ('collapse', ), 'fields': ('facebook','twitter','source')}),
		
		('Important dates', {'classes': ('collapse', ), 'fields': ('last_login','date_joined')}),
		('Permissions', {'classes': ('collapse', ), 'fields': ('is_active','is_staff','is_superuser','groups','user_permissions',)}), ]

	def has_add_permission(self,request):
		# if request.user.is_superuser and 'Permissions' not in self.fieldsets:
		# 	self.fieldsets.append(('Permissions', {'classes': ('collapse', ), 'fields': ('is_active','is_staff','is_superuser','groups','user_permissions',)}))
		if request.user.is_superuser and 'Verification' != self.fieldsets[-1][0]:
			self.fieldsets.append(('Verification', {'fields': ('verified',)}))
		return True

	def has_change_permission(self, request, obj=None):
		if request.user.role == 'Admin':
			return True
		else:
			return False

	# def work(self, obj):
	# 	return format_html('<a href="/stroops/stroop/work/?q=%s" >Work</a>'%(obj.username))

	def has_delete_permission(self, request, obj=None):
		if request.user.role == 'Admin':
			return True
		else:
			return False

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		if request.user.role == 'Driver':
			return qs.filter(role = 'Driver')
		elif request.user.role == 'Seller':
			return qs.filter(role = 'Seller')
		elif request.user.role == 'Customer':
			return qs.filter(role = 'Customer')
		elif request.user.role == 'Admin':
			return qs.filter(role = 'Admin')
		return qs

class CustomerAdmin(UserAdmin):
	# form = CustomerAdminForm
	list_display = ('username', 'email', 'mobile', 'first_name', 'last_name',)
	search_fields = ('username', 'email', 'mobile', 'first_name', 'last_name', 'gender')
	
	add_fieldsets = (
		(None, {
			'classes': ('wide', 'extrapretty'),
			'fields': ('first_name', 'last_name', 'email', 'mobile', 'username', 'role', 'password1', 'password2' ),
		}),
	)

	fieldsets = [
		(None, {'fields': ('email', 'username', 'role', 'mobile', 'first_name', 'last_name')}),
		('Personal info', {'fields': ('image', 'gender', 'dob', 'about',)}),
		('Social Detail', {'classes': ('collapse', ), 'fields': ('facebook','twitter','source')}),
		
		('Important dates', {'classes': ('collapse', ), 'fields': ('last_login','date_joined')}),]

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		# print(request.user.auth_token)
		return qs.filter(role = 'Customer')

	def has_change_permission(self, request, obj=None):
		if request.user.role == 'Admin':
			return True
		else:
			return False

	def has_delete_permission(self, request, obj=None):
		if request.user.role == 'Admin':
			return True
		else:
			return False

	def has_add_permission(self,request):
		if request.user.role == 'Admin':
			return True
		else:
			return False


class AddressInLine(admin.StackedInline):
	model = Address
	extra = 1
	max_num = 1
	min_num = 1
	fields = ('title', 'country', 'state', 'city', 'postcode', 'address')
	verbose_name = _("Shop Address")
	verbose_name_plural = _("Shop Address")
	# autocomplete_fields = ['product',]
	# classes = ['collapse', 'extrapretty']

class SellerAdmin(UserAdmin):
	list_display = ('id','username', 'email', 'mobile', 'first_name', 'last_name',)
	search_fields = ('username', 'email', 'mobile', 'first_name', 'last_name', 'gender')
	inlines = [AddressInLine]

	add_fieldsets = (
		(None, {
			'classes': ('wide', 'extrapretty'),
			'fields': ('first_name', 'last_name', 'email', 'mobile', 'username', 'role', 'password1', 'password2' ),
		}),
	)

	fieldsets = [
		(None, {'fields': ('first_name', 'last_name', 'username', 'email', 'mobile', 'role')}),
		('Personal info', {'fields': ('image', 'gender', 'dob', 'about',)}),
		# ('Social Detail', {'classes': ('collapse', ), 'fields': ('facebook','twitter','source')}),
		('Important dates', {'classes': ('collapse', ), 'fields': ('last_login','date_joined')}),]


	def has_delete_permission(self, request, obj=None):
		return False

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		qs = qs.filter(role='Seller')
		if request.user.role == 'Seller':
			qs = qs.filter(id=request.user.id)
		return qs

	def has_change_permission(self, request, obj=None):
		if request.user.role == 'Admin' or request.user.role == 'Seller':
			return True
		else:
			return False

	def has_delete_permission(self, request, obj=None):
		if request.user.role == 'Admin':
			return True
		else:
			return False

	def has_add_permission(self,request):
		if request.user.role == 'Admin':
			return True
		else:
			return False

	def save_model(self, request, obj, form, change):
		super().save_model(request, obj, form, change)


class DocumentInLine(admin.TabularInline):
	model = Document
	extra = 0
	# max_num = 1
	# min_num = 1
	fields = ('doctype', 'image', 'status')
	verbose_name = _("Documents")
	verbose_name_plural = _("Documents")
	# autocomplete_fields = ['product',]
	# classes = ['collapse', 'extrapretty']

class DriverAdmin(UserAdmin):
	list_display = ('username', 'email', 'mobile', 'first_name', 'last_name',)
	search_fields = ('username', 'email', 'mobile', 'first_name', 'last_name', 'gender')

	add_fieldsets = (
		(None, {
			'classes': ('wide', 'extrapretty'),
			'fields': ('first_name', 'last_name', 'email', 'mobile', 'username', 'role', 'password1', 'password2' ),
		}),
	)

	inlines = [DocumentInLine,]

	fieldsets = [
		(None, {'fields': ('first_name', 'last_name', 'username', 'email', 'mobile', 'role')}),
		('Personal info', {'fields': ('image', 'gender', 'dob', 'about', 'latitude', 'longitute')}),
		('Social Detail', {'classes': ('collapse', ), 'fields': ('facebook','twitter','source')}),
		
		('Important dates', {'classes': ('collapse', ), 'fields': ('last_login','date_joined')}),]


	def has_delete_permission(self, request, obj=None):
		return True

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		return qs.filter(role='Driver')

	def has_change_permission(self, request, obj=None):
		if request.user.role == 'Admin' or request.user.role == 'Seller':
			return True
		else:
			return False

	def has_delete_permission(self, request, obj=None):
		if request.user.role == 'Admin' or request.user.role == 'Seller':
			return True
		else:
			return False

	def has_add_permission(self,request):
		if request.user.role == 'Admin' or request.user.role == 'Seller':
			return True
		else:
			return False

class AddressAdmin(admin.ModelAdmin):
	list_display = ('id','user', 'title', 'country', 'state', 'city', 'postcode', 'address', 'timestamp_and_utimestamp', 'status', 'actionbutton',)
	search_fields = ('title', 'city', 'postcode', 'country__name', 'state__title')
	# autocomplete_fields = ('user', 'country', 'state',)

	fieldsets=(        
	   (None,{"fields": (('user'),('title'),('address','city'),('state', 'country'),('postcode'),('latitude', 'longitute')),}), 
	)

	formfield_overrides = {
		# models.CharField: {'widget': TextInput(attrs={'size':'20'})},
		models.TextField: {'widget': Textarea(attrs={'rows':5, 'cols':40})},
	}

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="admin:%s/%s/%s" class="editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		if request.user.role == 'Admin':
			return qs
		return qs.filter(user=request.user)

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = 'Added/Last Modified'

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['user', 'title', 'country', 'state', 'city', 'address', 'postcode', 'latitude', 'longitute', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")

class VehicleAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'number', 'timestamp_and_utimestamp', 'status', 'actionbutton',)
	search_fields = ('number',)
	autocomplete_fields = ('user',)

	fieldsets=(        
	   (None,{"fields": (('user'),('vtype', 'number'),),}), 
	)

	# def licence_img(self, obj):
	# 	# used in the admin site model as a "thumbnail"
	# 	if obj.licence:
	# 		return mark_safe('<img src="%s" width="40px" height="42px" />' % obj.licence.url)
	# 	else:
	# 		return 'No Image Found'
	# licence_img.short_description = 'Licence'

	# def rc_img(self, obj):
	# 	# used in the admin site model as a "thumbnail"
	# 	if obj.rc:
	# 		return mark_safe('<img src="%s" width="40px" height="42px" />' % obj.rc.url)
	# 	else:
	# 		return 'No Image Found'
	# rc_img.short_description = 'RC'

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="admin:%s/%s/%s" class="editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		if request.user.role == 'Admin':
			return qs
		return qs.filter(user=request.user)

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == 'user':
			kwargs['queryset'] = User.objects.filter(role='Seller')
		return super(VehicleAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['user', 'vtype', 'licence', 'rc', 'number', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")



class CategoryAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'categoryimg','timestamp_and_utimestamp', 'status','actionbutton',)
	search_fields = ('title',)
	readonly_fields = ('categoryimg',)
	autocomplete_fields = ('parent',)
	# list_per_page=2

	fieldsets=(        
	   (None,{"fields": (('parent'), ('title','slug'),('content'),('image'),('status')),}), 
	)

	formfield_overrides = {
		models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':25})},
	}

	def product_count(self, obj):
		return obj.product_set.count()
	product_count.short_description = _('Product')

	def categoryimg(self, obj):
		if obj.image:
			return mark_safe('<img src="%s" width="40px" height="42px" />' % obj.image.url)
	categoryimg.short_description = _('Image')

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="%s/change/" class="editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def has_change_permission(self, request, obj=None):
		if request.user.role == 'Admin':
			return True
		else:
			return False

	def has_delete_permission(self, request, obj=None):
		if request.user.role == 'Admin':
			return True
		else:
			return False

	def has_add_permission(self,request):
		# if request.user.is_superuser and 'Verification' != self.fieldsets[-1][0]:
		# 	self.fieldsets.append(('Verification', {'fields': ('verified',)}))
		if request.user.role == 'Admin':
			return True
		else:
			return False

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['title', 'slug', 'content', 'image', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")

class ProductImageInLine(admin.TabularInline):
	model = ProductImage
	extra = 0
	fields = ('product', 'image',)
	autocomplete_fields = ['product',]
	classes = ['collapse', 'extrapretty']

	def get_readonly_fields(self, request, obj=None):
		readonly_fields = super().get_readonly_fields(request, obj)
		if obj and request.user.role == 'Seller':
			return  ['product', 'image']
		return readonly_fields

	def has_change_permission(self, request, obj=None):
		if request.user.role == 'Admin' or request.user.role == 'Seller':
			return True
		else:
			return False

	def has_delete_permission(self, request, obj=None):
		if request.user.role == 'Admin' or request.user.role == 'Seller':
			return True
		else:
			return False

	def has_add_permission(self,request, obj=None):
		if request.user.role == 'Admin' or request.user.role == 'Seller':
			return True
		else:
			return False

class AvailabilityInLine(admin.TabularInline):
	model = Availability
	extra = 0
	fields = ('quantity', 'sales', 'seller')
	autocomplete_fields = ['product',]
	classes = ['collapse', 'extrapretty']

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		if request.user.role == 'Admin':
			return qs
		return qs.filter(seller=request.user)

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == 'seller':
			if request.user.role == 'Seller':
				kwargs['queryset'] = User.objects.filter(id=request.user.id)
			else:
				kwargs['queryset'] = User.objects.filter(role='Seller')
		return super(AvailabilityInLine, self).formfield_for_foreignkey(db_field, request, **kwargs)

class ProductAdmin(admin.ModelAdmin):
	model = Product
	list_display = ('id', 'title', 'aquantity_total', 'sales_total', 'productimg', 'timestamp_and_utimestamp', 'status', 'actionbutton',)
	search_fields = ('title',)
	autocomplete_fields = ('manufacturer', 'tax',)
	filter_horizontal = ('category',)
	readonly_fields = ['view', 'like', 'unlike', 'impression',]
	inlines = [ProductImageInLine, AvailabilityInLine]

	fieldsets=(        
	   (None,{"fields": (('admin'), ('category'),('manufacturer', 'tax'),('title','slug'),('content'),('image', 'short_description'), ('fsale', 'adult'),('min_limit', 'max_limit'), ('gross_price','price', 'discount'),('weight_type', 'weight', 'status'), ),}), 
	)

	formfield_overrides = {
		# models.CharField: {'widget': TextInput(attrs={'size':'20'})},
		models.TextField: {'widget': Textarea(attrs={'rows':8, 'cols':40})},
	}

	def formfield_for_choice_field(self, db_field, request, **kwargs):
		if request.user.role == 'Seller':
			if db_field.name == 'status':
				kwargs['choices'] = (('Inactive', 'Inactive'),)
			
		return super().formfield_for_choice_field(db_field, request, **kwargs)

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if request.user.role == 'Seller':
			if db_field.name == 'admin':
				kwargs['queryset'] = User.objects.filter(id=request.user.id)
		return super().formfield_for_foreignkey(db_field, request, **kwargs)
	
	def productimg(self, obj):
		if obj.image:
			return mark_safe('<img src="%s" width="40px" height="45px">' % obj.image.url)
	productimg.short_description = _('Image')

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s" class="editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def get_readonly_fields(self, request, obj=None):
		readonly_fields = super().get_readonly_fields(request, obj)
		if obj and request.user.role == 'Seller':
			return readonly_fields + ['admin', 'category', 'manufacturer', 'tax', 'title', 'slug', 'content', 'short_description', 'image', 'fsale', 'gross_price', 'price', 'discount', 'min_limit', 'max_limit', 'weight', 'weight_type', 'seasonal', 'adult', 'status']
		return readonly_fields

	def has_change_permission(self, request, obj=None):
		if request.user.role == 'Admin' or request.user.role == 'Seller':
			return True
		else:
			return False

	def has_delete_permission(self, request, obj=None):
		if request.user.role == 'Admin':
			return True
		else:
			return False

	def has_add_permission(self,request):
		if request.user.role == 'Admin' or request.user.role == 'Seller':
			return True
		else:
			return False

	def aquantity_total(self, obj):
		grand_total = 0
		ente = Availability.objects.filter(product= obj.id)
		for enter in ente:
			grand_total += enter.quantity
		return grand_total
	aquantity_total.short_description = _('available stock')

	def sales_total(self, obj):
		grand_total = 0
		ente = Availability.objects.filter(product= obj.id)
		for enter in ente:
			grand_total += enter.sales
		return grand_total
	sales_total.short_description = _('sales stock')

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['admin', 'category', 'manufacturer', 'tax', 'title', 'slug', 'content', 'image', 'fsale', 'price', 'min_limit', 'max_limit', 'weight', 'weight_type', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")

class DiscountAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'code', 'amount', 'valid', 'timestamp_and_utimestamp', 'status','actionbutton',)
	search_fields = ('title', 'code', 'amount', 'valid',)

	fieldsets=(        
	   (None,{"fields": (('title'),('code', 'amount'),('valid')),}), 
	)

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s" class="editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def has_change_permission(self, request, obj=None):
		if request.user.role == 'Admin':
			return True
		else:
			return False

	def has_delete_permission(self, request, obj=None):
		if request.user.role == 'Admin':
			return True
		else:
			return False

	def has_add_permission(self,request):
		if request.user.role == 'Admin':
			return True
		else:
			return False

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['title', 'code', 'amount', 'valid', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")

class WishlistAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'product', 'quantity',  'price', 'total', 'timestamp_and_utimestamp', 'cart', 'status','actionbutton',)
	search_fields = ('price', 'total',)

	# fieldsets=(
	#    (None,{"fields": (('user', 'product'),('cart', 'quantity'),('price', 'total'),),}), 
	# )

	formfield_overrides = {
		# models.CharField: {'widget': TextInput(attrs={'size':'20'})},
		models.TextField: {'widget': Textarea(attrs={'rows':8, 'cols':40})},
	}

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s" class="editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['user', 'product', 'quantity',  'note', 'price', 'total', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")

class PaymentAdmin(admin.ModelAdmin):
	list_display = ('id', 'order', 'method', 'amount', 'payed', 'rawdata', 'timestamp_and_utimestamp', 'status','actionbutton',)
	autocomplete_fields = ('order',)
	search_fields = ('method', 'amount', 'payed',)
	readonly_fields = ('rawdata',)

	fieldsets=(        
	   (None,{"fields": (('order'),('method', 'rawdata'),('amount', 'payed'),),}), 
	)

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s" class="editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def has_change_permission(self, request, obj=None):
		if request.user.role == 'Admin':
			return True
		else:
			return False

	def has_delete_permission(self, request, obj=None):
		if request.user.role == 'Admin':
			return True
		else:
			return False

	def has_add_permission(self,request):
		if request.user.role == 'Admin':
			return True
		else:
			return False

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		if request.user.role == 'Admin':
			return qs
		return qs.filter(order__seller=request.user)

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['order', 'method', 'amount', 'payed', 'rawdata', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")

class AvailabilityAdmin(admin.ModelAdmin):
	list_display = ('id', 'get_product', 'get_seller', 'quantity', 'sales', 'timestamp_and_utimestamp', 'status', 'actionbutton',)
	search_fields = ('quantity',)
	autocomplete_fields = ('product',)

	fieldsets=(        
	   (None,{"fields": (('seller','product'),('quantity', 'sales'),),}), 
	)

	def get_product(self, obj):
		return obj.product.title
	get_product.short_description = _('Product')

	def get_seller(self, obj):
		return obj.seller.username
	get_seller.short_description = _('Seller')

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s" class="editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		if request.user.role == 'Admin':
			return qs
		return qs.filter(seller=request.user)

	def has_delete_permission(self, request, obj=None):
		if request.user.role == 'Admin':
			return True
		else:
			return False

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['seller', 'product', 'quantity',  'sales', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")

	# def has_add_permission(self,request):
	# 	if request.user.role == 'Seller':
	# 		return True
	# 	else:
	# 		return False

	# def has_change_permission(self, request, obj=None):
	# 	if request.user.role == 'Seller':
	# 		return True
	# 	else:
	# 		return False

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == 'seller':
			kwargs['queryset'] = User.objects.filter(role='Seller')
		return super(AvailabilityAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class Over18InLine(admin.TabularInline):
	model = Over18
	extra = 0
	fields = ('country', 'dob', 'document', 'status',)
	verbose_name = _("Adult Document")
	verbose_name_plural = _("Adult Document")
	# autocomplete_fields = ['product',]
	# classes = ['collapse', 'extrapretty']


class OrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'address', 'price', 'note', 'total', 'date', 'timestamp_and_utimestamp', 'status','actionbutton',)
	search_fields = ('total', 'date', 'address__title','seller__username', 'status')
	filter_horizontal = ('wishlist',)
	autocomplete_fields = ('address',)
	readonly_fields = []
	inlines = [Over18InLine]

	fieldsets=(        
	   (None,{"fields": (('wishlist'),('discount'), ('address'),('seller'),('driver'),('price', 'total'),('date', 'note'),('confirm', 'adult', 'driverconfirm'),('paymode'),('status')),}), 
	)

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s" class="editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def get_readonly_fields(self, request, obj=None):
		readonly_fields = super().get_readonly_fields(request, obj)
		if obj:
			if obj.status == 'IN TRANSIT' or obj.status == 'DELIVERED': # editing an existing object
				return readonly_fields + ['status', 'driver']
		return readonly_fields

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		if request.user.role == 'Admin':
			return qs
		return qs.filter(seller=request.user)

	def has_add_permission(self,request):
		if request.user.role == 'Admin' or request.user.role == 'Seller':
			return True
		else:
			return False

	def has_delete_permission(self, request, obj=None):
		if request.user.role == 'Admin':
			return True
		else:
			return False

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == 'seller':
			kwargs['queryset'] = User.objects.filter(role='Seller')
		if db_field.name == 'driver':
			kwargs['queryset'] = User.objects.filter(role='Driver')
		return super(OrderAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['discount', 'wishlist', 'driver', 'seller', 'address', 'price', 'total', 'date', 'confirm', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")

class DispatcherAdmin(admin.ModelAdmin):
	list_display = ('id', 'address', 'price', 'total', 'date', 'timestamp_and_utimestamp', 'status','actionbutton',)
	search_fields = ('total', 'date',)
	filter_horizontal = ('wishlist',)
	# autocomplete_fields = ('discount', 'seller', 'driver',)

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s" class="editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == 'driver':
			kwargs['queryset'] = User.objects.filter(role='Driver')
		if db_field.name == 'seller':
			kwargs['queryset'] = User.objects.filter(role='Seller')
		return super().formfield_for_foreignkey(db_field, request, **kwargs)

	def get_queryset(self, request):
		qs = super(DispatcherAdmin, self).get_queryset(request)
		for qw in qs:
			prod = Order.objects.filter(status = 'Active')
		return qs

class SupportAdmin(admin.ModelAdmin):
	list_display = ('id', 'order', 'user', 'title', 'content', 'timestamp_and_utimestamp', 'status','actionbutton',)
	search_fields = ('title',)
	autocomplete_fields = ('parent', 'user', 'order',)

	fieldsets=(        
	   (None,{"fields": (('parent'), ('user', 'order'),('title'),('content'),),}), 
	)

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s" class="editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		if request.user.role == 'Seller':
			return qs
		return qs.filter(user=request.user)

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['order', 'user', 'title', 'content', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")

class RatingAdmin(admin.ModelAdmin):
	list_display = ('id', 'product', 'user', 'star', 'review', 'timestamp_and_utimestamp', 'status','actionbutton',)
	search_fields = ('star',)
	autocomplete_fields = ('product', 'user',)

	fieldsets=(        
	   (None,{"fields": (('user', 'product'),('star'), ('review'),),}), 
	)

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s" class = "editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	# def get_queryset(self, request):
	# 	qs = super().get_queryset(request)
	# 	if request.user.role == 'Seller':
	# 		return qs
	# 	return qs.filter(user=request.user)

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['product', 'user', 'star', 'review', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")

class FaqAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'content', 'timestamp_and_utimestamp', 'status','actionbutton',)
	search_fields = ('title',)

	fieldsets=(        
	   (None,{"fields": (('title', 'slug'),('content'),),}), 
	)

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s" class = "editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['title', 'slug', 'content', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")

class ManufacturerAdmin(admin.ModelAdmin):
	list_display = ('title', 'estd', 'email', 'timestamp_and_utimestamp', 'status','actionbutton',)
	search_fields = ('title',)

	fieldsets=(        
	   (None,{"fields": (('title','slug'),('content'),('email', 'mobile'),('estd', 'logo'),),}), 
	)

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s" class = "editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['title', 'slug', 'estd', 'logo', 'email', 'mobile', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")

class TaxAdmin(admin.ModelAdmin):
	list_display = ('title', 'code', 'percentage', 'timestamp_and_utimestamp', 'status', 'actionbutton',)
	search_fields = ('title',)

	fieldsets=(        
	   (None,{"fields": (('title'),('code', 'percentage'),),}), 
	)

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s" class = "editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def has_add_permission(self,request):
		if request.user.role == 'Admin':
			return True
		else:
			return False

	def has_change_permission(self, request, obj=None):
		if request.user.role == 'Admin':
			return True
		else:
			return False

	def has_delete_permission(self, request, obj=None):
		if request.user.role == 'Admin':
			return False

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['title', 'code', 'percentage', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")

class SubscribeAdmin(admin.ModelAdmin):
	list_display = ('id', 'email', 'url', 'timestamp_and_utimestamp', 'status', 'actionbutton',)
	search_fields = ('email',)

	fieldsets=(        
	   (None,{"fields": (('email'), ('url'),),}), 
	)

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s" class = "editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = 'Action'

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['email', 'url', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")

class PageAdmin(admin.ModelAdmin):
	list_display = ('title', 'keyword', 'meta_description', 'timestamp_and_utimestamp', 'status', 'actionbutton',)
	search_fields = ('title',)
	readonly_fields = ('track', 'utrack',)

	fieldsets=(        
	   (None,{"fields": (('title', 'slug'), ('content'),('keyword', 'meta_title'),('meta_description'),('status')),}), 
	)

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s" class = "editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['title', 'slug', 'keyword','meta_title', 'meta_description', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")

class PopupAdmin(admin.ModelAdmin):
	list_display = ('title', 'timestamp_and_utimestamp', 'status','actionbutton',)
	search_fields = ('title',)
	readonly_fields = ('track', 'utrack',)

	fieldsets=(        
	   (None,{"fields": (('title', 'image'), ('status'),),}), 
	)

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s" class = "editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['title', 'image', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")


class VehicleTypeAdmin(admin.ModelAdmin):
	list_display = ('title', 'timestamp_and_utimestamp', 'status','actionbutton',)
	search_fields = ('title',)

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s" class = "editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['title', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")


class DocTypeAdmin(admin.ModelAdmin):
	list_display = ('title', 'timestamp_and_utimestamp', 'status','actionbutton',)
	search_fields = ('title',)

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s" class = "editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description =_(_('Added/Last Modified'))

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['title', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")


class DocumentAdmin(admin.ModelAdmin):
	list_display = ('documentimg', 'user','timestamp_and_utimestamp', 'status','actionbutton',)
	search_fields = ('title',)
	autocomplete_fields = ('doctype',)
	related_search_fields = {
	   'user': ('first_name', 'email', 'username'),
	}

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s" class = "editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == 'user':
			kwargs['queryset'] = User.objects.filter(role='Driver')
		return super().formfield_for_foreignkey(db_field, request, **kwargs)


	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	def documentimg(self, obj):
		# used in the admin site model as a "thumbnail"
		if obj.image:
			return mark_safe('<img src="%s" width="40px" height="42px" />' % obj.image.url)
		else:
			return 'No Image Found'
	documentimg.short_description = _('Image')

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['user_username', 'doctype_title', 'image', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")

class Over18Admin(admin.ModelAdmin):
	list_display = ('order', 'dob', 'documentimg', 'timestamp_and_utimestamp', 'status','actionbutton',)
	search_fields = ('title',)
	autocomplete_fields = ('order','country',) 

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s" class = "editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	def documentimg(self, obj):
		# used in the admin site model as a "thumbnail"
		try:
			return mark_safe('<img src="%s" width="40px" height="42px" />' % obj.document.url)
		except:
			return _('No Image Found')
	documentimg.short_description = _('document')

	actions = ["export_as_csv"]

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['country__name', 'dob', 'document', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")

class DeliveryChargeAdmin(admin.ModelAdmin):
	list_display = ('title', 'amount', 'timestamp_and_utimestamp', 'status','actionbutton',)
	search_fields = ('title',)
	# autocomplete_fields = ('order','country',)

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s/change/" class = "editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = _('Action')

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')


class BannerAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'bannerimg', 'web', 'mobile', 'timestamp_and_utimestamp', 'status', 'actionbutton',)
	search_fields = ('title',)

	fieldsets=(        
	   (None,{"fields": (('title'),('content'),('mobile', 'web'),('image'),('status')),}), 
	)
    

	def bannerimg(self, obj):
		# used in the admin site model as a "thumbnail"
		if obj.image:
			return mark_safe('<img src="%s" width="40px" height="42px" />' % obj.image.url)
		else:
			return 'No Image Found'
	bannerimg.short_description = 'Banner'


	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="%s/change/" class="editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
		# return format_html('<a href="admin:%s/%s/%s" class="editclsbtn"><i class="fal fa-edit"></i></a> <a class="btn deleteclsbtn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = 'Action'

	

	def timestamp_and_utimestamp(self, obj):
		d = obj.timestamp
		m = obj.utimestamp
		return format_html('Added Date: %s<br> Modified Date: %s' %(datetime.strptime(str(d).split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S'), datetime.strptime(str(m).split('.')[0],'%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M:%S')))
	timestamp_and_utimestamp.short_description = _('Added/Last Modified')

	actions = ["export_as_csv"]

    

	def export_as_csv(self, request, queryset):
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]
		field_names = ['title', 'content', 'image', 'web', 'mobile', 'timestamp', 'utimestamp', 'status']
		
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			row = writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = _("Export Selected")
    





admin.site.register(DeliveryCharge, DeliveryChargeAdmin)
admin.site.register(VehicleDocType)
admin.site.register(VehicleDocument)
admin.site.register(DocType, DocTypeAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(VehicleType, VehicleTypeAdmin)
admin.site.register(User, UserCustomAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Seller, SellerAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(Category, CategoryAdmin)
# admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Availability, AvailabilityAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Over18, Over18Admin)
admin.site.register(Dispatcher, DispatcherAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Support, SupportAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Faq, FaqAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Tax, TaxAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Popup, PopupAdmin)
# admin.site.register(DeliveryCharge, DeliveryChargeAdmin)