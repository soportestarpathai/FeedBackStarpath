from django import forms
from apps.platforms.models import Platform

class PlatformForm(forms.ModelForm):
    class Meta:
        model  = Platform
        fields = ['nombre', 'descripcion', 'color']
