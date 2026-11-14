import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json_file = os.path.join(BASE_DIR, "scratch", "teachers_audit_data.json")

with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

html_template = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ProfChezVous - Tableau de Bord Publicité & Disponibilité Professeurs</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Chart.js CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
        }}
        .glass-card {{
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 1rem;
        }}
        .gradient-text {{
            background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .badge-success {{
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}
        .badge-warning {{
            background: rgba(245, 158, 11, 0.15);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }}
    </style>
</head>
<body class="min-h-screen p-4 md:p-8">

    <div class="max-w-7xl mx-auto space-y-8">
        
        <!-- Header -->
        <header class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
            <div>
                <div class="flex items-center gap-3">
                    <span class="px-3 py-1 text-xs font-semibold rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                        AUDIT OPÉRATIONNEL & MARKETING
                    </span>
                    <span class="text-xs text-slate-400">Date : 13 Novembre 2026</span>
                </div>
                <h1 class="text-3xl md:text-4xl font-extrabold mt-2 tracking-tight">
                    Disponibilité des Professeurs & <span class="gradient-text">Stratégie Publicitaire</span>
                </h1>
                <p class="text-slate-400 text-sm mt-1">
                    Analyse pré-lancement pour garantir l'adéquation 100% entre les promesses publicitaires et la capacité d'accueil réelle.
                </p>
            </div>
            <div class="flex items-center gap-3">
                <a href="Audit_Disponibilite_Professeurs_Campagne_Pub.xlsx" download class="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold shadow-lg shadow-emerald-900/30 transition-all hover:scale-105 text-sm">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                    Télécharger l'Excel (.xlsx)
                </a>
            </div>
        </header>

        <!-- KPI Grid -->
        <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div class="glass-card p-6">
                <div class="text-slate-400 text-xs uppercase font-semibold tracking-wider">Capacité Opérationnelle</div>
                <div class="text-3xl font-black mt-2 text-white flex items-baseline gap-2">
                    32 <span class="text-xs font-medium text-emerald-400">Professeurs Validés</span>
                </div>
                <div class="text-xs text-slate-400 mt-2">Sur 54 inscrits au total (22 profils incomplets écartés)</div>
            </div>

            <div class="glass-card p-6 border-indigo-500/30">
                <div class="text-indigo-400 text-xs uppercase font-semibold tracking-wider">Levier Essai Gratuit</div>
                <div class="text-3xl font-black mt-2 text-white flex items-baseline gap-2">
                    87.5% <span class="text-xs font-medium text-indigo-300">(28 / 32 profs)</span>
                </div>
                <div class="text-xs text-slate-400 mt-2">Prêts pour l'argument pub : <em>"1er cours d'essai offert"</em></div>
            </div>

            <div class="glass-card p-6">
                <div class="text-slate-400 text-xs uppercase font-semibold tracking-wider">Zone Géographique Forte</div>
                <div class="text-3xl font-black mt-2 text-white flex items-baseline gap-2">
                    Calavi & Cotonou
                </div>
                <div class="text-xs text-slate-400 mt-2">95% des rattachements de quartiers couverts</div>
            </div>

            <div class="glass-card p-6">
                <div class="text-slate-400 text-xs uppercase font-semibold tracking-wider">Tarif Moyen Constaté</div>
                <div class="text-3xl font-black mt-2 text-white flex items-baseline gap-2">
                    2 750 <span class="text-xs font-medium text-slate-400">FCFA / heure</span>
                </div>
                <div class="text-xs text-slate-400 mt-2">Fourchette de 2 000 à 4 000 FCFA selon la classe</div>
            </div>
        </section>

        <!-- Recommandations Stratégiques Alert Box -->
        <section class="glass-card p-6 border-l-4 border-l-amber-500">
            <div class="flex items-start gap-4">
                <div class="p-2 rounded-lg bg-amber-500/10 text-amber-400 shrink-0">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                </div>
                <div class="space-y-2">
                    <h2 class="text-lg font-bold text-white">Stratégie Publicitaire Recommandée pour Garantir la Satisfaction Parentale</h2>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2 text-sm">
                        <div class="bg-slate-900/60 p-4 rounded-xl border border-emerald-500/20">
                            <div class="text-emerald-400 font-bold mb-1">🎯 Cible Prioritaire Pub (Feu Vert)</div>
                            <p class="text-xs text-slate-300 leading-relaxed">
                                Lancez les pubs sur <strong>Mathématiques, PCT et SVT</strong> pour les classes de <strong>3ème, 1ère et Terminale</strong> sur <strong>Abomey-Calavi et Cotonou</strong>. Vous avez une densité maximale pour honorer chaque demande.
                            </p>
                        </div>
                        <div class="bg-slate-900/60 p-4 rounded-xl border border-indigo-500/20">
                            <div class="text-indigo-400 font-bold mb-1">🎁 Tunnel d'Essai à l'Officialisation</div>
                            <p class="text-xs text-slate-300 leading-relaxed">
                                Utilisez le slogan : <em>"Testez l'enseignant idéal chez vous : 1er cours d'essai offert pour évaluer son niveau avant d'officialiser."</em> Cela élimine la barrière psychologique des parents.
                            </p>
                        </div>
                        <div class="bg-slate-900/60 p-4 rounded-xl border border-rose-500/20">
                            <div class="text-rose-400 font-bold mb-1">⛔ Zones & Segments à Proscrire (Feu Rouge)</div>
                            <p class="text-xs text-slate-300 leading-relaxed">
                                <strong>N'élargissez pas</strong> les pubs aux villes de province (Parakou, Porto-Novo) ni aux matières rares (Philosophie seule, Musique). Vous n'avez pas de profs dispo pour ces demandes.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Charts Section -->
        <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Matières Chart -->
            <div class="glass-card p-6">
                <h3 class="text-lg font-bold text-white mb-1">Professeurs par Matière Enseignée</h3>
                <p class="text-xs text-slate-400 mb-4">Volume de professeurs disponibles pour chaque discipline</p>
                <div class="h-64">
                    <canvas id="subjectsChart"></canvas>
                </div>
            </div>

            <!-- Top Quartiers Chart -->
            <div class="glass-card p-6">
                <h3 class="text-lg font-bold text-white mb-1">Top 10 des Quartiers les Mieux Couverts</h3>
                <p class="text-xs text-slate-400 mb-4">Rattachements des professeurs aux zones géographiques</p>
                <div class="h-64">
                    <canvas id="quartiersChart"></canvas>
                </div>
            </div>
        </section>

        <!-- Interactive Simulator Tool -->
        <section class="glass-card p-6 space-y-4">
            <div>
                <h3 class="text-xl font-bold text-white">Simulateur de Capacité Pré-Campagne</h3>
                <p class="text-xs text-slate-400">Sélectionnez les critères d'une future publicité pour vérifier instantanément si la plateforme peut répondre aux parents.</p>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
                <div>
                    <label class="block text-xs font-semibold text-slate-400 mb-1">Matière ciblée</label>
                    <select id="simSubject" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-indigo-500" onchange="runSimulation()">
                        <option value="ALL">Toutes les matières</option>
                    </select>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-400 mb-1">Zone Géographique</label>
                    <select id="simZone" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-indigo-500" onchange="runSimulation()">
                        <option value="ALL">Toutes les zones</option>
                    </select>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-400 mb-1">Option Essai Gratuit</label>
                    <select id="simTrial" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-indigo-500" onchange="runSimulation()">
                        <option value="ALL">Indifférent (Gratuit ou Payant)</option>
                        <option value="YES">Exiger Essai Gratuit Actif</option>
                    </select>
                </div>
            </div>

            <!-- Simulation Result Box -->
            <div id="simResult" class="p-4 rounded-xl bg-slate-900/80 border border-slate-700 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div>
                    <div class="text-xs text-slate-400 font-medium">Résultat de la simulation :</div>
                    <div id="simCountText" class="text-lg font-bold text-white mt-1">Sélectionnez des critères pour simuler</div>
                </div>
                <div id="simBadge" class="px-4 py-2 rounded-lg font-semibold text-xs text-center">
                    En attente
                </div>
            </div>
        </section>

        <!-- Table of Operational Teachers -->
        <section class="glass-card p-6 space-y-4">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h3 class="text-lg font-bold text-white">Répertoire Détaillé des 32 Professeurs Opérationnels</h3>
                    <p class="text-xs text-slate-400">Consultez les fiches actives pour le dispatching des leads générés par la publicité</p>
                </div>
                <input type="text" id="teacherSearch" placeholder="Rechercher nom, matière, quartier..." class="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 w-full sm:w-64" onkeyup="filterTeachers()">
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs">
                    <thead class="text-slate-400 uppercase bg-slate-800/60 border-b border-slate-700">
                        <tr>
                            <th class="p-3">Professeur</th>
                            <th class="p-3">Matière(s)</th>
                            <th class="p-3">Classes d'Expertise</th>
                            <th class="p-3">Quartiers Couverts</th>
                            <th class="p-3 text-center">Essai Gratuit</th>
                            <th class="p-3 text-right">Tarif Base</th>
                            <th class="p-3 text-center">Contact</th>
                        </tr>
                    </thead>
                    <tbody id="teachersTableBody" class="divide-y divide-slate-800/60">
                        <!-- Filled by JS -->
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Footer -->
        <footer class="text-center text-xs text-slate-500 py-6 border-t border-slate-800">
            ProfChezVous &bull; Audit de Pré-Lancement Publicitaire &bull; Données issues directement de la plateforme.
        </footer>

    </div>

    <!-- Inject JSON Data -->
    <script>
        const AUDIT_DATA = {json.dumps(data)};
        
        // Initialisation UI
        document.addEventListener('DOMContentLoaded', () => {{
            initCharts();
            populateFilters();
            renderTeachersTable(AUDIT_DATA.teachers);
            runSimulation();
        }});

        function initCharts() {{
            // 1. Subjects Chart
            const subCtx = document.getElementById('subjectsChart').getContext('2d');
            const topSubjects = AUDIT_DATA.subjects.slice(0, 8);
            new Chart(subCtx, {{
                type: 'bar',
                data: {{
                    labels: topSubjects.map(s => s[0]),
                    datasets: [{{
                        label: 'Nombre de professeurs',
                        data: topSubjects.map(s => s[1]),
                        backgroundColor: '#6366f1',
                        borderRadius: 6
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }} }},
                        x: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8' }} }}
                    }}
                }}
            }});

            // 2. Quartiers Chart
            const qCtx = document.getElementById('quartiersChart').getContext('2d');
            const topQuartiers = AUDIT_DATA.quartiers.slice(0, 8);
            new Chart(qCtx, {{
                type: 'bar',
                data: {{
                    labels: topQuartiers.map(q => q.quartier + ' (' + q.ville + ')'),
                    datasets: [{{
                        label: 'Profs disponibles',
                        data: topQuartiers.map(q => q.profs.length),
                        backgroundColor: '#10b981',
                        borderRadius: 6
                    }}]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }} }},
                        y: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8' }} }}
                    }}
                }}
            }});
        }}

        function populateFilters() {{
            const subSelect = document.getElementById('simSubject');
            AUDIT_DATA.subjects.forEach(([sub, cnt]) => {{
                const opt = document.createElement('option');
                opt.value = sub;
                opt.textContent = `${{sub}} (${{cnt}} profs)`;
                subSelect.appendChild(opt);
            }});

            const zoneSelect = document.getElementById('simZone');
            const zones = [...new Set(AUDIT_DATA.quartiers.map(q => q.ville))];
            zones.forEach(z => {{
                const opt = document.createElement('option');
                opt.value = z;
                opt.textContent = `Commune : ${{z}}`;
                zoneSelect.appendChild(opt);
            }});
        }}

        function runSimulation() {{
            const selectedSub = document.getElementById('simSubject').value;
            const selectedZone = document.getElementById('simZone').value;
            const trialOnly = document.getElementById('simTrial').value === 'YES';

            const filtered = AUDIT_DATA.teachers.filter(t => {{
                const matchSub = (selectedSub === 'ALL') || t.matieres.includes(selectedSub);
                const matchZone = (selectedZone === 'ALL') || t.villes.includes(selectedZone);
                const matchTrial = (!trialOnly) || t.essai_gratuit;
                return matchSub && matchZone && matchTrial;
            }});

            const count = filtered.length;
            const countText = document.getElementById('simCountText');
            const badge = document.getElementById('simBadge');

            if (count >= 5) {{
                countText.innerHTML = `<span class="text-emerald-400">${{count}} Professeurs Disponibles</span> &bull; Capacité optimale pour lancer la publicité sans rupture !`;
                badge.className = "px-4 py-2 rounded-lg font-bold text-xs bg-emerald-500/20 text-emerald-300 border border-emerald-500/40";
                badge.textContent = "FEU VERT POUR LA PUB";
            }} else if (count >= 2) {{
                countText.innerHTML = `<span class="text-amber-400">${{count}} Professeurs Disponibles</span> &bull; Capacité modérée, limitez le budget pub quotidien.`;
                badge.className = "px-4 py-2 rounded-lg font-bold text-xs bg-amber-500/20 text-amber-300 border border-amber-500/40";
                badge.textContent = "BUDGET MODÉRÉ CONSEILLÉ";
            }} else {{
                countText.innerHTML = `<span class="text-rose-400">${{count}} Professeur Disponible</span> &bull; ⚠️ Risque majeur de générer des demandes non traitées !`;
                badge.className = "px-4 py-2 rounded-lg font-bold text-xs bg-rose-500/20 text-rose-300 border border-rose-500/40";
                badge.textContent = "CIBLAGE DÉCONSEILLÉ";
            }}
        }}

        function renderTeachersTable(list) {{
            const tbody = document.getElementById('teachersTableBody');
            tbody.innerHTML = '';

            list.forEach(t => {{
                const tr = document.createElement('tr');
                tr.className = "hover:bg-slate-800/40 transition-colors";
                
                const trialBadge = t.essai_gratuit 
                    ? '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">OUI</span>'
                    : '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-700 text-slate-300">NON</span>';

                tr.innerHTML = `
                    <td class="p-3 font-semibold text-slate-200">${{t.nom_complet}}</td>
                    <td class="p-3 text-indigo-300">${{t.matieres.join(', ')}}</td>
                    <td class="p-3 text-slate-300">${{t.classes_expertise.join(', ') || t.classes_enseignees.slice(0,3).join(', ')}}</td>
                    <td class="p-3 text-slate-400 max-w-xs truncate" title="${{t.quartiers.join(', ')}}">${{t.quartiers.slice(0, 2).join(', ')}}${{t.quartiers.length > 2 ? ' +'+(t.quartiers.length-2) : ''}}</td>
                    <td class="p-3 text-center">${{trialBadge}}</td>
                    <td class="p-3 text-right font-mono text-slate-300">${{t.tarif_horaire_base ? t.tarif_horaire_base.toLocaleString() + ' F' : '-'}}</td>
                    <td class="p-3 text-center">
                        <a href="https://wa.me/${{t.telephone.replace(/[^0-9]/g, '')}}" target="_blank" class="text-emerald-400 hover:underline">WhatsApp</a>
                    </td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function filterTeachers() {{
            const q = document.getElementById('teacherSearch').value.toLowerCase();
            const filtered = AUDIT_DATA.teachers.filter(t => {{
                const text = (t.nom_complet + ' ' + t.matieres.join(' ') + ' ' + t.quartiers.join(' ')).toLowerCase();
                return text.includes(q);
            }});
            renderTeachersTable(filtered);
        }}
    </script>
</body>
</html>
"""

output_path = os.path.join(BASE_DIR, "dashboard_publicite_profs.html")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f"Tableau de bord généré avec succès dans : {output_path}")
