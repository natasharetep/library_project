from django import forms 
from .models import *
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()



class CustomUserCreationForm(UserCreationForm):
    # email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class BookAddForm(forms.ModelForm):
    class Meta:
        model = BookAdd
        fields = '__all__'
        widgets = {
            'book_name': forms.TextInput(attrs={'class': 'form-control mt-3', 'placeholder': 'Enter Book Name'}),
            'author': forms.TextInput(attrs={'class': 'form-control mt-3', 'placeholder': 'Enter Book Title'}),
            'entry_date': forms.DateInput(attrs={'class': 'form-control mt-3', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-control mt-3'}),
            'description': forms.Textarea(attrs={'class': 'form-control mt-3', 'placeholder': 'Enter Description'}),
            'book_image': forms.ClearableFileInput(attrs={'class': 'form-control mt-3'}),

        }