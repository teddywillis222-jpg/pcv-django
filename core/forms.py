from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

from .models import Apprenant, Enfant, Parent, Profile


class SignUpForm(UserCreationForm):
    """Inscription : Nom complet et Rôle obligatoires."""
    
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={
            "placeholder": "votre.email@exemple.com",
            "required": True,
        })
    )

    role = forms.ChoiceField(
        label="Rôle",
        choices=Profile.ROLE_CHOICES,
        required=True,
        widget=forms.RadioSelect(attrs={"class": "role-radio-input"})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].label = "Nom complet"
        self.fields["first_name"].required = True
        self.fields["first_name"].widget.attrs.update({
            "placeholder": "Ex: Jean Dupont",
            "required": True,
            "minlength": "2"
        })
        # Username will be hidden in the template, we just need it minimally required.
        self.fields["username"].label = "Nom d'utilisateur (caché)"
        self.fields["username"].required = False
        
        # Make sure password fields have good labels and security requirements
        if "password1" in self.fields:
            self.fields["password1"].label = "Mot de passe"
            self.fields["password1"].widget.attrs.update({
                "placeholder": "Min 8 caractères, 1 majuscule, 1 chiffre",
                "minlength": "8"
            })
        if "password2" in self.fields:
            self.fields["password2"].label = "Confirmer le mot de passe"
            self.fields["password2"].widget.attrs.update({"placeholder": "Répétez le mot de passe"})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cet email est déjà utilisé. Veuillez vous connecter.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Le mot de passe doit contenir au moins une majuscule.")
        
        if not re.search(r'[0-9]', password):
            raise ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Le mot de passe doit contenir au moins un caractère spécial.")
        
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

    def clean_first_name(self):
        nom = self.cleaned_data.get("first_name", "").strip()
        if not nom:
            raise forms.ValidationError("Le nom complet est obligatoire.")
        if len(nom) < 2:
            raise forms.ValidationError("Le nom complet doit contenir au moins 2 caractères")
        return nom
        
    def clean_role(self):
        role = self.cleaned_data.get("role")
        if not role:
            raise forms.ValidationError("Veuillez sélectionner un rôle.")
        return role

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        if email and not cleaned_data.get("username"):
            # Auto generate username from email
            base_username = email.split('@')[0]
            import random
            cleaned_data["username"] = f"{base_username}{random.randint(1000, 9999)}"
        return cleaned_data


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Nom d'utilisateur ou email",
        widget=forms.TextInput(attrs={"placeholder": "Nom d'utilisateur ou email"}),
    )


class FinalisationCompteForm(forms.Form):
    """Formulaire pour finaliser le compte (après Google Login sans rôle)."""

    nom_complet = forms.CharField(
        label="Nom complet",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Votre nom complet"}),
    )
    role = forms.ChoiceField(
        label="Rôle",
        choices=Profile.ROLE_CHOICES,
        required=True,
    )


