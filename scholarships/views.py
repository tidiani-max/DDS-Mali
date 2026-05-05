from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Scholarship, ScholarshipApplication
from .forms import ScholarshipApplicationForm
from webinars.utils.whatsapp import send_scholarship_confirmation


def scholarship_list(request):
    country  = request.GET.get('country', '')
    level    = request.GET.get('level', '')
    qs = Scholarship.objects.filter(is_active=True)
    if country:
        qs = qs.filter(country=country)
    if level:
        qs = qs.filter(level=level)
    featured = Scholarship.objects.filter(is_active=True, is_featured=True)
    return render(request, 'scholarships/list.html', {
        'scholarships': qs, 'featured': featured,
        'country': country, 'level': level,
        'country_choices': Scholarship.COUNTRY_CHOICES,
        'level_choices': Scholarship.LEVEL_CHOICES,
    })


def scholarship_detail(request, pk):
    scholarship = get_object_or_404(Scholarship, pk=pk, is_active=True)
    form = ScholarshipApplicationForm()

    if request.method == 'POST':
        form = ScholarshipApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.scholarship = scholarship
            app.save()
            # Send WhatsApp confirmation
            send_scholarship_confirmation(app)
            messages.success(request,
                f'✅ Application submitted! Ref: APP-{app.pk:05d}. '
                'Check WhatsApp for confirmation.')
            return redirect('scholarships:detail', pk=pk)

    return render(request, 'scholarships/detail.html', {'scholarship': scholarship, 'form': form})
