from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Item, Profile


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('phone',)

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ('title', 'description', 'location',
                  'lat', 'lng', 'starting_bid', 'image', 'buyNow',)
