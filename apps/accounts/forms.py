from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.accounts.models import CustomUser


class LoginForm(forms.Form):
    email    = forms.EmailField(label='Correo electrónico')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')


class RegisterForm(UserCreationForm):
    email      = forms.EmailField(required=True, label='Correo electrónico')
    first_name = forms.CharField(max_length=150, required=False, label='Nombre')
    last_name  = forms.CharField(max_length=150, required=False, label='Apellido')

    class Meta:
        model  = CustomUser
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email      = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name  = self.cleaned_data.get('last_name', '')
        # username derived from email prefix to satisfy AbstractUser uniqueness
        base = self.cleaned_data['email'].split('@')[0]
        username = base
        n = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f'{base}{n}'
            n += 1
        user.username = username
        if commit:
            user.save()
        return user
