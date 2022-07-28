from django.db import models

from home.models import *



from django.utils.translation import gettext as _
# Create your models here.


class Report(Order):
	class Meta:
		proxy = True

class LowStock(Product):
	class Meta:
		proxy = True
		verbose_name_plural = _('Low Stock')

class OutOfStock(Product):
	class Meta:
		proxy = True
		verbose_name_plural = _('Out of Stock')

class StockIn(Product):
	class Meta:
		proxy = True
		verbose_name_plural = _('Stock In')