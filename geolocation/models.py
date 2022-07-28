from django.db import models
from django_extensions.db.fields import AutoSlugField
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.translation import gettext_lazy as _


status=[('Active','Active'),('Inactive','Inactive'),('Delete','Delete'),]
pattern=[('LTR','Left to Right'),('RTL','Right to left'),('TTB','Top to Bottom'),('BTT','Bottom to Top')]

class Continent(models.Model):
	title = models.CharField(_('title'), max_length=160)
	slug = AutoSlugField(populate_from='title', editable=True, max_length=160)
	area = models.BigIntegerField(_('area'))
	population = models.BigIntegerField(_('population'))
	timestamp = models.DateTimeField(auto_now_add=True)
	utimestamp = models.DateTimeField(auto_now=True)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.title

	class Meta:
		verbose_name_plural = _('Continent')

class Language(models.Model):
	code=models.CharField(_('code'), max_length=10)
	name=models.CharField(_('name'), max_length=50)
	pattern=models.CharField(_('pattern'), max_length=10, choices=pattern, default='LTR')
	timestamp=models.DateTimeField(auto_now_add=True)
	utimestamp=models.DateTimeField(auto_now=True)
	track=models.TextField(blank=True, editable=False)
	utrack=models.TextField(blank=True, editable=False)
	status=models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = _('Language')

class Country(models.Model):
	continent = models.ForeignKey(Continent, on_delete=models.PROTECT, verbose_name = 'continent')
	name = models.CharField(_('name'), max_length=50)
	local = models.CharField(_('local'), max_length=50)
	code = models.IntegerField(_('code'), )
	code2 = models.CharField(_('code2'), max_length=2)
	code3 = models.CharField(_('code3'), max_length=3)
	capital = models.CharField(_('capital'), max_length=50)
	gdp = models.BigIntegerField(_('gdp'))
	area = models.BigIntegerField(_('area'))
	population = models.BigIntegerField(_('population'))
	latitude = models.FloatField()
	longitude = models.FloatField()
	track = models.TextField(blank=True, editable=False)
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.name
	
	class Meta:
		verbose_name_plural = _('Country')

class State(models.Model):
	country=models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name = 'country')
	title=models.CharField(_('title'), max_length=160)
	slug=AutoSlugField(populate_from='title', editable=True, max_length=160)
	capital=models.CharField(_('capital'), max_length=100)
	local=models.CharField(_('local'), max_length=100, null=True)
	area=models.BigIntegerField(_('area'))
	population=models.BigIntegerField(_('population'))
	longitude=models.FloatField()
	latitude=models.FloatField()
	timestamp=models.DateTimeField(auto_now_add=True)
	utimestamp=models.DateTimeField(auto_now=True)
	track=models.TextField(blank=True, editable=False)
	utrack=models.TextField(blank=True, editable=False)
	status=models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.title

	class Meta:
		verbose_name_plural = _('State')

class Region(models.Model):
	state=models.ManyToManyField(State, verbose_name = 'state')
	title=models.CharField(_('title'), max_length=160)
	slug=AutoSlugField(populate_from='title', editable=True, max_length=160)
	content=RichTextUploadingField(_('content'))
	timestamp=models.DateTimeField(auto_now_add=True)
	utimestamp=models.DateTimeField(auto_now=True)
	track=models.TextField(blank=True, editable=False)
	utrack=models.TextField(blank=True, editable=False)
	status=models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.title

	class Meta:
		verbose_name_plural = _('Region')
