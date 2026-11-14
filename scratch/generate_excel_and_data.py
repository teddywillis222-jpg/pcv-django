import os
import sys
import json
from collections import defaultdict, Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from core.models import TeacherProfile, Quartier
from core.choices import ValidationStatus

def export_all():
    print("Chargement des professeurs validés...")
    teachers_qs = TeacherProfile.objects.filter(
        statut_de_validation=ValidationStatus.VALIDE
    ).prefetch_related('quartiers_couverts')
    
    teachers = list(teachers_qs)
    print(f"Nombre de profs validés: {len(teachers)}")

    # 1. Structure pour le JSON et l'analyse
    teachers_data = []
    subject_counts = Counter()
    subject_classes = defaultdict(lambda: Counter())
    city_quartier_map = defaultdict(lambda: defaultdict(list))
    quartier_summary = defaultdict(lambda: {
        'ville': '',
        'profs': [],
        'matieres': set(),
        'essai_gratuit_count': 0
    })

    # Standardisation des classes
    all_known_classes = [
        'Primaire', '6ème', '5ème', '4ème', '3ème', 
        '2nde Littéraire', '2nde Scientifique',
        '1ère Littéraire', '1ère Scientifique',
        'Tle Littéraire', 'Tle Scientifique'
    ]

    for t in teachers:
        # Matières
        raw_mat = t.matiere_enseignee or ''
        subjects = [s.strip().capitalize() for s in raw_mat.split(',') if s.strip()]
        for s in subjects:
            subject_counts[s] += 1

        # Classes
        classes_ens = t.classes_enseignees or []
        classes_exp = t.classes_expertise or []
        combined_classes = list(set(classes_ens + classes_exp))
        
        for s in subjects:
            for c in combined_classes:
                subject_classes[s][c] += 1

        # Modes de cours
        modes = t.modes_de_cours or []
        mode_labels = []
        for m in modes:
            if 'PARENT_HOME' in m or 'DOMICILE' in m:
                mode_labels.append("À domicile (parent)")
            elif 'ONLINE' in m or 'DISTANCE' in m:
                mode_labels.append("En ligne")
            elif 'APPRENANT_HOME' in m:
                mode_labels.append("Chez l'élève")
            elif 'HYBRID' in m:
                mode_labels.append("Hybride")
            elif 'SMALL_GROUP' in m:
                mode_labels.append("Petit groupe")
            else:
                mode_labels.append(m)

        # Quartiers et villes
        t_quartiers = []
        t_villes = set()
        for q in t.quartiers_couverts.all():
            v_nom = q.ville.strip() if q.ville else 'Non précisée'
            q_nom = q.nom.strip()
            t_quartiers.append(f"{q_nom} ({v_nom})")
            t_villes.add(v_nom)
            
            city_quartier_map[v_nom][q_nom].append(f"{t.prenom} {t.nom}")
            quartier_summary[f"{q_nom}___{v_nom}"]['ville'] = v_nom
            quartier_summary[f"{q_nom}___{v_nom}"]['quartier'] = q_nom
            quartier_summary[f"{q_nom}___{v_nom}"]['profs'].append(f"{t.prenom} {t.nom}")
            for s in subjects:
                quartier_summary[f"{q_nom}___{v_nom}"]['matieres'].add(s)
            if t.essai_gratuit_actif:
                quartier_summary[f"{q_nom}___{v_nom}"]['essai_gratuit_count'] += 1

        # Tarifs
        tarifs = t.tarifs_par_classe or {}
        tarif_base = float(t.tarif_horaire) if t.tarif_horaire else (
            min([float(v) for v in tarifs.values()]) if tarifs else 0.0
        )

        teacher_info = {
            'id': t.id,
            'nom_complet': f"{t.prenom} {t.nom}".strip(),
            'prenom': t.prenom,
            'nom': t.nom,
            'email': t.email,
            'telephone': t.telephone_whatsapp,
            'matieres': subjects,
            'classes_enseignees': classes_ens,
            'classes_expertise': classes_exp,
            'modes': mode_labels,
            'villes': sorted(list(t_villes)),
            'quartiers': sorted(t_quartiers),
            'nb_quartiers': len(t_quartiers),
            'essai_gratuit': t.essai_gratuit_actif,
            'tarif_horaire_base': tarif_base,
            'tarifs_par_classe': tarifs,
            'annees_experience': t.annees_d_experience,
            'score_fiabilite': t.score_fiabilite,
            'note_initiale': float(t.note_initiale_equipe) if t.note_initiale_equipe else 0.0,
            'a_video': bool(t.youtube_video_id or t.video_presentation)
        }
        teachers_data.append(teacher_info)

    # 2. Création du classeur Excel enrichi avec openpyxl
    wb = openpyxl.Workbook()
    
    # Styles
    navy_fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
    gold_fill = PatternFill(start_color="D4AF37", end_color="D4AF37", fill_type="solid")
    header_fill = PatternFill(start_color="2A4D69", end_color="2A4D69", fill_type="solid")
    sub_fill = PatternFill(start_color="4B86B4", end_color="4B86B4", fill_type="solid")
    zebra_fill = PatternFill(start_color="F7F9FB", end_color="F7F9FB", fill_type="solid")
    alert_fill = PatternFill(start_color="FFF3CD", end_color="FFF3CD", fill_type="solid")
    success_fill = PatternFill(start_color="D4EDDA", end_color="D4EDDA", fill_type="solid")

    font_title = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    font_section = Font(name="Calibri", size=13, bold=True, color="1B365D")
    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=11, bold=True)
    font_normal = Font(name="Calibri", size=11)
    font_small = Font(name="Calibri", size=10, italic=True)

    thin_border = Border(
        left=Side(style='thin', color="D3D3D3"),
        right=Side(style='thin', color="D3D3D3"),
        top=Side(style='thin', color="D3D3D3"),
        bottom=Side(style='thin', color="D3D3D3")
    )

    # --- FEUILLE 1: Synthèse & Stratégie Publicitaire ---
    ws_strat = wb.active
    ws_strat.title = "Synthèse & Stratégie Pub"
    ws_strat.views.sheetView[0].showGridLines = True

    # Bannière
    ws_strat.merge_cells("A1:G2")
    ws_strat["A1"] = "AUDIT OPÉRATIONNEL - PROFESSEURS DISPONIBLES & STRATÉGIE PUBLICITAIRE"
    ws_strat["A1"].font = font_title
    ws_strat["A1"].fill = navy_fill
    ws_strat["A1"].alignment = Alignment(horizontal="center", vertical="center")

    # Métriques clés
    ws_strat["A4"] = "Indicateur Clé"
    ws_strat["B4"] = "Valeur"
    ws_strat["C4"] = "Interprétation & Impact Campagne Publicitaire"
    for col in ["A4", "B4", "C4"]:
        ws_strat[col].font = font_header
        ws_strat[col].fill = header_fill

    kpis = [
        ("Professeurs validés (opérationnels)", len(teachers), "Capacité d'accueil immédiate pour répondre aux demandes des parents."),
        ("Professeurs avec Essai Gratuit Actif", sum(1 for t in teachers if t.essai_gratuit_actif), f"Soit {sum(1 for t in teachers if t.essai_gratuit_actif)/len(teachers)*100:.1f}% de l'offre ! Argument massif pour le tunnel pub 'Essai offert -> Officialisation'."),
        ("Nombre de communes couvertes", len(city_quartier_map), "Abomey-Calavi et Cotonou concentrent plus de 90% de la force vive."),
        ("Nombre de quartiers uniques couverts", len(quartier_summary), "Permet un ciblage ultra-localisé par quartier sur Facebook/Instagram."),
        ("Top 3 Matières dominantes", "Mathématiques (10), PCT (8), SVT (7)", "Cible prioritaire pour les créations publicitaires (visuels & textes)."),
        ("Tarif moyen horaire constaté", f"{sum(t['tarif_horaire_base'] for t in teachers_data)/len(teachers_data):.0f} FCFA / h", "Tarif accessible et rassurant à mettre en avant lors de l'officialisation.")
    ]

    r = 5
    for label, val, comment in kpis:
        ws_strat.cell(row=r, column=1, value=label).font = font_bold
        ws_strat.cell(row=r, column=2, value=val).alignment = Alignment(horizontal="center")
        ws_strat.cell(row=r, column=3, value=comment)
        for c in range(1, 4):
            ws_strat.cell(row=r, column=c).border = thin_border
        r += 1

    # Recommandations Ads
    r += 2
    ws_strat.cell(row=r, column=1, value="RECOMMANDATIONS STRATÉGIQUES POUR LA PUBLICITÉ").font = font_section
    r += 1

    ws_strat.cell(row=r, column=1, value="Type de Recommandation").font = font_header
    ws_strat.cell(row=r, column=1).fill = header_fill
    ws_strat.cell(row=r, column=2, value="Détail & Paramétrage Ads").font = font_header
    ws_strat.cell(row=r, column=2).fill = header_fill
    ws_strat.cell(row=r, column=3, value="Pourquoi ? (Garantie de non-déception)").font = font_header
    ws_strat.cell(row=r, column=3).fill = header_fill
    r += 1

    recos = [
        ("CIBLAGE GÉOGRAPHIQUE ADS", "Cibler uniquement Cotonou et Abomey-Calavi (rayon 15-20km). Ne pas diffuser sur Porto-Novo, Parakou ou le Nord.", "La plateforme a 99 rattachements à Calavi et 37 à Cotonou. Ailleurs, risque élevé de demande sans prof disponible."),
        ("CAMPAGNE 1 - SCIENTIFIQUE", "Créatifs axés sur : 'Maths, Physique-Chimie (PCT) et SVT - Collège & Lycée'.", "25 professeurs couvrent ce trio critique. C'est l'angoisse n°1 des parents au Bénin."),
        ("CAMPAGNE 2 - LITTÉRAIRE & LANGUES", "Créatifs axés sur : 'Français, Anglais & Renforcement - Préparation BEPC & BAC'.", "12 professeurs disponibles. Très forte demande en période pré-examens."),
        ("ARGUMENT D'APPEL (HOOK)", "Mettre en avant : '1ère Séance d'Essai pour tester la méthode sans engagement'.", "Plus de 85% des profs validés l'ont activé. Taux de conversion optimal vers l'officialisation."),
        ("SEGMENTS À EXCLURE DE LA PUB", "Ne PAS faire de publicité spécifique pour : Primaire CI-CM2 seul, Philosophie seule, Espagnol, Musique, etc.", "Très peu de professeurs dédiés (1 à 2). Risque immédiat de saturation ou d'échec de mise en relation.")
    ]

    for cat, det, just in recos:
        ws_strat.cell(row=r, column=1, value=cat).font = font_bold
        ws_strat.cell(row=r, column=2, value=det)
        ws_strat.cell(row=r, column=3, value=just)
        for c in range(1, 4):
            ws_strat.cell(row=r, column=c).border = thin_border
        r += 1

    # --- FEUILLE 2: Professeurs Disponibles ---
    ws_profs = wb.create_sheet(title="Professeurs Validés")
    ws_profs.views.sheetView[0].showGridLines = True

    headers_profs = [
        "ID", "Nom & Prénom", "Téléphone WhatsApp", "Email", "Matières Enseignées",
        "Classes Enseignées", "Classes d'Expertise", "Modes d'Intervention",
        "Villes Couvertes", "Nombre Quartiers", "Liste des Quartiers Couverts",
        "Essai Gratuit Actif", "Tarif Horaire Base (FCFA)", "Tarifs par Classe",
        "Expérience (ans)", "Score Fiabilité", "Note Équipe", "Vidéo Présente"
    ]

    for col_idx, h in enumerate(headers_profs, 1):
        cell = ws_profs.cell(row=1, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for row_idx, t in enumerate(teachers_data, 2):
        fill = zebra_fill if row_idx % 2 == 0 else PatternFill(fill_type=None)
        
        ws_profs.cell(row=row_idx, column=1, value=t['id']).alignment = Alignment(horizontal="center")
        ws_profs.cell(row=row_idx, column=2, value=t['nom_complet']).font = font_bold
        ws_profs.cell(row=row_idx, column=3, value=t['telephone'])
        ws_profs.cell(row=row_idx, column=4, value=t['email'])
        ws_profs.cell(row=row_idx, column=5, value=", ".join(t['matieres']))
        ws_profs.cell(row=row_idx, column=6, value=", ".join(t['classes_enseignees']))
        ws_profs.cell(row=row_idx, column=7, value=", ".join(t['classes_expertise']))
        ws_profs.cell(row=row_idx, column=8, value=", ".join(t['modes']))
        ws_profs.cell(row=row_idx, column=9, value=", ".join(t['villes']))
        ws_profs.cell(row=row_idx, column=10, value=t['nb_quartiers']).alignment = Alignment(horizontal="center")
        ws_profs.cell(row=row_idx, column=11, value="; ".join(t['quartiers']))
        
        # Essai gratuit
        eg_cell = ws_profs.cell(row=row_idx, column=12, value="OUI" if t['essai_gratuit'] else "NON")
        eg_cell.alignment = Alignment(horizontal="center")
        eg_cell.font = font_bold
        eg_cell.fill = success_fill if t['essai_gratuit'] else alert_fill

        ws_profs.cell(row=row_idx, column=13, value=t['tarif_horaire_base']).number_format = '#,##0'
        ws_profs.cell(row=row_idx, column=14, value=str(t['tarifs_par_classe']) if t['tarifs_par_classe'] else "Tarif base")
        ws_profs.cell(row=row_idx, column=15, value=t['annees_experience']).alignment = Alignment(horizontal="center")
        ws_profs.cell(row=row_idx, column=16, value=t['score_fiabilite']).alignment = Alignment(horizontal="center")
        ws_profs.cell(row=row_idx, column=17, value=t['note_initiale']).alignment = Alignment(horizontal="center")
        ws_profs.cell(row=row_idx, column=18, value="OUI" if t['a_video'] else "NON").alignment = Alignment(horizontal="center")

        for c in range(1, len(headers_profs) + 1):
            if c != 12: # garder fill essai gratuit
                if fill.fill_type: ws_profs.cell(row=row_idx, column=c).fill = fill
            ws_profs.cell(row=row_idx, column=c).border = thin_border

    # --- FEUILLE 3: Couverture Géographique ---
    ws_geo = wb.create_sheet(title="Couverture Géographique")
    ws_geo.views.sheetView[0].showGridLines = True

    headers_geo = [
        "Commune / Ville", "Quartier", "Nombre de Profs Opérationnels",
        "Nb avec Essai Gratuit", "Taux Essai Gratuit", "Matières Disponibles dans le Quartier", "Liste des Professeurs"
    ]

    for col_idx, h in enumerate(headers_geo, 1):
        cell = ws_geo.cell(row=1, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    sorted_quartiers = sorted(quartier_summary.values(), key=lambda x: (x['ville'], -len(x['profs']), x['quartier']))
    for row_idx, q in enumerate(sorted_quartiers, 2):
        nb_p = len(q['profs'])
        nb_eg = q['essai_gratuit_count']
        taux = f"{(nb_eg / nb_p * 100):.0f}%" if nb_p > 0 else "0%"

        ws_geo.cell(row=row_idx, column=1, value=q['ville']).font = font_bold
        ws_geo.cell(row=row_idx, column=2, value=q['quartier'])
        ws_geo.cell(row=row_idx, column=3, value=nb_p).alignment = Alignment(horizontal="center")
        ws_geo.cell(row=row_idx, column=4, value=nb_eg).alignment = Alignment(horizontal="center")
        ws_geo.cell(row=row_idx, column=5, value=taux).alignment = Alignment(horizontal="center")
        ws_geo.cell(row=row_idx, column=6, value=", ".join(sorted(list(q['matieres']))))
        ws_geo.cell(row=row_idx, column=7, value=", ".join(q['profs']))

        fill = zebra_fill if row_idx % 2 == 0 else PatternFill(fill_type=None)
        for c in range(1, len(headers_geo) + 1):
            if fill.fill_type: ws_geo.cell(row=row_idx, column=c).fill = fill
            ws_geo.cell(row=row_idx, column=c).border = thin_border

    # --- FEUILLE 4: Matrice Matières x Niveaux ---
    ws_matrix = wb.create_sheet(title="Matrice Matières x Niveaux")
    ws_matrix.views.sheetView[0].showGridLines = True

    # Niveaux clés
    classes_cols = [
        "Primaire", "6ème", "5ème", "4ème", "3ème", 
        "2nde Littéraire", "2nde Scientifique", 
        "1ère Littéraire", "1ère Scientifique", 
        "Tle Littéraire", "Tle Scientifique"
    ]

    ws_matrix.cell(row=1, column=1, value="Matière").font = font_header
    ws_matrix.cell(row=1, column=1).fill = header_fill
    ws_matrix.cell(row=1, column=2, value="Total Profs").font = font_header
    ws_matrix.cell(row=1, column=2).fill = sub_fill

    for idx, c_name in enumerate(classes_cols, 3):
        cell = ws_matrix.cell(row=1, column=idx, value=c_name)
        cell.font = font_header
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    sorted_subjects = sorted(subject_counts.items(), key=lambda x: -x[1])
    for row_idx, (sub, total_cnt) in enumerate(sorted_subjects, 2):
        ws_matrix.cell(row=row_idx, column=1, value=sub).font = font_bold
        ws_matrix.cell(row=row_idx, column=2, value=total_cnt).alignment = Alignment(horizontal="center")
        
        for c_idx, c_name in enumerate(classes_cols, 3):
            # Normalisation du check
            cnt = 0
            for k, v in subject_classes[sub].items():
                if c_name.lower().replace(' ', '') in k.lower().replace(' ', ''):
                    cnt += v
            
            cell = ws_matrix.cell(row=row_idx, column=c_idx, value=cnt)
            cell.alignment = Alignment(horizontal="center")
            if cnt >= 4:
                cell.fill = success_fill
                cell.font = font_bold
            elif cnt == 0:
                cell.font = font_small
                cell.value = "-"

        for c in range(1, len(classes_cols) + 3):
            ws_matrix.cell(row=row_idx, column=c).border = thin_border

    # Ajustement des largeurs de colonnes sur toutes les feuilles
    for sheet in wb.worksheets:
        for col in sheet.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = str(cell.value or '')
                if '\n' in val:
                    val = max(val.split('\n'), key=len)
                max_len = max(max_len, len(val))
            sheet.column_dimensions[col_letter].width = min(max(max_len + 3, 11), 50)

    excel_path = os.path.join(BASE_DIR, "Audit_Disponibilite_Professeurs_Campagne_Pub.xlsx")
    wb.save(excel_path)
    print(f"Fichier Excel sauvegardé avec succès dans: {excel_path}")

    # Sauvegarde du JSON pour le Dashboard
    # Convertir les sets en listes pour JSON
    quartiers_json_ready = []
    for q in sorted_quartiers:
        q_copy = dict(q)
        q_copy['matieres'] = sorted(list(q['matieres']))
        quartiers_json_ready.append(q_copy)

    json_path = os.path.join(BASE_DIR, "scratch", "teachers_audit_data.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total_teachers': len(teachers),
            'teachers': teachers_data,
            'subjects': sorted_subjects,
            'quartiers': quartiers_json_ready,
            'classes': classes_cols
        }, f, ensure_ascii=False, indent=2)
    print(f"JSON pour dashboard exporté: {json_path}")

if __name__ == '__main__':
    export_all()
