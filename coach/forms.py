# coach/forms.py
from django import forms
from .models import Coach

class CoachForm(forms.ModelForm):
    class Meta:
        model = Coach
        fields = '__all__' # Ambil semua field dari model
        widgets = {
            # Bisa tambahkan styling/class di sini jika perlu
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sport_branch': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'certifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'service_fee': forms.TextInput(attrs={'class': 'form-control'}),
        }