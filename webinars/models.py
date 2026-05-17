from django.db import models
import uuid

class Webinar(models.Model):
    STATUS_CHOICES = [('upcoming','Upcoming'),('live','Live Now'),('past','Past')]
    CATEGORY_CHOICES = [
        ('career','Career Development'),
        ('tech','Technical Skills'),
        ('leadership','Leadership'),
        ('ai','AI & Machine Learning'),
        ('scholarship','Scholarship Guidance'),
    ]
    title            = models.CharField(max_length=300)
    category         = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status           = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    date             = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=90, help_text='Duration in minutes')
    description      = models.TextField()
    image            = models.ImageField(upload_to='webinars/', blank=True, null=True, help_text='Webinar cover image')
    speaker_name     = models.CharField(max_length=200)
    speaker_role     = models.CharField(max_length=200)
    speaker_company  = models.CharField(max_length=200, blank=True)
    speaker_photo    = models.ImageField(upload_to='speakers/', blank=True, null=True)
    zoom_link        = models.URLField(blank=True, help_text='Zoom / Google Meet link for registered participants')
    zoom_password    = models.CharField(max_length=100, blank=True, help_text='Meeting password if any')
    recording_link   = models.URLField(blank=True)
    is_free          = models.BooleanField(default=True)
    max_seats        = models.PositiveIntegerField(default=100)
    whatsapp_group   = models.CharField(max_length=300, blank=True, help_text='WhatsApp group invite link')
    certificate_enabled = models.BooleanField(default=True, help_text='Send e-certificates after webinar ends')
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title

    def seats_taken(self):
        return self.registrations.count()

    def seats_left(self):
        return max(0, self.max_seats - self.seats_taken())

    def is_full(self):
        return self.seats_taken() >= self.max_seats

    def is_past(self):
        from django.utils import timezone
        end_time = self.date + timezone.timedelta(minutes=self.duration_minutes)
        return timezone.now() > end_time


class WebinarRegistration(models.Model):
    webinar          = models.ForeignKey(Webinar, on_delete=models.CASCADE, related_name='registrations')
    full_name        = models.CharField(max_length=200)
    email            = models.EmailField()
    whatsapp_number  = models.CharField(max_length=30, default='', blank=True, help_text='WhatsApp number with country code e.g. +22376543210')
    profession       = models.CharField(max_length=200, blank=True)
    country          = models.CharField(max_length=100, blank=True)
    # Certificate
    certificate_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    certificate_sent = models.BooleanField(default=False)
    attended         = models.BooleanField(default=False, help_text='Mark as attended to send certificate')
    # Meta
    registered_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('webinar', 'email')

    def __str__(self):
        return f"{self.full_name} → {self.webinar.title}"

    def certificate_url(self):
        return f"/webinars/certificate/{self.certificate_code}/"

    def whatsapp_clean(self):
        """Return clean number for WhatsApp API (digits only, no +)"""
        return self.whatsapp_number.replace('+','').replace(' ','').replace('-','')
