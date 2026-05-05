"""
WhatsApp messaging via Fonnte API.
Sign up free at https://fonnte.com
After signup, get your token from dashboard and add to settings.py
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def send_whatsapp(to_number: str, message: str) -> dict:
    """
    Send a WhatsApp message via Fonnte API.
    to_number: digits only with country code e.g. '22376543210'
    Returns {'success': True/False, 'message': '...'}
    """
    token = getattr(settings, 'WHATSAPP_API_TOKEN', '')
    if not token:
        logger.warning("WHATSAPP_API_TOKEN not set – message NOT sent to %s", to_number)
        return {'success': False, 'message': 'WhatsApp token not configured'}

    try:
        resp = requests.post(
            'https://api.fonnte.com/send',
            headers={'Authorization': token},
            data={
                'target': to_number,
                'message': message,
                'countryCode': '223',  # Mali default; overridden by full number
            },
            timeout=15
        )
        data = resp.json()
        if data.get('status'):
            return {'success': True, 'message': 'Sent'}
        return {'success': False, 'message': data.get('reason', 'Unknown error')}
    except Exception as e:
        logger.error("WhatsApp send error: %s", e)
        return {'success': False, 'message': str(e)}


def send_whatsapp_with_file(to_number: str, message: str, file_url: str) -> dict:
    """Send WhatsApp message with a document/PDF attachment."""
    token = getattr(settings, 'WHATSAPP_API_TOKEN', '')
    if not token:
        return {'success': False, 'message': 'WhatsApp token not configured'}

    try:
        resp = requests.post(
            'https://api.fonnte.com/send',
            headers={'Authorization': token},
            data={
                'target': to_number,
                'message': message,
                'url': file_url,      # public URL of the PDF
                'filename': 'certificate.pdf',
                'countryCode': '223',
            },
            timeout=20
        )
        data = resp.json()
        if data.get('status'):
            return {'success': True, 'message': 'Sent with attachment'}
        return {'success': False, 'message': data.get('reason', 'Unknown error')}
    except Exception as e:
        logger.error("WhatsApp file send error: %s", e)
        return {'success': False, 'message': str(e)}


def send_webinar_confirmation(registration):
    """Send registration confirmation WhatsApp message."""
    webinar = registration.webinar
    date_str = webinar.date.strftime('%A %d %B %Y at %H:%M GMT')
    msg = (
        f"✅ *Registration Confirmed!*\n\n"
        f"Hello *{registration.full_name}*,\n\n"
        f"You are registered for:\n"
        f"📚 *{webinar.title}*\n"
        f"📅 {date_str}\n"
        f"🎤 Speaker: {webinar.speaker_name} – {webinar.speaker_role}\n"
    )
    if webinar.zoom_link:
        msg += f"\n🔗 *Meeting Link:*\n{webinar.zoom_link}\n"
    if webinar.zoom_password:
        msg += f"🔑 Password: {webinar.zoom_password}\n"
    if webinar.whatsapp_group:
        msg += f"\n💬 Join our WhatsApp group:\n{webinar.whatsapp_group}\n"
    msg += (
        f"\n🌍 *Diawara Digital & Software*\n"
        f"contact@dds-mali.com"
    )
    return send_whatsapp(registration.whatsapp_clean(), msg)


def send_certificate_whatsapp(registration, cert_url: str):
    """Send e-certificate via WhatsApp."""
    webinar = registration.webinar
    msg = (
        f"🎓 *Certificate of Completion*\n\n"
        f"Congratulations *{registration.full_name}*! 🎉\n\n"
        f"You have successfully completed:\n"
        f"📚 *{webinar.title}*\n\n"
        f"Your certificate is ready. Download it below 👇\n\n"
        f"🔗 {cert_url}\n\n"
        f"Thank you for participating!\n"
        f"🌍 *Diawara Digital & Software*"
    )
    return send_whatsapp_with_file(registration.whatsapp_clean(), msg, cert_url)


def send_scholarship_confirmation(application):
    """Send scholarship application confirmation via WhatsApp."""
    sch = application.scholarship
    msg = (
        f"📬 *Application Received!*\n\n"
        f"Hello *{application.full_name}*,\n\n"
        f"We received your application for:\n"
        f"🎓 *{sch.title}*\n"
        f"🏛️ {sch.university}\n"
        f"🌏 {sch.get_country_display()}\n\n"
        f"Our team will review it and contact you within *5-7 business days*.\n\n"
        f"📋 Your reference: *APP-{application.pk:05d}*\n\n"
    )
    if sch.whatsapp_contact:
        msg += f"📞 Questions? Contact us: wa.me/{sch.whatsapp_contact.replace('+','')}\n\n"
    msg += "🌍 *Diawara Digital & Software*\ncontact@dds-mali.com"
    return send_whatsapp(application.whatsapp_clean(), msg)


def send_scholarship_status_update(application):
    """Send status update when admin changes application status."""
    status_msgs = {
        'reviewing': '🔍 Your application is now *under review* by our team.',
        'accepted':  '🎉 *Congratulations!* Your application has been *ACCEPTED*! We will contact you soon with next steps.',
        'rejected':  '😔 Unfortunately your application was not selected this time. Please apply again for other opportunities.',
    }
    msg_body = status_msgs.get(application.status, '')
    if not msg_body:
        return {'success': False, 'message': 'No message for this status'}

    msg = (
        f"📬 *Scholarship Update*\n\n"
        f"Hello *{application.full_name}*,\n\n"
        f"{msg_body}\n\n"
        f"🎓 *{application.scholarship.title}*\n"
        f"📋 Reference: APP-{application.pk:05d}\n\n"
        f"🌍 *Diawara Digital & Software*"
    )
    return send_whatsapp(application.whatsapp_clean(), msg)