class ParentForm(forms.ModelForm):
    quartier_ville = forms.ChoiceField(
        choices=[
            ("", "Sélectionnez votre quartier-ville"),
            ("Cotonou - Akpakpa", "Cotonou - Akpakpa"),
            ("Cotonou - Haie Vive", "Cotonou - Haie Vive"),
            ("Cotonou - Fidjrossè", "Cotonou - Fidjrossè"),
            ("Cotonou - Cadjèhoun", "Cotonou - Cadjèhoun"),
            ("Cotonou - Agla", "Cotonou - Agla"),
            ("Abomey-Calavi - Arimbo", "Abomey-Calavi - Arimbo"),
            ("Abomey-Calavi - Zoca", "Abomey-Calavi - Zoca"),
            ("Abomey-Calavi - Godomey", "Abomey-Calavi - Godomey"),
            ("Porto-Novo - Centre", "Porto-Novo - Centre"),
            ("Autre", "Autre (à préciser ultérieurement)")
        ],
        required=True
    )

    class Meta:
        model = Parent
        fields = ["nom", "numero_whatsapp", "quartier_ville", "photo_profil"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nom'].widget.attrs['readonly'] = True
        self.fields['nom'].widget.attrs['class'] = 'bg-gray-100'
        self.fields['numero_whatsapp'].required = True
        self.fields['numero_whatsapp'].widget.attrs.update({"placeholder": "Ex: 01 23 45 67 89"})
        self.fields['photo_profil'].widget.attrs.update({"accept": "image/*"})


class EnfantForm(forms.ModelForm):
    from .choices import ObjectifMotivation
    
    MATIERES_CHOICES = [
        ("Mathématiques", "Mathématiques"),
        ("Physique-Chimie", "Physique-Chimie (PCT)"),
        ("SVT", "SVT"),
        ("Français", "Français"),
        ("Anglais", "Anglais"),
        ("Philosophie", "Philosophie"),
        ("Histoire-Géo", "Histoire-Géographie"),
    ]
    
    DIFFICULTES_CHOICES = [
        ("Bases fragiles non acquises", "Bases fragiles non acquises"),
        ("Manque de concentration", "Manque de concentration"),
        ("Problèmes de mémorisation", "Problèmes de mémorisation"),
        ("Manque d'organisation", "Manque d'organisation / Méthodologie"),
        ("Baisse de motivation", "Baisse de motivation / Confiance"),
    ]

    matieres_predefinies = forms.MultipleChoiceField(
        label="Matières nécessitant appui (Max 5)",
        required=False,
        choices=MATIERES_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )
    matieres_autre = forms.CharField(
        label="Autre(s) matière(s)",
        required=False,
        widget=forms.HiddenInput() # Rendu caché, on gère l'UI custom
    )
    difficultes_predefinies = forms.MultipleChoiceField(
        label="Difficultés principales observées",
        required=True,
        choices=DIFFICULTES_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )
    objectifs_motivations = forms.MultipleChoiceField(
        label="Objectifs & Motivations",
        required=True,
        choices=ObjectifMotivation.CHOICES,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Enfant
        fields = [
            "prenom",
            "classe",
            "quartier_ville",
            "mode_de_cours",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["prenom"].widget.attrs.update({"placeholder": "Ex: Alexandre"})
        
        # Ajout des placeholders natifs Django par le biais de choices
        classe_choices = [("", "Sélectionnez sa classe courante...")] + list(self.fields["classe"].choices)[1:]
        self.fields["classe"].choices = classe_choices
        
        mode_choices = [("", "Sélectionnez le mode de cours préféré...")] + list(self.fields["mode_de_cours"].choices)[1:]
        self.fields["mode_de_cours"].choices = mode_choices

        for field in ["prenom", "classe", "quartier_ville", "mode_de_cours"]:
            self.fields[field].required = True
            
        self.fields["quartier_ville"].widget = forms.Select(choices=[
            ("", "Sélectionnez un quartier-ville"),
            ("Cotonou - Akpakpa", "Cotonou - Akpakpa"),
            ("Cotonou - Haie Vive", "Cotonou - Haie Vive"),
            ("Cotonou - Fidjrossè", "Cotonou - Fidjrossè"),
            ("Cotonou - Cadjèhoun", "Cotonou - Cadjèhoun"),
            ("Cotonou - Agla", "Cotonou - Agla"),
            ("Abomey-Calavi - Arimbo", "Abomey-Calavi - Arimbo"),
            ("Abomey-Calavi - Zoca", "Abomey-Calavi - Zoca"),
            ("Abomey-Calavi - Godomey", "Abomey-Calavi - Godomey"),
            ("Porto-Novo - Centre", "Porto-Novo - Centre"),
            ("Autre", "Autre")
        ])

    def clean(self):
        cleaned_data = super().clean()
        matieres = cleaned_data.get("matieres_predefinies", [])
        autre = cleaned_data.get("matieres_autre", "")
        total_mat = len(matieres) + (1 if autre.strip() else 0)
        
        if total_mat == 0:
            self.add_error("matieres_predefinies", "Sélectionnez au moins une matière.")
        if total_mat > 5:
            self.add_error("matieres_predefinies", "5 matières maximum autorisées.")
            
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        matieres = list(self.cleaned_data.get('matieres_predefinies', []))
        autre = self.cleaned_data.get('matieres_autre', '').strip()
        if autre:
            for m in autre.split(','):
                if m.strip() and m.strip() not in matieres:
                    matieres.append(m.strip())
        instance.matieres = matieres[:5]
        
        objectifs = ", ".join(self.cleaned_data.get('objectifs_motivations', []))
        difficultes = ", ".join(self.cleaned_data.get('difficultes_predefinies', []))
        instance.objectif_principal = f"OBJECTIFS: {objectifs}\nDIFFICULTÉS: {difficultes}"
        
        if commit:
            instance.save()
        return instance


class ApprenantCreateProfileForm(forms.ModelForm):
    """Tous les champs obligatoires sauf photo_de_profil."""

    class Meta:
        model = Apprenant
        fields = [
            "nom",
            "email_apprenant",
            "telephone",
            "photo_de_profil",
            "niveau",
            "classe",
            "matieres_recherchees",
            "objectifs_motivations",
            "description_difficultes",
            "habitudes_de_travail",
            "quartier_ville",
            "preference_de_cours",
            "disponibilites",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ["nom", "email_apprenant", "telephone", "niveau", "classe", "quartier_ville", "preference_de_cours"]:
            if field_name in self.fields:
                self.fields[field_name].required = True


from .models import TeacherProfile

from .choices import CourseMode, ClassLevel

class TeacherProfileForm(forms.ModelForm):
    VILLE_QUARTIER_CHOICES = [
        ("", "Sélectionnez votre zone de résidence"),
        ("Cotonou - Haie Vive", "Cotonou - Haie Vive"),
        ("Cotonou - Fidjrossè", "Cotonou - Fidjrossè"),
        ("Cotonou - Akpakpa", "Cotonou - Akpakpa"),
        ("Cotonou - Cadjèhoun", "Cotonou - Cadjèhoun"),
        ("Cotonou - Agla", "Cotonou - Agla"),
        ("Abomey-Calavi - Arsat", "Abomey-Calavi - Arsat"),
        ("Abomey-Calavi - Zoca", "Abomey-Calavi - Zoca"),
        ("Abomey-Calavi - Godomey", "Abomey-Calavi - Godomey"),
        ("Porto-Novo", "Porto-Novo"),
        ("Autre Quartier", "Autre Quartier"),
    ]
    
    modes_de_cours = forms.MultipleChoiceField(choices=CourseMode.CHOICES, required=False)
    classes_enseignees = forms.MultipleChoiceField(choices=ClassLevel.CHOICES, required=False)
    ville_quartier = forms.ChoiceField(choices=VILLE_QUARTIER_CHOICES, required=True)
    
    class Meta:
        model = TeacherProfile
        fields = [
            "email",
            "nom",
            "telephone_whatsapp",
            "ville_quartier",
            "matiere_enseignee",
            "classes_enseignees",
            "categorie_de_soutien",
            "modes_de_cours",
            "photo_de_profil",
            "fichier_cni",
            "autorisation_publicitaire",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs["readonly"] = True
        self.fields["nom"].widget.attrs["readonly"] = True
        self.fields["nom"].label = "Nom Complet"
        
        self.fields["matiere_enseignee"].widget = forms.HiddenInput()
        self.fields["categorie_de_soutien"].empty_label = "Choisissez une catégorie principale..."
        
        for field_name in ["email", "nom", "telephone_whatsapp", "categorie_de_soutien", "matiere_enseignee", "ville_quartier", "photo_de_profil", "fichier_cni"]:
            if field_name in self.fields:
                self.fields[field_name].required = True
