from django.db import models

class Scholarship(models.Model):
    COUNTRY_CHOICES = [
    ('indonesia', 'Indonesia'),
    ('malaysia',  'Malaysia'),
    ('thailand',  'Thailand'),
    ('taiwan',    'Taiwan'),
    ('japan',     'Japan'),
    ('singapore', 'Singapore'),
    ('china',     'China'),
    ('other',     'Other'),
]
    LEVEL_CHOICES = [
        ('bachelor','Bachelor'),
        ('master','Master'),
        ('phd','PhD'),
        ('short','Short Course'),
    ]
    title           = models.CharField(max_length=300)
    country         = models.CharField(max_length=20, choices=COUNTRY_CHOICES, default='indonesia')
    level           = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    university      = models.CharField(max_length=300)
    description     = models.TextField()
    benefits        = models.TextField(help_text='One benefit per line')
    requirements    = models.TextField(help_text='One requirement per line')
    deadline        = models.DateField()
    image           = models.ImageField(upload_to='scholarships/', blank=True, null=True, help_text='Scholarship cover image')
    link            = models.URLField(blank=True, help_text='Official scholarship page URL')
    whatsapp_contact= models.CharField(max_length=30, blank=True, help_text='WhatsApp number to contact for this scholarship')
    is_active       = models.BooleanField(default=True)
    is_featured     = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['deadline']

    def __str__(self):
        return self.title

    def benefits_list(self):
        return [b.strip() for b in self.benefits.splitlines() if b.strip()]

    def requirements_list(self):
        return [r.strip() for r in self.requirements.splitlines() if r.strip()]

    def is_open(self):
        from django.utils import timezone
        return self.deadline >= timezone.now().date()

class ScholarshipApplication(models.Model):
    STATUS_CHOICES = [
        ('pending','Pending'),
        ('reviewing','Under Review'),
        ('accepted','Accepted'),
        ('rejected','Rejected'),
    ]
    scholarship      = models.ForeignKey(Scholarship, on_delete=models.CASCADE, related_name='applications')
    full_name        = models.CharField(max_length=200)
    email            = models.EmailField()
    whatsapp_number  = models.CharField(max_length=30, default='', blank=True, help_text='WhatsApp with country code e.g. +22376543210')
    nationality      = models.CharField(max_length=100)
    current_education= models.CharField(max_length=200)
    motivation       = models.TextField()
    cv               = models.FileField(upload_to='cvs/', blank=True, null=True)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes      = models.TextField(blank=True, help_text='Internal notes (not shown to applicant)')
    submitted_at     = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} → {self.scholarship.title}"

    def whatsapp_clean(self):
        return self.whatsapp_number.replace('+','').replace(' ','').replace('-','')
