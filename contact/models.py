from django.db import models

class ContactMessage(models.Model):
    SERVICE_CHOICES = [
        ('ai','AI / Custom Software'),
        ('web','Web Development'),
        ('scholarship','Scholarship Guidance'),
        ('webinar','Webinar / Training'),
        ('other','Other'),
    ]
    full_name   = models.CharField(max_length=200)
    email       = models.EmailField()
    phone       = models.CharField(max_length=30, blank=True)
    service     = models.CharField(max_length=20, choices=SERVICE_CHOICES, default='other')
    subject     = models.CharField(max_length=300)
    message     = models.TextField()
    is_read     = models.BooleanField(default=False)
    submitted_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.full_name} – {self.subject}"
