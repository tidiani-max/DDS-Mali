from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from django.urls import path
from django.contrib import messages
from django.shortcuts import redirect
from .models import Webinar, WebinarRegistration
from .utils.certificate import generate_certificate
from .utils.whatsapp import send_certificate_whatsapp, send_webinar_confirmation
from django.conf import settings


def site_url():
    return getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')


class WebinarRegistrationInline(admin.TabularInline):
    model = WebinarRegistration
    extra = 0
    can_delete = True
    show_change_link = True
    readonly_fields = ('full_name', 'whatsapp_number', 'email', 'profession',
                       'country', 'registered_at', 'certificate_sent',
                       'certificate_link', 'send_cert_btn')
    fields = ('full_name', 'whatsapp_number', 'email', 'attended',
              'certificate_sent', 'certificate_link', 'send_cert_btn')

    def has_add_permission(self, request, obj=None):
        return False

    def certificate_link(self, obj):
        url = f"{site_url()}/webinars/certificate/{obj.certificate_code}/"
        return format_html('<a href="{}" target="_blank">📄 View</a>', url)
    certificate_link.short_description = 'Certificate'

    def send_cert_btn(self, obj):
        if obj.attended:
            return format_html(
                '<a href="../../../webinarregistration/{}/send-cert/" '
                'style="background:#16a34a;color:white;padding:4px 10px;'
                'border-radius:4px;text-decoration:none;font-size:12px;">📱 WA</a>',
                obj.pk
            )
        return '—'
    send_cert_btn.short_description = 'Send via WA'


@admin.register(Webinar)
class WebinarAdmin(admin.ModelAdmin):
    list_display  = ('title', 'status', 'date', 'speaker_name',
                     'seats_display', 'checkin_link_col', 'certificate_enabled', 'webinar_actions')
    list_filter   = ('status', 'category', 'is_free', 'certificate_enabled')
    list_editable = ('status',)
    search_fields = ('title', 'speaker_name')
    inlines       = [WebinarRegistrationInline]

    fieldsets = (
        ('📚 Webinar Info', {
            'fields': ('title', 'category', 'status', 'date', 'duration_minutes',
                       'description', 'image', 'is_free', 'max_seats')
        }),
        ('🎤 Speaker', {
            'fields': ('speaker_name', 'speaker_role', 'speaker_company', 'speaker_photo')
        }),
        ('🔗 Links', {
            'fields': ('zoom_link', 'zoom_password', 'recording_link', 'whatsapp_group')
        }),
        ('📋 Check-in Link', {
            'description': '⬇️ Share this link in Zoom chat during the live session so participants can self-check-in',
            'fields': ('checkin_url_display',),
        }),
        ('🎓 Certificate', {
            'fields': ('certificate_enabled',)
        }),
    )
    readonly_fields = ('checkin_url_display',)

    def checkin_url_display(self, obj):
        if obj.pk:
            url = f"{site_url()}/webinars/{obj.pk}/checkin/"
            return format_html(
                '<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">'
                '<code style="background:#f1f5f9;padding:8px 14px;border-radius:8px;'
                'font-size:14px;border:1px solid #e2e8f0;">{}</code>'
                '<a href="{}" target="_blank" style="background:#0ea5e9;color:white;'
                'padding:8px 16px;border-radius:8px;text-decoration:none;font-size:13px;'
                'font-weight:600;">🔗 Open Page</a>'
                '</div>'
                '<p style="margin-top:8px;font-size:12px;color:#64748b;">'
                '📱 Paste this in your Zoom/Meet chat → participants click it → '
                'enter their email → marked attended automatically</p>',
                url, url
            )
        return '— Save the webinar first to generate the check-in link —'
    checkin_url_display.short_description = 'Check-in URL (share during live session)'

    def checkin_link_col(self, obj):
        url = f"{site_url()}/webinars/{obj.pk}/checkin/"
        return format_html(
            '<a href="{}" target="_blank" title="Open check-in page" '
            'style="background:#0ea5e9;color:white;padding:3px 8px;'
            'border-radius:6px;text-decoration:none;font-size:11px;font-weight:600;">'
            '📋 Check-in</a>',
            url
        )
    checkin_link_col.short_description = 'Check-in'

    def seats_display(self, obj):
        taken = obj.seats_taken()
        total = obj.max_seats
        pct = int(taken / total * 100) if total else 0
        color = '#16a34a' if pct < 70 else '#d97706' if pct < 90 else '#dc2626'
        return format_html('<span style="color:{};font-weight:600;">{}/{}</span>', color, taken, total)
    seats_display.short_description = 'Seats'

    def webinar_actions(self, obj):
        return format_html(
            '<a href="send-all-certs/{}/" '
            'style="background:#7c3aed;color:white;padding:3px 8px;border-radius:6px;'
            'text-decoration:none;font-size:11px;font-weight:600;">'
            '🎓 Certs</a>',
            obj.pk
        )
    webinar_actions.short_description = 'Actions'

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('send-all-certs/<int:webinar_id>/',
                 self.admin_site.admin_view(self.send_all_certificates),
                 name='webinar_send_all_certs'),
        ]
        return custom + urls

    def send_all_certificates(self, request, webinar_id):
        webinar = Webinar.objects.get(pk=webinar_id)
        attended = webinar.registrations.filter(attended=True, certificate_sent=False)
        sent = 0
        for reg in attended:
            cert_url = f"{site_url()}/webinars/certificate/{reg.certificate_code}/"
            result = send_certificate_whatsapp(reg, cert_url)
            if result['success']:
                reg.certificate_sent = True
                reg.save()
                sent += 1
        if sent:
            messages.success(request, f'✅ Certificates sent to {sent} participants via WhatsApp.')
        else:
            messages.warning(request,
                '⚠️ No certificates sent. Make sure WhatsApp token is configured '
                'and participants are marked as attended.')
        return redirect(f'/admin/webinars/webinar/{webinar_id}/change/')


