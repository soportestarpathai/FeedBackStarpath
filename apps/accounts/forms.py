from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.accounts.models import User

class LoginForm(forms.Form):
    email    = forms.EmailField(label='Correo electrónico')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Correo electrónico')

    class Meta:
        model  = User
        fields = ('username', 'email', 'password1', 'password2')
