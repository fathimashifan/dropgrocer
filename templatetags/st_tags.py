from django import template
from django.utils.safestring import mark_safe
from django.contrib import admin
from home.models import *
from django.db.models import Sum

register = template.Library()

@register.filter(takes_context=True)
def wishproditem(prod, request):
	# print("Wishlist", prod, request)
	item = Wishlist.objects.filter(user = request.user.id, product = prod, cart = False)
	# print(item)
	return item
@register.filter(takes_context=True)
def wishprod(prod, request):
	item = Wishlist.objects.filter(user = request.user.id, product = prod, cart = True, status = 'Active').values('quantity').last()
	
	if item == None:
		return 0
	else:
		print(item['quantity'])
	return item['quantity']
@register.simple_tag(takes_context=True)
def wish_list(context):
	ab = Wishlist.objects.filter(user=context['request'].user.id , status = 'Active', cart = True).count()
	# print('hello')
	return ab	

@register.simple_tag(takes_context=True)
def wishlist_total(context):
	total = Wishlist.objects.filter(user=context['request'].user.id ,status = 'Active', cart = True).aggregate(Sum('total'))['total__sum']
	# print(total)
	if total == None:
		return 0
	return total
	
@register.filter(takes_context=True)
def wishproditem(prod, request):
	# print("Wishlist", prod, request)
	item = Wishlist.objects.filter(user = request.user.id, product = prod, cart = False)
	# print(item)
	return item

@register.filter(takes_context=True)
def wishprod(prod, request):
	item = Wishlist.objects.filter(user = request.user.id, product = prod, cart = True, status = 'Active').values('quantity').last()
	
	if item == None:
		return 0
	else:
		print(item['quantity'])
	return item['quantity']