@admin.register(WebinarRegistration)
class WebinarRegistrationAdmin(admin.ModelAdmin):
    list_display  = ('full_name', 'whatsapp_number', 'email', 'webinar_title',
                     'attended', 'certificate_sent', 'registered_at', 'actions_col')
    list_filter   = ('webinar', 'attended', 'certificate_sent')
    list_editable = ('attended',)
    search_fields = ('full_name', 'email', 'whatsapp_number')
    readonly_fields = ('certificate_code', 'certificate_url_display', 'registered_at')
    actions       = ['mark_attended', 'send_certificates_wa', 'download_certificate']

    fieldsets = (
        ('👤 Participant', {
            'fields': ('webinar', 'full_name', 'email', 'whatsapp_number',
                       'profession', 'country')
        }),
        ('✅ Attendance & Certificate', {
            'fields': ('attended', 'certificate_sent', 'certificate_code',
                       'certificate_url_display', 'registered_at')
        }),
    )

    def webinar_title(self, obj):
        return obj.webinar.title[:45]
    webinar_title.short_description = 'Webinar'

    def certificate_url_display(self, obj):
        url = f"{site_url()}/webinars/certificate/{obj.certificate_code}/"
        return format_html(
            '<a href="{}" target="_blank">{}</a>', url, url
        )
    certificate_url_display.short_description = 'Certificate URL'

    def actions_col(self, obj):
        cert_url = f"/webinars/certificate/{obj.certificate_code}/"
        send_url = f"/admin/webinars/webinarregistration/{obj.pk}/send-cert/"
        return format_html(
            '<a href="{}" target="_blank" style="margin-right:4px;font-size:12px;">📄</a>'
            '<a href="{}" style="font-size:12px;">📱</a>',
            cert_url, send_url
        )
    actions_col.short_description = 'Actions'

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('<int:reg_id>/send-cert/',
                 self.admin_site.admin_view(self.send_single_certificate),
                 name='reg_send_cert'),
        ]
        return custom + urls

    def send_single_certificate(self, request, reg_id):
        reg = WebinarRegistration.objects.get(pk=reg_id)
        if not reg.attended:
            messages.error(request, f'❌ {reg.full_name} is not marked as attended yet.')
            return redirect('/admin/webinars/webinarregistration/')
        cert_url = f"{site_url()}/webinars/certificate/{reg.certificate_code}/"
        result = send_certificate_whatsapp(reg, cert_url)
        if result['success']:
            reg.certificate_sent = True
            reg.save()
            messages.success(request, f'✅ Certificate sent to {reg.full_name} on WhatsApp.')
        else:
            messages.error(request,
                f'❌ WhatsApp send failed: {result["message"]}. '
                f'Make sure WHATSAPP_API_TOKEN is set in settings.py')
        return redirect('/admin/webinars/webinarregistration/')

    def mark_attended(self, request, queryset):
        updated = queryset.update(attended=True)
        self.message_user(request, f'✅ {updated} participants marked as attended.')
    mark_attended.short_description = '✅ Mark as attended'

    def send_certificates_wa(self, request, queryset):
        sent = 0
        skipped = 0
        for reg in queryset:
            if not reg.attended:
                skipped += 1
                continue
            cert_url = f"{site_url()}/webinars/certificate/{reg.certificate_code}/"
            result = send_certificate_whatsapp(reg, cert_url)
            if result['success']:
                reg.certificate_sent = True
                reg.save()
                sent += 1
        msg = f'📱 Sent {sent} certificates via WhatsApp.'
        if skipped:
            msg += f' {skipped} skipped (not attended).'
        self.message_user(request, msg)
    send_certificates_wa.short_description = '📱 Send certificates via WhatsApp'

    def download_certificate(self, request, queryset):
        if queryset.count() == 1:
            reg = queryset.first()
            if not reg.attended:
                self.message_user(request,
                    f'⚠️ {reg.full_name} is not marked as attended.', level='warning')
                return
            pdf_bytes = generate_certificate(reg)
            resp = HttpResponse(pdf_bytes, content_type='application/pdf')
            resp['Content-Disposition'] = f'attachment; filename="DDS_Certificate_{reg.full_name}.pdf"'
            return resp
        self.message_user(request, 'Select exactly 1 registration to download.', level='warning')
    download_certificate.short_description = '📥 Download PDF certificate'