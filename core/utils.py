import string

def process_custom_choices(category, values):
    """
    Nettoie et sauvegarde de nouvelles options (matières, localisations, classes) dans CustomChoice.
    - category: 'matiere', 'localisation', ou 'classe'
    - values: une chaîne (ex: "Maths, Physique") ou une liste de chaînes
    Retourne la liste/chaîne nettoyée.
    """
    if not values:
        return values

    from django.apps import apps
    CustomChoice = apps.get_model('core', 'CustomChoice')

    def clean_val(val):
        # Retire les espaces multiples et capitalize la première lettre de chaque mot, 
        # mais on peut aussi juste strip() et capitalize() la chaîne entière.
        # Ex: "  anglais  canada " -> "Anglais Canada"
        val = ' '.join(val.split())
        return val.capitalize() if val else ""

    processed = []
    
    if isinstance(values, str):
        parts = [s.strip() for s in values.split(',')]
        is_string = True
    else:
        parts = values
        is_string = False

    seen_in_request = set()
    
    for p in parts:
        if not isinstance(p, str):
            processed.append(p)
            continue
            
        c_val = clean_val(p)
        if not c_val or c_val.lower() in seen_in_request:
            continue
            
        seen_in_request.add(c_val.lower())
        processed.append(c_val)
        
        # Sauvegarde en base si n'existe pas
        # Utilisation de get_or_create (insensible à la casse si on cherche manuellement)
        # Mais pour éviter les race conditions avec iexact, on utilise iexact
        exists = CustomChoice.objects.filter(category=category, value__iexact=c_val).exists()
        if not exists:
            try:
                CustomChoice.objects.create(category=category, value=c_val)
            except Exception:
                # Ignorer si une autre requête a inséré en même temps (UniqueConstraint)
                pass

    if is_string:
        return ", ".join(processed)
    return processed
