from django.db import models

class Project(models.Model):
    CATEGORY_CHOICES = [
        ('innovation', 'Innovation'),
        ('solution', 'Solution Sur Mesure'),
    ]
    STATUS_CHOICES = [
        ('dev', 'En développement'),
        ('live', 'En ligne'),
        ('done', 'Mission accomplie'),
    ]
    name        = models.CharField(max_length=200)
    category    = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, blank=True)
    sector      = models.CharField(max_length=200)
    description = models.TextField()
    features    = models.TextField(help_text='One feature per line')
    technologies= models.CharField(max_length=300, blank=True)
    icon_emoji  = models.CharField(max_length=10, default='💡')
    icon_color  = models.CharField(max_length=30, default='#3b82f6')
    order       = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    def features_list(self):
        return [f.strip() for f in self.features.splitlines() if f.strip()]


class Testimonial(models.Model):
    ROLE_CHOICES = [('student','Student'),('client','Client')]
    name    = models.CharField(max_length=200)
    role    = models.CharField(max_length=10, choices=ROLE_CHOICES)
    title   = models.CharField(max_length=200)
    quote   = models.TextField()
    avatar  = models.CharField(max_length=10, default='👤')
    active  = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.role})"
