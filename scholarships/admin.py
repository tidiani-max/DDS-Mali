from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import Scholarship, ScholarshipApplication
from .utils.whatsapp import send_scholarship_status_update


class ScholarshipApplicationInline(admin.TabularInline):
    model = ScholarshipApplication
    extra = 0
    readonly_fields = ('full_name', 'whatsapp_number', 'email', 'nationality',
                       'current_education', 'submitted_at')
    fields = ('full_name', 'whatsapp_number', 'email', 'status', 'submitted_at')
    show_change_link = True


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display  = ('title', 'country_flag', 'level', 'deadline',
                     'applications_count', 'is_active', 'is_featured')
    list_editable = ('is_active', 'is_featured')
    list_filter   = ('country', 'level', 'is_active', 'is_featured')
    search_fields = ('title', 'university')
    inlines       = [ScholarshipApplicationInline]

    fieldsets = (
        ('🎓 Scholarship Info', {
            'fields': ('title', 'country', 'level', 'university',
                       'description', 'image', 'deadline', 'is_active', 'is_featured')
        }),
        ('📋 Details', {
            'fields': ('benefits', 'requirements'),
            'classes': ('wide',)
        }),
        ('🔗 Links & Contact', {
            'fields': ('link', 'whatsapp_contact')
        }),
    )

    def country_flag(self, obj):
        flags = {'indonesia':'🇮🇩','malaysia':'🇲🇾','thailand':'🇹🇭','other':'🌏'}
        return format_html('{} {}', flags.get(obj.country,'🌏'), obj.get_country_display())
    country_flag.short_description = 'Country'

    def applications_count(self, obj):
        count = obj.applications.count()
        return format_html('<b style="color:#7c3aed">{}</b>', count)
    applications_count.short_description = 'Applications'


@admin.register(ScholarshipApplication)
class ScholarshipApplicationAdmin(admin.ModelAdmin):
    list_display  = ('full_name', 'whatsapp_number', 'email', 'scholarship_name',
                     'nationality', 'status_badge', 'submitted_at', 'send_wa_btn')
    list_filter   = ('status', 'scholarship__country', 'scholarship__level')
    search_fields = ('full_name', 'email', 'whatsapp_number', 'nationality')
    readonly_fields = ('submitted_at', 'updated_at')
    actions       = ['notify_reviewing', 'notify_accepted', 'notify_rejected']

    fieldsets = (
        ('👤 Applicant', {
            'fields': ('scholarship', 'full_name', 'email', 'whatsapp_number',
                       'nationality', 'current_education')
        }),
        ('📝 Application', {
            'fields': ('motivation', 'cv')
        }),
        ('📊 Status', {
            'fields': ('status', 'admin_notes', 'submitted_at', 'updated_at')
        }),
    )

    def scholarship_name(self, obj):
        return obj.scholarship.title[:40]
    scholarship_name.short_description = 'Scholarship'

    def status_badge(self, obj):
        colors = {
            'pending': '#d97706', 'reviewing': '#2563eb',
            'accepted': '#16a34a', 'rejected': '#dc2626'
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600">{}</span>',
            colors.get(obj.status, '#64748b'), obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def send_wa_btn(self, obj):
        return format_html(
            '<a href="notify/{}/" style="background:#16a34a;color:white;padding:3px 8px;border-radius:4px;text-decoration:none;font-size:11px;">📱 Notify</a>',
            obj.pk
        )
    send_wa_btn.short_description = 'WhatsApp'

    def notify_reviewing(self, request, queryset):
        queryset.update(status='reviewing')
        sent = 0
        for app in queryset:
            r = send_scholarship_status_update(app)
            if r['success']:
                sent += 1
        self.message_user(request, f'✅ {queryset.count()} marked as reviewing, {sent} WA notifications sent.')
    notify_reviewing.short_description = '🔍 Mark reviewing + notify via WhatsApp'

    def notify_accepted(self, request, queryset):
        queryset.update(status='accepted')
        sent = 0
        for app in queryset:
            r = send_scholarship_status_update(app)
            if r['success']:
                sent += 1
        self.message_user(request, f'🎉 {queryset.count()} accepted, {sent} WA notifications sent.')
    notify_accepted.short_description = '✅ Accept + notify via WhatsApp'

    def notify_rejected(self, request, queryset):
        queryset.update(status='rejected')
        sent = 0
        for app in queryset:
            r = send_scholarship_status_update(app)
            if r['success']:
                sent += 1
        self.message_user(request, f'{queryset.count()} rejected, {sent} WA notifications sent.')
    notify_rejected.short_description = '❌ Reject + notify via WhatsApp'
