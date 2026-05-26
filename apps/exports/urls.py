from django.urls import path
from apps.exports import views

urlpatterns = [
    path('exports/pdf/',          views.pdf_form_view,     name='pdf_form'),
    path('exports/pdf/download/', views.pdf_download_view, name='pdf_download'),
]
