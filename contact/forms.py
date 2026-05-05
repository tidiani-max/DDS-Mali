from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model  = ContactMessage
        fields = ['full_name','email','phone','service','subject','message']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder':'Your full name','class':'form-input'}),
            'email':     forms.EmailInput(attrs={'placeholder':'your@email.com','class':'form-input'}),
            'phone':     forms.TextInput(attrs={'placeholder':'+223 XX XX XX XX','class':'form-input'}),
            'service':   forms.Select(attrs={'class':'form-input'}),
            'subject':   forms.TextInput(attrs={'placeholder':'How can we help?','class':'form-input'}),
            'message':   forms.Textarea(attrs={'rows':5,'placeholder':'Tell us more...','class':'form-input'}),
        }
