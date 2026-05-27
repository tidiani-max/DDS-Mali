from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.utils import timezone
from .models import Webinar, WebinarRegistration
from .forms import WebinarRegistrationForm
from .utils.certificate import generate_certificate
from .utils.whatsapp import send_webinar_confirmation


def webinar_list(request):
    now = timezone.now()
    all_webinars = Webinar.objects.all()

    # Auto-update status based on date+duration
    for w in all_webinars:
        from datetime import timedelta
        end_time = w.date + timedelta(minutes=w.duration_minutes)
        if timezone.now() > end_time and w.status != 'past':
            w.status = 'past'
            w.save(update_fields=['status'])
        elif w.date > timezone.now() and w.status == 'past':
            w.status = 'upcoming'
            w.save(update_fields=['status'])

    upcoming = Webinar.objects.exclude(status='past').order_by('date')
    past     = Webinar.objects.filter(status='past').order_by('-date')
    return render(request, 'webinars/list.html', {'upcoming': upcoming, 'past': past})


def webinar_detail(request, pk):
    webinar = get_object_or_404(Webinar, pk=pk)
    form = WebinarRegistrationForm()

    if request.method == 'POST':
        form = WebinarRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if WebinarRegistration.objects.filter(webinar=webinar, email=email).exists():
                messages.warning(request, '⚠️ This email is already registered for this webinar.')
            elif webinar.is_full():
                messages.error(request, '❌ Sorry, this webinar is full.')
            else:
                reg = form.save(commit=False)
                reg.webinar = webinar
                reg.save()
                send_webinar_confirmation(reg)
                messages.success(request,
                    '🎉 You are registered! Check WhatsApp for confirmation with the meeting link.')
                return redirect('webinars:detail', pk=pk)

    return render(request, 'webinars/detail.html', {'webinar': webinar, 'form': form})


def checkin(request, pk):
    """
    Check-in page for live webinar attendees.
    Host shares this URL in Zoom chat during the session.
    Participant enters their email → system marks them attended=True.
    """
    webinar = get_object_or_404(Webinar, pk=pk)
    checked_in = False
    error = None
    registration = None

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        if not email:
            error = 'Please enter your email.'
        else:
            try:
                registration = WebinarRegistration.objects.get(
                    webinar=webinar,
                    email__iexact=email
                )
                if registration.attended:
                    # Already checked in — just confirm again
                    checked_in = True
                else:
                    registration.attended = True
                    registration.save()
                    checked_in = True
            except WebinarRegistration.DoesNotExist:
                error = 'No registration found for that email. Make sure you registered first.'

    ctx = {
        'webinar': webinar,
        'checked_in': checked_in,
        'registration': registration,
        'error': error,
    }
    return render(request, 'webinars/Checkin.html', ctx)


def certificate_view(request, cert_code):
    reg = get_object_or_404(WebinarRegistration, certificate_code=cert_code)
    if not reg.attended:
        return render(request, 'webinars/certificate_not_ready.html', {'registration': reg})
    if request.GET.get('download'):
        pdf_bytes = generate_certificate(reg)
        resp = HttpResponse(pdf_bytes, content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="DDS_Certificate_{reg.full_name}.pdf"'
        return resp
    return render(request, 'webinars/certificate.html', {'registration': reg})


def certificate_pdf(request, cert_code):
    reg = get_object_or_404(WebinarRegistration, certificate_code=cert_code)
    if not reg.attended:
        return HttpResponse('Certificate not available yet.', status=403)
    pdf_bytes = generate_certificate(reg)
    resp = HttpResponse(pdf_bytes, content_type='application/pdf')
    resp['Content-Disposition'] = f'inline; filename="DDS_Certificate_{reg.full_name}.pdf"'
    return resp
