from django.contrib import admin
from .models import *

class ContinentAdmin(admin.ModelAdmin):
	list_display=('title', 'area', 'population', 'timestamp', 'status',)
	readonly_fields=('timestamp', 'utimestamp',)
	search_fields=('title',)

class LanguageAdmin(admin.ModelAdmin):
	list_display=('name', 'code', 'pattern', 'timestamp', 'status',)
	search_fields=('name', 'code',)

class CountryAdmin(admin.ModelAdmin):
	list_display=('name', 'local', 'code', 'code2', 'code3', 'capital', 'gdp', 'area', 'population', 'timestamp', 'status',)
	search_fields=('name', 'local', 'code', 'code2', 'code3', 'capital',)
	autocomplete_fields=('continent',)

class StateAdmin(admin.ModelAdmin):
	list_display=('title', 'local', 'country', 'capital', 'population', 'timestamp', 'status',)
	search_fields=('title', 'local', 'capital',)
	autocomplete_fields=('country',)

class RegionAdmin(admin.ModelAdmin):
	list_display=('title', 'timestamp', 'status',)
	filter_horizontal=('state',)
	search_fields=('title',)

admin.site.register(Continent, ContinentAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Region, RegionAdmin)

# Register your models here.
