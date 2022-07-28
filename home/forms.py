from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *
import datetime
from django.utils.translation import gettext_lazy as _


class NewDeliverAddress(ModelForm):
	class Meta:
		model = Address
		fields = ('title', 'country', 'state', 'city', 'address', 'postcode',)
		widgets = {
			'title': forms.TextInput(attrs={'placeholder': 'title', 'class':'form-control'}),
			'country': forms.Select(attrs={'placeholder': 'country', 'class':'form-control'}),
			'state': forms.Select(attrs={'placeholder': 'state', 'class':'form-control'}),
			'city': forms.TextInput(attrs={'placeholder': 'city', 'class':'form-control'}),
			'address': forms.TextInput(attrs={'placeholder': 'address', 'class':'form-control'}),
			'postcode': forms.NumberInput( attrs={'placeholder': 'postcode', 'class':'form-control postcode12'}),
		}

class SubscribeForm(ModelForm):
	class Meta:
		model=Subscribe
		fields=('email', 'url',)

class Over18Form(ModelForm):
	class Meta:
		model=Over18
		fields=('dob', 'document',)

		widgets = {
			'dob': forms.DateInput(attrs={'type':'date','placeholder': 'dob', 'class':'form-control'}),
			'document': forms.FileInput(attrs={'type':'file','placeholder': 'Upload Document', 'class':'form-control docinpt'}),
		}

	# def clean_dob(self):
	# 	dob = self.cleaned_data.get('dob', False)
	# 	if dob:
	# 		print(dob, '888888888', (datetime.datetime.now().date() - dob).days)
	# 		if (datetime.datetime.now().date() - dob).days < 18:
	# 			print('55555555555')
	# 			raise forms.ValidationError(_('Age must be 18+'))
	# 	return dob

# class PayModeForm(ModelForm):
# 	class Meta:
# 		model=O
# 		fields=('email', 'url',)

class CustomerAdminForm(UserCreationForm):
	class Meta(UserCreationForm.Meta):
		model = User
		fields = ('username', 'email', 'mobile', 'role')

class UserProfileForm(forms.ModelForm):

	class Meta:
		model=User
		fields=('username', 'first_name', 'last_name', 'gender', 'dob', 'email', 'mobile', 'image')
		widgets = {
			'first_name': forms.TextInput(attrs={'placeholder': 'first name', 'class':'form-control'}),
			'last_name': forms.TextInput(attrs={'placeholder': 'last name', 'class':'form-control'}),
			'email': forms.EmailInput(attrs={'placeholder': 'email', 'class':'form-control'}),
			'gender': forms.Select(attrs={'placeholder': 'gender', 'class':'form-control'}),
			'dob': forms.DateInput(attrs={'type':'date','placeholder': 'dob', 'class':'form-control'}),
		}
