from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

from .models import Apprenant, Enfant, Parent, Profile
from .choices import ClassLevel, CourseMode, Localisation, Matiere

class DynamicMultipleChoiceField(forms.MultipleChoiceField):
    def valid_value(self, value):
        return True


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
                "placeholder": "Min 6 caractères (lettre, chiffre et spécial)",
                "minlength": "6"
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
        if len(password) < 6:
            raise ValidationError("Le mot de passe doit contenir au moins 6 caractères.")
        
        if not re.search(r'[a-zA-Z]', password):
            raise ValidationError("Le mot de passe doit contenir au moins une lettre.")
        
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
        widget=forms.TextInput(attrs={
            "placeholder": "Votre identifiant",
            "class": "auth-input",
            "required": True
        }),
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Votre mot de passe",
            "class": "auth-input",
            "required": True
        }),
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
        choices=Localisation.CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'pcv-multi-select'})
    )

    class Meta:
        model = Parent
        fields = ["nom", "numero_whatsapp", "quartier_ville"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nom'].widget.attrs['readonly'] = True
        self.fields['nom'].widget.attrs['class'] = 'bg-gray-100'
        self.fields['numero_whatsapp'].required = True
        self.fields['numero_whatsapp'].required = True
        self.fields['numero_whatsapp'].widget.attrs.update({"placeholder": "Ex: 01 23 45 67 89", "class": "phone-input"})


class EnfantForm(forms.ModelForm):
    from .choices import ObjectifMotivation
    
    DIFFICULTES_CHOICES = [
        ("Bases fragiles non acquises", "Bases fragiles non acquises"),
        ("Manque de concentration", "Manque de concentration"),
        ("Problèmes de mémorisation", "Problèmes de mémorisation"),
        ("Manque d'organisation", "Manque d'organisation / Méthodologie"),
        ("Baisse de motivation", "Baisse de motivation / Confiance"),
    ]

    matieres_predefinies = DynamicMultipleChoiceField(
        label="Matières nécessitant appui (Max 5)",
        required=False,
        choices=Matiere.get_choices(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-input pcv-multi-select allow-multiple', 
            'placeholder': 'Ex : Mathématiques',
            'data-max-items': '5'
        })
    )
    objectifs_motivations = forms.MultipleChoiceField(
        choices=ObjectifMotivation.CHOICES,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-input pcv-multi-select allow-multiple', 
            'placeholder': 'Quels sont les objectifs ?'
        }),
        required=False
    )
    difficultes_predefinies = forms.MultipleChoiceField(
        choices=DIFFICULTES_CHOICES,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-input pcv-multi-select allow-multiple', 
            'placeholder': 'Quelles difficultés ?'
        }),
        required=False
    )

    class Meta:
        model = Enfant
        fields = [
            "prenom",
            "classe",
            "quartier_ville",
            "mode_de_cours",
            "matieres_predefinies",
            "objectifs_motivations",
            "difficultes_predefinies",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["prenom"].widget.attrs.update({"placeholder": "Ex: Alexandre"})
        
        # Ajout des placeholders natifs Django par le biais de choices
        classe_choices = [("", "Ex : 4ème")] + list(self.fields["classe"].choices)[1:]
        self.fields["classe"].choices = classe_choices
        
        mode_choices = [("", "Ex : A domicile")] + list(self.fields["mode_de_cours"].choices)[1:]
        self.fields["mode_de_cours"].choices = mode_choices

        for field in ["prenom", "classe", "quartier_ville", "mode_de_cours"]:
            self.fields[field].required = True
            
        self.fields["quartier_ville"].widget = forms.Select(choices=Localisation.CHOICES, attrs={'class': 'pcv-multi-select'})
        self.fields["mode_de_cours"].widget.attrs.update({'class': 'pcv-multi-select'})

    def clean(self):
        cleaned_data = super().clean()
        matieres = cleaned_data.get("matieres_predefinies", [])
        total_mat = len(matieres)
        
        if total_mat == 0:
            self.add_error("matieres_predefinies", "Sélectionnez au moins une matière.")
        if total_mat > 5:
            self.add_error("matieres_predefinies", "5 matières maximum autorisées.")
            
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        matieres = list(self.cleaned_data.get('matieres_predefinies', []))
        
        instance.matieres = matieres[:5]
        
        objectifs = self.cleaned_data.get('objectifs_motivations', [])
        
        objectifs_str = ", ".join(objectifs)
        difficultes = ", ".join(self.cleaned_data.get('difficultes_predefinies', []))
        instance.objectif_principal = f"OBJECTIFS: {objectifs_str}\nDIFFICULTÉS: {difficultes}"
        
        if commit:
            instance.save()
        return instance


class ApprenantCreateProfileForm(forms.ModelForm):
    """Formulaire en 2 étapes pour le profil apprenant."""
    from .choices import ObjectifApprenant

    matieres_recherchees = DynamicMultipleChoiceField(
        choices=Matiere.get_choices(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-input pcv-multi-select allow-multiple', 
            'style': 'height: 52px;',
            'data-max-items': '5'
        }),
        required=False
    )
    
    objectifs_motivations = forms.MultipleChoiceField(
        choices=ObjectifApprenant.CHOICES,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-input pcv-multi-select allow-multiple', 
            'placeholder': 'Quels sont vos objectifs ?'
        }),
        required=False
    )
    
    quartier_ville = forms.ChoiceField(
        choices=Localisation.CHOICES,
        widget=forms.Select(attrs={'style': 'height: 52px;', 'class': 'pcv-multi-select'}),
        required=True
    )

    class Meta:
        model = Apprenant
        fields = [
            "nom",
            "telephone",
            "photo_de_profil",
            "classe",
            "matieres_recherchees",
            "objectifs_motivations",
            "description_difficultes",
            "quartier_ville",
            "preference_de_cours",
        ]
        widgets = {
            'classe': forms.Select(choices=ClassLevel.CHOICES, attrs={'style': 'height: 52px;'}),
            'preference_de_cours': forms.Select(choices=CourseMode.CHOICES, attrs={'style': 'height: 52px;'}),
            'description_difficultes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ex: Je ne comprends pas bien les théorèmes de maths, et je manque d\'organisation.'}),
            'nom': forms.TextInput(attrs={'placeholder': 'Ex: Jean Dupont', 'style': 'height: 52px;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        classe_choices = [("", "Ex : 4ème")] + list(self.fields["classe"].choices)[1:]
        self.fields["classe"].choices = classe_choices
        
        mode_choices = [("", "Ex : A domicile")] + list(self.fields["preference_de_cours"].choices)[1:]
        self.fields["preference_de_cours"].choices = mode_choices

        required_fields = ["nom", "telephone", "classe", "quartier_ville", "preference_de_cours"]
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
        
        optional_fields = ["photo_de_profil", "matieres_recherchees", "objectifs_motivations", "description_difficultes"]
        for field_name in optional_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False
        
        if "telephone" in self.fields:
            self.fields["telephone"].widget.attrs.update({"class": "phone-input", "placeholder": "Ex: 01 23 45 67 89", "style": "height: 52px;"})


from .models import TeacherProfile
from .choices import SupportCategory

class TeacherProfileForm(forms.ModelForm):
    
    modes_de_cours = forms.MultipleChoiceField(
        choices=CourseMode.CHOICES, 
        required=False, 
        widget=forms.SelectMultiple(attrs={'class': 'pcv-multi-select allow-multiple'})
    )
    classes_enseignees = forms.MultipleChoiceField(
        choices=ClassLevel.CHOICES, 
        required=False, 
        widget=forms.SelectMultiple(attrs={
            'class': 'pcv-multi-select allow-multiple',
            'data-max-items': '3'
        })
    )
    ville_quartier = forms.ChoiceField(choices=Localisation.CHOICES, required=True, widget=forms.Select(attrs={'class': 'pcv-multi-select'}))
    categories_de_soutien = DynamicMultipleChoiceField(
        choices=SupportCategory.CHOICES,
        required=True,
        widget=forms.SelectMultiple(attrs={
            'class': 'pcv-multi-select allow-multiple', 
            'placeholder': 'Catégories (Max 4)',
            'data-max-items': '4'
        })
    )
    matiere_enseignee = DynamicMultipleChoiceField(
        choices=Matiere.get_choices(),
        required=True,
        widget=forms.SelectMultiple(attrs={
            'class': 'pcv-multi-select allow-multiple', 
            'placeholder': 'Matières enseignées (Max 3)',
            'data-max-items': '3'
        })
    )
    essai_gratuit_actif = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'pcv-checkbox'})
    )
    
    class Meta:
        model = TeacherProfile
        fields = [
            "email",
            "nom",
            "telephone_whatsapp",
            "ville_quartier",
            "matiere_enseignee",
            "classes_enseignees",
            "categories_de_soutien",
            "modes_de_cours",
            "presentation",
            "methodologie",
            "tarif_horaire",
            "photo_de_profil",
            "fichier_cni",
            "autorisation_publicitaire",
            "essai_gratuit_actif",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs["readonly"] = True
        self.fields["nom"].widget.attrs["readonly"] = True

        if self.instance and self.instance.pk:
            if "fichier_cni" in self.fields:
                del self.fields["fichier_cni"]
        self.fields["nom"].label = "Nom Complet"
        
        self.fields["telephone_whatsapp"].widget.attrs.update({"placeholder": "01 XX XX XX XX"})

        if self.instance and self.instance.pk and self.instance.matiere_enseignee:
            if isinstance(self.instance.matiere_enseignee, str):
                self.initial['matiere_enseignee'] = [m.strip() for m in self.instance.matiere_enseignee.split(',')]
        
        for field_name in ["email", "nom", "telephone_whatsapp", "categories_de_soutien", "matiere_enseignee", "ville_quartier", "photo_de_profil", "fichier_cni"]:
            if field_name in self.fields:
                if field_name == "photo_de_profil" and self.instance and self.instance.photo_de_profil:
                    self.fields[field_name].required = False
                else:
                    self.fields[field_name].required = True
                if field_name == "telephone_whatsapp":
                    self.fields[field_name].widget.attrs.update({"class": "phone-input"})

    def clean_matiere_enseignee(self):
        matieres = self.cleaned_data.get('matiere_enseignee')
        if isinstance(matieres, list):
            if len(matieres) > 3:
                raise forms.ValidationError("Vous ne pouvez sélectionner que 3 matières maximum.")
            return ", ".join(matieres)
        return matieres

    def clean_classes_enseignees(self):
        classes = self.cleaned_data.get('classes_enseignees')
        if isinstance(classes, list) and len(classes) > 3:
            raise forms.ValidationError("Vous ne pouvez sélectionner que 3 classes maximum.")
        return classes

    def clean_categories_de_soutien(self):
        categories = self.cleaned_data.get('categories_de_soutien')
        if isinstance(categories, list) and len(categories) > 4:
            raise forms.ValidationError("Vous ne pouvez sélectionner que 4 catégories maximum.")
        return categories


from .models import ProfessorAnnouncement

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = ProfessorAnnouncement
        fields = ['title', 'message', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500',
                'placeholder': 'Titre de l\'annonce',
                'id': 'id_title'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500',
                'placeholder': 'Message détaillé de l\'annonce...',
                'rows': 4,
                'id': 'id_message'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-green-600 focus:ring-green-500 border-gray-300 rounded'
            }),
        }
        help_texts = {
            'title': 'Apparaîtra en gras en haut de la carte.',
            'message': 'Le contenu détaillé de votre annonce.',
            'is_active': 'Cochez pour rendre cette annonce visible aux professeurs immédiatement.'
        }
