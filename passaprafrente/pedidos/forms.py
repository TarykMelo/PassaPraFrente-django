from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['nota', 'comentario']
        widgets = {
            'nota': forms.Select(attrs={'class': 'form-select'}),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Conte como foi sua experiência com o vendedor...',
                'rows': 4
            }),
        }