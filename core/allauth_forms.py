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

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Liste basique de domaines jetables courants à bloquer
            disposable_domains = [
                'yopmail.com', '10minutemail.com', 'tempmail.com', 'mailinator.com',
                'guerrillamail.com', 'temp-mail.org', 'throwawaymail.com'
            ]
            domain = email.split('@')[-1].lower()
            if domain in disposable_domains:
                raise forms.ValidationError(
                    "Les adresses email temporaires ne sont pas autorisées pour garantir la qualité de la plateforme."
                )
        return email
