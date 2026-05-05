from django import forms
from .models import ScholarshipApplication

class ScholarshipApplicationForm(forms.ModelForm):
    class Meta:
        model = ScholarshipApplication
        fields = ['full_name','email','whatsapp_number','nationality','current_education','motivation','cv']
        widgets = {
            'full_name':          forms.TextInput(attrs={'placeholder':'Your full name','class':'form-input'}),
            'email':              forms.EmailInput(attrs={'placeholder':'your@email.com','class':'form-input'}),
            'whatsapp_number':    forms.TextInput(attrs={'placeholder':'+223 76 54 32 10','class':'form-input'}),
            'nationality':        forms.TextInput(attrs={'placeholder':'e.g. Malian','class':'form-input'}),
            'current_education':  forms.TextInput(attrs={'placeholder':'e.g. Bachelor in Computer Science','class':'form-input'}),
            'motivation':         forms.Textarea(attrs={'rows':5,'placeholder':'Why do you want this scholarship? What are your goals?','class':'form-input'}),
            'cv':                 forms.FileInput(attrs={'class':'form-input'}),
        }
