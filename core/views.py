from django.shortcuts import render
from .models import Project, Testimonial
from scholarships.models import Scholarship
from webinars.models import Webinar

def home(request):
    innovations = Project.objects.filter(category='innovation')
    solutions   = Project.objects.filter(category='solution')
    testimonials= Testimonial.objects.filter(active=True)
    upcoming_webinars = Webinar.objects.filter(status='upcoming').order_by('date')[:3]
    scholarships = Scholarship.objects.filter(is_active=True)[:3]
    ctx = {
        'innovations': innovations,
        'solutions': solutions,
        'testimonials': testimonials,
        'upcoming_webinars': upcoming_webinars,
        'scholarships': scholarships,
    }
    return render(request, 'core/home.html', ctx)

def about(request):
    return render(request, 'core/about.html')
