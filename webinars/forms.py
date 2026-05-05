from django import forms
from .models import WebinarRegistration

class WebinarRegistrationForm(forms.ModelForm):
    class Meta:
        model  = WebinarRegistration
        fields = ['full_name', 'email', 'whatsapp_number', 'profession', 'country']
        widgets = {
            'full_name':       forms.TextInput(attrs={'placeholder':'Your full name','class':'form-input'}),
            'email':           forms.EmailInput(attrs={'placeholder':'your@email.com','class':'form-input'}),
            'whatsapp_number': forms.TextInput(attrs={'placeholder':'+223 76 54 32 10','class':'form-input'}),
            'profession':      forms.TextInput(attrs={'placeholder':'e.g. Student / Developer','class':'form-input'}),
            'country':         forms.TextInput(attrs={'placeholder':'e.g. Mali, Senegal...','class':'form-input'}),
        }
