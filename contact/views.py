from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm

def contact(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            msg = form.save()
            # Try to send email notification to admin
            try:
                send_mail(
                    subject=f'[DDS] New contact: {msg.subject}',
                    message=f'From: {msg.full_name} <{msg.email}>\nPhone: {msg.phone}\nService: {msg.get_service_display()}\n\n{msg.message}',
                    from_email=settings.CONTACT_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, '✅ Message sent! We will get back to you within 24 hours.')
            return redirect('contact:contact')
    return render(request, 'contact/contact.html', {'form': form})
