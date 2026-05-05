from django.contrib import admin
from .models import Project, Testimonial

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name','category','status','order')
    list_editable = ('order',)
    list_filter = ('category','status')

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name','role','active')
    list_editable = ('active',)
