from django import forms
from apps.reports.models import Report
from apps.platforms.models import Platform


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = [
            'titulo', 'descripcion', 'plataforma', 'tipo', 'severidad',
            'url_pagina', 'pasos_reproducir', 'resultado_esperado', 'resultado_obtenido',
        ]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['plataforma'].queryset = Platform.objects.filter(activa=True)
        if user and user.is_usuario:
            for f in ['url_pagina', 'pasos_reproducir', 'resultado_esperado', 'resultado_obtenido']:
                self.fields[f].required = False
                self.fields[f].widget = forms.HiddenInput()
