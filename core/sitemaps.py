from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from webinars.models import Webinar
from scholarships.models import Scholarship


class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'weekly'

    def items(self):
        return ['core:home', 'core:about', 'contact:contact',
                'webinars:list', 'scholarships:list']

    def location(self, item):
        return reverse(item)


class WebinarSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return Webinar.objects.all()

    def location(self, obj):
        return f'/webinars/{obj.pk}/'

    def lastmod(self, obj):
        return obj.created_at


class ScholarshipSitemap(Sitemap):
    priority = 0.9
    changefreq = 'monthly'

    def items(self):
        return Scholarship.objects.filter(is_active=True)

    def location(self, obj):
        return f'/scholarships/{obj.pk}/'

    def lastmod(self, obj):
        return obj.created_at
