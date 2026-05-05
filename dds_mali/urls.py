from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Admin branding
admin.site.site_header  = '🌍 DDS Mali Admin'
admin.site.site_title   = 'DDS Mali'
admin.site.index_title  = 'Diawara Digital & Software — Dashboard'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('scholarships/', include('scholarships.urls')),
    path('webinars/', include('webinars.urls')),
    path('contact/', include('contact.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
