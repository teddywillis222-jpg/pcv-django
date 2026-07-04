from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

def formater_telephone_benin(numero):
    if not numero:
        return numero
        
    # Retire les espaces et tirets accidentels
    cleaned = str(numero).strip().replace(" ", "").replace("-", "")
    
    # S'il a déjà l'indicatif +229 ou 229, on le retire pour la validation
    if cleaned.startswith('+229'):
        cleaned = cleaned[4:]
    elif cleaned.startswith('229') and len(cleaned) == 13:
        cleaned = cleaned[3:]
        
    # Vérifie si la chaîne fait exactement 10 chiffres et ne contient que des nombres, et commence par 01.
    if len(cleaned) != 10 or not cleaned.isdigit() or not cleaned.startswith('01'):
        raise forms.ValidationError(f"Format invalide pour '{numero}'. Vous devez saisir exactement 10 chiffres commençant par 01 (ex: 01XXXXXXXX).")
        
    return f"+229{cleaned}"


from .models import Apprenant, Enfant, Parent, Profile
from .choices import ClassLevel, CourseMode, Localisation, Matiere

class DynamicSelectMultiple(forms.SelectMultiple):
    def get_context(self, name, value, attrs):
        if value:
            choices_list = list(self.choices)
            existing_vals = [str(c[0]) for c in choices_list]
            added = False
            for val in value:
                if str(val) not in existing_vals:
                    choices_list.append((val, val))
                    added = True
            if added:
                self.choices = choices_list
        return super().get_context(name, value, attrs)

class DynamicSelect(forms.Select):
    def get_context(self, name, value, attrs):
        if value:
            choices_list = list(self.choices)
            existing_vals = [str(c[0]) for c in choices_list]
            if str(value) not in existing_vals:
                choices_list.append((value, value))
                self.choices = choices_list
        return super().get_context(name, value, attrs)


class DynamicMultipleChoiceField(forms.MultipleChoiceField):
    widget = DynamicSelectMultiple

    def valid_value(self, value):
        return True

    def __init__(self, **kwargs):
        widget = kwargs.get('widget')
        if widget and isinstance(widget, forms.SelectMultiple) and not isinstance(widget, DynamicSelectMultiple):
            kwargs['widget'] = DynamicSelectMultiple(attrs=widget.attrs, choices=widget.choices)
        super().__init__(**kwargs)


class DynamicChoiceField(forms.ChoiceField):
    widget = DynamicSelect

    def valid_value(self, value):
        return True

    def __init__(self, **kwargs):
        widget = kwargs.get('widget')
        if widget and isinstance(widget, forms.Select) and not isinstance(widget, DynamicSelect):
            kwargs['widget'] = DynamicSelect(attrs=widget.attrs, choices=widget.choices)
        super().__init__(**kwargs)


