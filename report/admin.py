from django.contrib import admin
from django.forms import modelformset_factory
from .models import *
from django.forms import BaseModelFormSet
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.urls import reverse
from home.models import *
from django.db.models import Sum

class LowStocktAdmin(admin.ModelAdmin):
	# change_list_template = 'admin/report.html'
	list_display = ('title', 'productimg', 'timestamp', 'utimestamp', 'status', 'actionbutton',)
	search_fields = ('title',)
	autocomplete_fields = ('admin', 'manufacturer', 'tax',)
	filter_horizontal = ('category',)
	readonly_fields = ('view', 'like', 'unlike', 'impression',)

	def productimg(self, obj):
		if obj.image:
			return mark_safe('<img src="%s" width="40px" height="45px">' % obj.image.url)
	productimg.short_description = 'Image'

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></a> <a class="btn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = 'Action'

	def get_queryset(self, request):
		qs = super(LowStocktAdmin, self).get_queryset(request)
		pid = []
		for qw in qs:
			prod = Availability.objects.filter(product_id = qw.id).aggregate(Sum('quantity'))['quantity__sum']
			# print(prod)
			if prod != None and prod < 5:
				pid.append(qw.id)
		return qs.filter(id__in=pid)

class OutOfStockAdmin(admin.ModelAdmin):
	list_display = ('title', 'productimg', 'timestamp', 'utimestamp', 'status', 'actionbutton',)
	search_fields = ('title',)
	autocomplete_fields = ('admin', 'manufacturer', 'tax',)
	filter_horizontal = ('category',)
	readonly_fields = ('view', 'like', 'unlike', 'impression',)
	
	def productimg(self, obj):
		if obj.image:
			return mark_safe('<img src="%s" width="40px" height="45px">' % obj.image.url)
	productimg.short_description = 'Image'

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></a> <a class="btn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = 'Action'

	def get_queryset(self, request):
		qs = super(OutOfStockAdmin, self).get_queryset(request)
		pid = []
		for qw in qs:
			prod = Availability.objects.filter(product_id = qw.id).aggregate(Sum('quantity'))['quantity__sum']
			# print(prod)
			if prod != None and prod < 1:
				pid.append(qw.id)
		return qs.filter(id__in=pid)	

class StockInAdmin(admin.ModelAdmin):
	list_display = ('title', 'productimg', 'timestamp', 'utimestamp', 'status', 'actionbutton',)
	search_fields = ('title',)
	autocomplete_fields = ('admin', 'manufacturer', 'tax',)
	filter_horizontal = ('category',)
	readonly_fields = ('view', 'like', 'unlike', 'impression',)
	
	def productimg(self, obj):
		if obj.image:
			return mark_safe('<img src="%s" width="40px" height="45px">' % obj.image.url)
	productimg.short_description = 'Image'

	def actionbutton(self, obj):
		info = obj._meta.app_label, obj._meta.model_name
		return format_html('<a href="/dgr/%s/%s/%s"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></a> <a class="btn" href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>' % (obj._meta.app_label, obj._meta.model_name, obj.id, reverse('admin:%s_%s_delete' % info, args=(obj.id,))))
	actionbutton.short_description = 'Action'

	def get_queryset(self, request):
		qs = super(StockInAdmin, self).get_queryset(request)
		pid = []
		for qw in qs:
			prod = Availability.objects.filter(product_id = qw.id).aggregate(Sum('quantity'))['quantity__sum']
			if prod != None and prod > 5:
				pid.append(qw.id)
		return qs.filter(id__in=pid)			

admin.site.register(LowStock, LowStocktAdmin)
admin.site.register(OutOfStock, OutOfStockAdmin)
admin.site.register(StockIn, StockInAdmin)
