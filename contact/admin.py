from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ('full_name', 'email', 'phone', 'service_badge',
                     'subject', 'is_read', 'submitted_at')
    list_filter   = ('service', 'is_read')
    list_editable = ('is_read',)
    search_fields = ('full_name', 'email', 'subject', 'message')
    readonly_fields = ('submitted_at',)

    fieldsets = (
        ('👤 Contact Info', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('📩 Message', {
            'fields': ('service', 'subject', 'message', 'is_read', 'submitted_at')
        }),
    )

    def service_badge(self, obj):
        colors = {
            'ai': '#8b5cf6', 'web': '#3b82f6', 'scholarship': '#16a34a',
            'webinar': '#0ea5e9', 'other': '#64748b'
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 9px;border-radius:10px;font-size:11px">{}</span>',
            colors.get(obj.service, '#64748b'), obj.get_service_display()
        )
    service_badge.short_description = 'Service'

    def has_add_permission(self, request):
        return False  # Messages only come from the website form