class SignUpForm(forms.ModelForm):
    """Inscription : Nom complet, Rôle et Téléphone obligatoires."""
    
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={
            "placeholder": "votre.email@exemple.com",
            "required": True,
        })
    )

    telephone = forms.CharField(
        label="Numéro whatsapp (à vérifier)",
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "01XXXXXXXX",
            "class": "phone-input",
            "required": True,
            "type": "tel"
        })
    )

    role = forms.ChoiceField(
        label="Rôle",
        choices=Profile.ROLE_CHOICES,
        required=True,
        widget=forms.RadioSelect(attrs={"class": "role-radio-input"})
    )

    password = forms.CharField(
        label="Mot de passe",
        required=True,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Min 6 caractères",
            "minlength": "6",
            "required": True
        })
    )

    class Meta:
        model = User
        fields = ("email", "first_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].label = "Nom complet"
        self.fields["first_name"].required = True
        self.fields["first_name"].widget.attrs.update({
            "placeholder": "Ex: Jean Dupont",
            "required": True,
            "minlength": "2"
        })

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email", "")
        
        # Generate username automatically
        if email:
            base = email.split('@')[0][:20]
            base = re.sub(r'[^a-zA-Z0-9_]', '', base)
        else:
            base = "user"
            
        if not base:
            base = "user"

        username = base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1
            
        # We inject it into the instance later in save(), but we can also store it in cleaned_data
        cleaned_data["username"] = username
        return cleaned_data
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data.get("username")
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    def clean_telephone(self):
        numero = self.cleaned_data.get('telephone')
        formatted = formater_telephone_benin(numero)
        if Profile.objects.filter(telephone=formatted).exists():
            raise forms.ValidationError("Ce numéro WhatsApp est déjà lié à un compte. Veuillez vous connecter.")
        return formatted

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cet email est déjà utilisé. Veuillez vous connecter.")
            
        if email:
            disposable_domains = [
                'yopmail.com', '10minutemail.com', 'tempmail.com', 'mailinator.com',
                'guerrillamail.com', 'temp-mail.org', 'throwawaymail.com'
            ]
            domain = email.split('@')[-1].lower()
            if domain in disposable_domains:
                raise ValidationError("Les adresses email temporaires ne sont pas autorisées pour garantir la qualité de la plateforme.")
                
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 6:
            raise ValidationError("Le mot de passe doit contenir au moins 6 caractères.")
        
        if not re.search(r'[a-zA-Z]', password):
            raise ValidationError("Le mot de passe doit contenir au moins une lettre.")
        
        if not re.search(r'[0-9]', password):
            raise ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Le mot de passe doit contenir au moins un caractère spécial.")
        
        return password


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
    telephone = forms.CharField(
        label="Numéro WhatsApp",
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "01XXXXXXXX",
            "class": "phone-input",
            "required": True,
            "type": "tel"
        })
    )
    role = forms.ChoiceField(
        label="Rôle",
        choices=Profile.ROLE_CHOICES,
        required=True,
    )

    def clean_telephone(self):
        numero = self.cleaned_data.get('telephone')
        formatted = formater_telephone_benin(numero)
        if Profile.objects.filter(telephone=formatted).exists():
            raise forms.ValidationError("Ce numéro WhatsApp est déjà lié à un compte. Veuillez utiliser un autre numéro.")
        return formatted


class ParentForm(forms.ModelForm):
    quartier_ville = DynamicChoiceField(
        choices=Localisation.CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'pcv-multi-select'})
    )

    class Meta:
        model = Parent
        fields = ["nom", "quartier_ville"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nom'].widget.attrs['readonly'] = True
        self.fields['nom'].widget.attrs['class'] = 'bg-gray-100'


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
    objectifs_motivations = DynamicMultipleChoiceField(
        choices=ObjectifMotivation.CHOICES,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-input pcv-multi-select allow-multiple', 
            'placeholder': 'Quels sont les objectifs ?'
        }),
        required=False
    )
    difficultes_predefinies = DynamicMultipleChoiceField(
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
        self.fields["classe"].widget.attrs.update({'class': 'pcv-multi-select'})

    def clean_quartier_ville(self):
        ville = self.cleaned_data.get('quartier_ville')
        if ville:
            from core.utils import process_custom_choices
            return process_custom_choices('localisation', ville)
        return ville

    def clean_classe(self):
        classe = self.cleaned_data.get('classe')
        if classe:
            from core.utils import process_custom_choices
            return process_custom_choices('classe', classe)
        return classe

    def clean_matieres_predefinies(self):
        matieres = self.cleaned_data.get('matieres_predefinies', [])
        if matieres:
            from core.utils import process_custom_choices
            return process_custom_choices('matiere', matieres)
        return matieres

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

    telephone = forms.CharField(
        label="Numéro WhatsApp",
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Ex: 01XXXXXXXX",
            "class": "form-input",
            "required": True,
            "type": "tel"
        })
    )

    matieres_recherchees = DynamicMultipleChoiceField(
        choices=Matiere.get_choices(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-input pcv-multi-select allow-multiple', 
            'data-max-items': '5'
        }),
        required=False
    )
    
    objectifs_motivations = DynamicMultipleChoiceField(
        choices=ObjectifApprenant.CHOICES,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-input pcv-multi-select allow-multiple', 
            'placeholder': 'Quels sont vos objectifs ?'
        }),
        required=False
    )
    
    quartier_ville = DynamicChoiceField(
        choices=Localisation.CHOICES,
        widget=forms.Select(attrs={'class': 'pcv-multi-select'}),
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
            'classe': forms.Select(choices=ClassLevel.CHOICES),
            'preference_de_cours': forms.Select(choices=CourseMode.CHOICES),
            'description_difficultes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ex: Je ne comprends pas bien les théorèmes de maths, et je manque d\'organisation.'}),
            'nom': forms.TextInput(attrs={'placeholder': 'Ex: Jean Dupont'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        classe_choices = [("", "Ex : 4ème")] + list(self.fields["classe"].choices)[1:]
        self.fields["classe"].choices = classe_choices
        
        mode_choices = [("", "Ex : A domicile")] + list(self.fields["preference_de_cours"].choices)[1:]
        self.fields["preference_de_cours"].choices = mode_choices

        required_fields = ["nom", "classe", "quartier_ville", "preference_de_cours"]
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
        
        optional_fields = ["photo_de_profil", "matieres_recherchees", "objectifs_motivations", "description_difficultes"]
        for field_name in optional_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False

    def clean_telephone(self):
        numero = self.cleaned_data.get('telephone')
        if numero:
            return formater_telephone_benin(numero)
        return numero

    def clean_quartier_ville(self):
        ville = self.cleaned_data.get('quartier_ville')
        if ville:
            from core.utils import process_custom_choices
            return process_custom_choices('localisation', ville)
        return ville

    def clean_classe(self):
        classe = self.cleaned_data.get('classe')
        if classe:
            from core.utils import process_custom_choices
            return process_custom_choices('classe', classe)
        return classe

    def clean_matieres_recherchees(self):
        matieres = self.cleaned_data.get('matieres_recherchees', [])
        if matieres:
            from core.utils import process_custom_choices
            return process_custom_choices('matiere', matieres)
        return matieres

class EditEnfantForm(EnfantForm):
    numero_whatsapp = forms.CharField(
        label="Numéro WhatsApp du parent",
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Ex: 01XXXXXXXX",
            "class": "form-input",
            "required": True,
            "type": "tel"
        })
    )

    def clean_numero_whatsapp(self):
        numero = self.cleaned_data.get('numero_whatsapp')
        if numero:
            return formater_telephone_benin(numero)
        return numero

