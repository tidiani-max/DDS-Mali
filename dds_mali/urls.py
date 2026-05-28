from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import StaticViewSitemap, WebinarSitemap, ScholarshipSitemap

# Admin branding
admin.site.site_header  = '🌍 DDS Mali Admin'
admin.site.site_title   = 'DDS Mali'
admin.site.index_title  = 'Diawara Digital & Software — Dashboard'

sitemaps = {
    'static':       StaticViewSitemap,
    'webinars':     WebinarSitemap,
    'scholarships': ScholarshipSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('scholarships/', include('scholarships.urls')),
    path('webinars/', include('webinars.urls')),
    path('contact/', include('contact.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# Serve media assets explicitly regardless of DEBUG state
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
