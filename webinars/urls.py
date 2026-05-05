from django.urls import path
from . import views

app_name = 'webinars'
urlpatterns = [
    path('', views.webinar_list, name='list'),
    path('<int:pk>/', views.webinar_detail, name='detail'),
    path('<int:pk>/checkin/', views.checkin, name='checkin'),
    path('certificate/<uuid:cert_code>/', views.certificate_view, name='certificate'),
    path('certificate/<uuid:cert_code>/pdf/', views.certificate_pdf, name='certificate_pdf'),
]