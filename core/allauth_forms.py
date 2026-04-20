from django import forms
from core.models import Profile

class CustomSignupForm(forms.Form):
    first_name = forms.CharField(max_length=150, label='Nom complet', widget=forms.TextInput(attrs={'placeholder': 'Votre nom complet'}))
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, label='Rôle')

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.save()
        
        # We save the role in the session or create the profile directly here, 
        # but creating it here is best.
        Profile.objects.get_or_create(user=user, defaults={'role': self.cleaned_data['role']})