from .models import TeacherProfile
from .choices import SupportCategory

class TeacherProfileForm(forms.ModelForm):
    
    modes_de_cours = forms.MultipleChoiceField(
        choices=CourseMode.CHOICES, 
        required=True, 
        widget=forms.SelectMultiple(attrs={'class': 'pcv-multi-select allow-multiple', 'data-allow-create': 'false'})
    )
    classes_enseignees = DynamicMultipleChoiceField(
        choices=ClassLevel.CHOICES, 
        required=True, 
        widget=forms.SelectMultiple(attrs={
            'class': 'pcv-multi-select allow-multiple',
            'data-max-items': '15',
            'data-allow-create': 'false'
        })
    )
    ville_quartier = DynamicChoiceField(choices=Localisation.CHOICES, required=True, widget=forms.Select(attrs={'class': 'pcv-multi-select'}))
    categories_de_soutien = forms.MultipleChoiceField(
        choices=SupportCategory.CHOICES,
        required=True,
        widget=forms.SelectMultiple(attrs={
            'class': 'pcv-multi-select allow-multiple', 
            'placeholder': 'Catégories (Max 4)',
            'data-max-items': '4',
            'data-allow-create': 'false'
        })
    )
    telephone_whatsapp = forms.CharField(
        label="Numéro WhatsApp",
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Ex: 01XXXXXXXX",
            "class": "form-input",
            "required": True,
            "type": "tel"
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
            "annees_d_experience",
            "photo_de_profil",
            "fichier_cni",
            "essai_gratuit_actif",
        ]
        widgets = {
            'photo_de_profil': forms.FileInput(),
            'fichier_cni': forms.FileInput(),
        }

    def __init__(self, *args, **kwargs):
        is_editing = kwargs.pop('is_editing', False)
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs["readonly"] = True
        self.fields["nom"].widget.attrs["readonly"] = True

        if self.instance and self.instance.pk:
            self.initial['nom'] = f"{self.instance.prenom} {self.instance.nom}".strip()
            
        self.fields["nom"].label = "Nom Complet"
        
        if "annees_d_experience" in self.fields:
            self.fields["annees_d_experience"].required = is_editing

        if is_editing:
            for field_name in ["presentation", "methodologie"]:
                if field_name in self.fields:
                    self.fields[field_name].required = True
                    if field_name in ["presentation", "methodologie"]:
                        self.fields[field_name].widget.attrs["minlength"] = "800"
            if "tarif_horaire" in self.fields:
                self.fields["tarif_horaire"].required = False

        if self.instance and self.instance.pk and self.instance.matiere_enseignee:
            if isinstance(self.instance.matiere_enseignee, str):
                self.initial['matiere_enseignee'] = [m.strip() for m in self.instance.matiere_enseignee.split(',')]
        
        for field_name in ["email", "nom", "telephone_whatsapp", "categories_de_soutien", "matiere_enseignee", "ville_quartier", "photo_de_profil", "fichier_cni"]:
            if field_name in self.fields:
                if field_name == "photo_de_profil" and self.instance and getattr(self.instance, "photo_de_profil", None):
                    self.fields[field_name].required = False
                elif field_name == "fichier_cni" and self.instance and getattr(self.instance, "fichier_cni", None):
                    self.fields[field_name].required = False
                else:
                    self.fields[field_name].required = True

    def clean_telephone_whatsapp(self):
        numero = self.cleaned_data.get('telephone_whatsapp')
        if numero:
            return formater_telephone_benin(numero)
        return numero

    def clean_nom(self):
        if self.instance and self.instance.pk:
            return self.instance.nom
        return self.cleaned_data.get('nom')

    def clean_ville_quartier(self):
        ville = self.cleaned_data.get('ville_quartier')
        if ville:
            from core.utils import process_custom_choices
            return process_custom_choices('localisation', ville)
        return ville

    def clean_matiere_enseignee(self):
        matieres = self.cleaned_data.get('matiere_enseignee')
        if isinstance(matieres, list):
            if len(matieres) > 3:
                raise forms.ValidationError("Vous ne pouvez sélectionner que 3 matières maximum.")
            from core.utils import process_custom_choices
            processed = process_custom_choices('matiere', matieres)
            return ", ".join(processed)
        return matieres

    def clean_classes_enseignees(self):
        classes = self.cleaned_data.get('classes_enseignees')
        if isinstance(classes, list):
            if len(classes) > 15:
                raise forms.ValidationError("Vous ne pouvez sélectionner que 15 classes maximum.")
            # Les codes sont retournés tels quels (en majuscules) pour correspondre à ClassLevel.CHOICES
            return classes
        return classes

    def clean_categories_de_soutien(self):
        categories = self.cleaned_data.get('categories_de_soutien')
        if isinstance(categories, list) and len(categories) > 4:
            raise forms.ValidationError("Vous ne pouvez sélectionner que 4 catégories maximum.")
        return categories

    def clean(self):
        cleaned_data = super().clean()
        classes = cleaned_data.get('classes_enseignees', [])
        
        tarifs = {}
        tarif_horaire_global = cleaned_data.get('tarif_horaire')
        
        if isinstance(classes, list):
            classes_lower = [str(c).lower() for c in classes]
            for key, val in self.data.items():
                if key.startswith('tarif_classe_'):
                    class_code = key.replace('tarif_classe_', '')
                    if class_code.lower() in classes_lower:
                        if val and val.isdigit():
                            tarifs[class_code] = int(val)
                        elif tarif_horaire_global:
                            tarifs[class_code] = int(tarif_horaire_global)
                    
        self.cleaned_tarifs_par_classe = tarifs
        return cleaned_data
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if hasattr(self, 'cleaned_tarifs_par_classe'):
            instance.tarifs_par_classe = self.cleaned_tarifs_par_classe
        if commit:
            instance.save()
            self.save_m2m()
        return instance


from .models import ProfessorAnnouncement

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = ProfessorAnnouncement
        fields = ['title', 'target_audience', 'message', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500',
                'placeholder': 'Titre de l\'annonce',
                'id': 'id_title'
            }),
            'target_audience': forms.Select(attrs={
                'class': 'w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500',
                'id': 'id_target_audience'
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
            'target_audience': 'Définissez qui pourra voir cette annonce sur son tableau de bord.',
            'message': 'Le contenu détaillé de votre annonce.',
            'is_active': 'Cochez pour rendre cette annonce visible aux utilisateurs cibles immédiatement.'
        }

class TeacherVideoPresentationForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['video_presentation']
        widgets = {
            'video_presentation': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'video/*',
            })
        }
