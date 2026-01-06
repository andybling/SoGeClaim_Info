import re
import html
from typing import Dict, Any, List, Optional

import streamlit as st
from dateutil import parser as dtparser


# =========================================================
# CONFIGURATION DE L'APPLICATION
# =========================================================
st.set_page_config(
    page_title="Suivi de Réclamation SGCI",
    page_icon="🆑",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Logo et thème rouge/noir/blanc
st.markdown(
    """
    <style>
      /* Réduction marges pour un rendu propre sur mobile */
      .block-container { padding-top: 1rem; padding-bottom: 1rem; }
      /* Légère amélioration des titres */
      h1, h2, h3 { letter-spacing: -0.2px; }
      h1 { color: #D50032; }
      h2, h3 { color: #000000; }
      /* Cards workflow */
      .wf-card {
        border-radius: 14px;
        padding: 10px 10px;
        text-align: center;
        font-size: 0.85rem;
        line-height: 1.2rem;
        box-shadow: 0 1px 8px rgba(0,0,0,0.06);
        margin-bottom: 10px;
        border: 1px solid #e0e0e0;
      }
      .wf-title { font-weight: 800; }
      .wf-dur { opacity: 0.95; font-size: 0.78rem; margin-top: 4px; }
      .muted { color: rgba(0,0,0,0.55); }
      .pill {
        display:inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-weight: 800;
        font-size: 0.85rem;
      }
      .stButton button {
        background-color: #D50032;
        color: white;
        border: none;
      }
      .stButton button:hover {
        background-color: #A80028;
        color: white;
      }
      .card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: #f9f9f9;
      }
      .info-box {
        background-color: #fff5f7;
        border-left: 4px solid #D50032;
        padding: 10px;
        margin: 10px 0;
      }
      .contact-info {
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        margin: 15px 0;
      }
    </style>
    """,
    unsafe_allow_html=True
)

# Header avec logo
col_logo, col_title = st.columns([1, 3])
with col_logo:
    st.image("https://particuliers.societegenerale.ci/fileadmin/user_upload/logos/SGBCI103_2025.svg", width=80)
with col_title:
    st.title("Suivi de Réclamation")
st.caption("Saisissez votre référence de réclamation pour suivre l'avancement.")

# Contact info
st.markdown(
    """
    <div class="contact-info">
        <strong>Votre conseiller clientèle</strong><br>
        <span style="color: #D50032; font-weight: bold; font-size: 1.2em;">27 20 20 10 10</span>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DONNÉES SIMULÉES (POC) - À REMPLACER PAR BACKEND/API
# =========================================================
def fetch_reclamation_data(ref: str) -> Optional[Dict[str, Any]]:
    """
    Simule la récupération des données d'une réclamation.
    En V1: remplacer par un appel API / DB / Excel.
    """
    reclamations_db = {
        "SGCI-338245": {
            "Filiale": "SGCI",
            "Réf. Réclamation": "SGCI-338245",
            "Date de création": "18-12-2024 13:16:36",
            "Date dernière modification": "19-12-2024 11:00:00",
            "Etat": "A Terminer",
            "Type": "Monetique",
            "Activité": "Retrait GAB SG",
            "Motif": "RETRAIT CONTESTE-NON RECONNU",
            "Objet de la réclamation": "Retrait DAB contesté",
            "Caractère": "Non fondé",  # Nouveau champ
            "Canal de réception": "Email",
            "Agence": "00111-PLATEAU",
            "Montant": "100000",
            "Dévise du montant": "XOF",
            "SLA Réclamation": "[REC - Etude Technique:10h 38m 16s, REC - Traitement Back:2d 10h 54m 1s, REC - En Régularisation:4d 10h 54m 52s]",
        },
        "SGCI-123456": {
            "Filiale": "SGCI",
            "Réf. Réclamation": "SGCI-123456",
            "Date de création": "20-12-2024 09:00:00",
            "Date dernière modification": "22-12-2024 15:30:00",
            "Etat": "Traitement",
            "Type": "Service",
            "Activité": "Frais de tenue de compte",
            "Motif": "AUTRES",
            "Objet de la réclamation": "Frais de compte non justifiés",
            "Caractère": "",  # Champ vide
            "Canal de réception": "Agence",
            "Agence": "00225-YAMOUSSOUKRO",
            "Montant": "5000",
            "Dévise du montant": "XOF",
            "SLA Réclamation": "[REC - Traitement:1h 15m 0s, REC - SUPPORT:30m 0s]",
        },
        "SGCI 3325G": {  # Ajout de la référence de l'image
            "Filiale": "SGCI",
            "Réf. Réclamation": "SGCI 3325G",
            "Date de création": "15-01-2025 10:30:00",
            "Date dernière modification": "20-01-2025 14:15:00",
            "Etat": "Résolue",
            "Type": "Monetique",
            "Activité": "Hôtel 648 56",
            "Motif": "RETRAIT CONTESTE-NON RECONNU",
            "Objet de la réclamation": "Hôtel 1080 central",
            "Caractère": "Fondé",
            "Canal de réception": "Email",
            "Agence": "00111 PLATEAU",
            "Montant": "10000",
            "Dévise du montant": "XOF",
            "SLA Réclamation": "[REC - Etude Technique:5h 20m 10s, REC - Traitement Back:1d 2h 30m 0s]",
        }
    }
    return reclamations_db.get(ref.strip().upper())


# =========================================================
# STATUTS / WORKFLOW
# =========================================================
STATUSES_ORDER = [
    "Initialisation", "SUPPORT", "Etude Technique", "Traitement", "Infos complémentaires",
    "Attente retour tiers", "En cours de régularisation", "Valider Regularisation",
    "Traitée", "A Terminer", "Résolue"
]

STATUS_COLORS = {
    "SUPPORT": "#6c757d",
    "Traitement": "#0d6efd",
    "Etude Technique": "#6610f2",
    "Infos complémentaires": "#20c997",
    "Attente retour tiers": "#fd7e14",
    "En cours de régularisation": "#ffc107",
    "Valider Regularisation": "#198754",
    "Traitée": "#0dcaf0",
    "A Terminer": "#D50032",  # Rouge SGCI
    "Initialisation": "#343a40",
    "Résolue": "#198754",
}


# =========================================================
# UTILITAIRES (NETTOYAGE / DATES / DURÉES)
# =========================================================
def clean_html_spaces(x: Any) -> str:
    if x is None:
        return ""
    s = str(x)
    s = html.unescape(s)
    s = s.replace("\xa0", " ").replace("\u00a0", " ")
    return re.sub(r"\s+", " ", s).strip()

def parse_date_fr_maybe(x: Any) -> Optional[str]:
    s = clean_html_spaces(x)
    if not s:
        return None
    try:
        dt = dtparser.parse(s, dayfirst=True)
        return dt.strftime("%d/%m/%Y à %H:%M")
    except Exception:
        return s

def duration_to_seconds(x: Any) -> int:
    """
    Supporte:
      - 2d 10h 54m 1s
      - 10h 38m 16s
      - 27 mi 45 s
      - 30m 0s
    """
    if x is None:
        return 0
    s = clean_html_spaces(x).lower()
    if not s:
        return 0

    # numérique direct
    if re.fullmatch(r"\d+", s):
        return int(s)

    s_compact = s.replace(" ", "")

    # dhms
    m = re.fullmatch(r"(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?", s_compact)
    if m:
        d, h, mi, sec = [int(v) if v else 0 for v in m.groups()]
        return d*86400 + h*3600 + mi*60 + sec

    # mi/s (ex: 27mi45s)
    m2 = re.fullmatch(r"(?:(\d+)mi)?(?:(\d+)s)?", s_compact)
    if m2:
        mi, sec = [int(v) if v else 0 for v in m2.groups()]
        return mi*60 + sec

    return 0

def seconds_to_human(seconds: int) -> str:
    if seconds <= 0:
        return "0s"
    d, rem = divmod(seconds, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    parts = []
    if d: parts.append(f"{d}j")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}min")
    if s: parts.append(f"{s}s")
    return " ".join(parts)


# =========================================================
# PARSING WORKFLOW (SLA Réclamation)
# =========================================================
def parse_workflow_from_sla(raw: Any) -> List[Dict[str, Any]]:
    s = clean_html_spaces(raw).strip()
    s = s.strip("[]")
    if not s:
        return []

    steps = []
    for item in s.split(","):
        item = item.strip()
        if ":" not in item:
            continue
        step, dur = item.split(":", 1)
        step = step.replace("REC -", "").strip()

        # normalisations métier
        if "traitement back" in step.lower():
            step = "Traitement"
        if "en régularisation" in step.lower() or "en regularisation" in step.lower():
            step = "En cours de régularisation"

        sec = duration_to_seconds(dur)
        if sec > 0:
            steps.append({"step": step, "seconds": sec, "human": seconds_to_human(sec)})

    return steps


# =========================================================
# UI COMPONENTS
# =========================================================
def pill_status(text: str) -> str:
    color = STATUS_COLORS.get(text, "#6c757d")
    return f'<span class="pill" style="background:{color};color:white;">{text}</span>'

def chunk_list(lst: List[str], size: int) -> List[List[str]]:
    return [lst[i:i+size] for i in range(0, len(lst), size)]

def render_workflow(status: str, steps: List[Dict[str, Any]]):
    st.markdown("### 🔄 Suivi du traitement")

    if status not in STATUSES_ORDER:
        st.warning("Le statut actuel n'est pas reconnu dans le référentiel.")
        status_idx = -1
    else:
        status_idx = STATUSES_ORDER.index(status)

    # durées par step
    sec_by_step = {}
    for s in steps:
        sec_by_step[s["step"]] = sec_by_step.get(s["step"], 0) + int(s["seconds"])

    # On affiche en lignes de 5 pour un rendu centré propre
    rows = chunk_list(STATUSES_ORDER, 5)

    for r in rows:
        cols = st.columns(len(r))
        for i, step_name in enumerate(r):
            global_index = STATUSES_ORDER.index(step_name)

            if status_idx == -1:
                state = "future"
            elif global_index < status_idx:
                state = "done"
            elif global_index == status_idx:
                state = "current"
            else:
                state = "future"

            if state == "done":
                bg = "#198754"
                fg = "white"
                icon = "✅"
            elif state == "current":
                bg = "#ffc107"
                fg = "#1f2d3d"
                icon = "⏳"
            else:
                bg = "#f1f3f5"
                fg = "#343a40"
                icon = "•"

            dur = seconds_to_human(sec_by_step.get(step_name, 0)) if sec_by_step.get(step_name, 0) else "—"

            cols[i].markdown(
                f"""
                <div class="wf-card" style="background:{bg};color:{fg};">
                  <div class="wf-title">{icon} {step_name}</div>
                  <div class="wf-dur">{dur}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Tableau détail
    if steps:
        st.markdown("#### ⏱️ Détail des durées")
        # agrégation et tri
        agg = {}
        for s in steps:
            agg[s["step"]] = agg.get(s["step"], 0) + int(s["seconds"])
        detail = [{"Étape": k, "Durée": seconds_to_human(v), "Secondes": v} for k, v in agg.items()]
        detail = sorted(detail, key=lambda x: x["Secondes"], reverse=True)

        total = sum(x["Secondes"] for x in detail)
        st.caption(f"Durée totale cumulée (selon étapes disponibles) : **{seconds_to_human(total)}**")
        st.dataframe(detail, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune information de durée disponible pour cette réclamation.")


# =========================================================
# FONCTION POUR L'AVIS CLIENT
# =========================================================
def render_feedback_form(ref: str):
    st.markdown("### 💬 Votre avis sur le traitement")
    st.markdown("Nous attachons une grande importance à votre satisfaction. Merci de partager votre expérience.")
    
    with st.form(key=f"feedback_form_{ref}"):
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown("**Très insatisfait**")
        with col5:
            st.markdown("**Très satisfait**")
        
        # Note sous forme d'étoiles
        rating = st.slider("Note globale", 1, 5, 3, 
                          label_visibility="collapsed",
                          help="1 = Très insatisfait, 5 = Très satisfait")
        
        # Affichage visuel des étoiles
        stars = "⭐" * rating
        st.markdown(f"**Votre note : {stars} ({rating}/5)**")
        
        # Commentaire
        comment = st.text_area("Commentaire (optionnel)", 
                              placeholder="Partagez vos remarques sur le traitement de votre réclamation...",
                              height=100)
        
        # Bouton de soumission
        submitted = st.form_submit_button("Envoyer mon avis", type="primary")
        
        if submitted:
            # Ici, normalement, on enregistrerait dans une base de données
            st.success("Merci pour votre feedback ! Votre avis a été enregistré.")
            st.balloons()


# =========================================================
# MAIN - UI CLIENT
# =========================================================
st.markdown("#### 🔎 Rechercher ma réclamation")
ref = st.text_input("Référence de réclamation", placeholder="Ex : SGCI 3325G, SGCI-338245").strip()

col_btn1, col_btn2 = st.columns([1, 1])
with col_btn1:
    search_clicked = st.button("Rechercher", type="primary", use_container_width=True)
with col_btn2:
    reset_clicked = st.button("Réinitialiser", use_container_width=True)

if reset_clicked:
    st.rerun()

if search_clicked:
    if not ref:
        st.warning("Merci de saisir une référence de réclamation.")
        st.stop()

    data = fetch_reclamation_data(ref)
    if not data:
        st.error("Réclamation introuvable. Vérifiez la référence saisie.")
        st.stop()

    # Extraction champs (client-safe : pas de nom / compte affiché)
    ref_out = clean_html_spaces(data.get("Réf. Réclamation"))
    filiale = clean_html_spaces(data.get("Filiale"))
    etat = clean_html_spaces(data.get("Etat"))
    type_rec = clean_html_spaces(data.get("Type"))
    activite = clean_html_spaces(data.get("Activité"))
    motif = clean_html_spaces(data.get("Motif"))
    objet = clean_html_spaces(data.get("Objet de la réclamation"))
    caractere = clean_html_spaces(data.get("Caractère", ""))  # Nouveau champ
    agence = clean_html_spaces(data.get("Agence"))
    montant = clean_html_spaces(data.get("Montant"))
    devise = clean_html_spaces(data.get("Dévise du montant"))

    created = parse_date_fr_maybe(data.get("Date de création")) or "—"
    updated = parse_date_fr_maybe(data.get("Date dernière modification")) or "—"

    # normaliser statut
    status = etat
    if "en régularisation" in status.lower() or "en regularisation" in status.lower():
        status = "En cours de régularisation"
    if status not in STATUSES_ORDER:
        # garde le statut tel quel, mais le workflow ne pourra pas le positionner précisément
        pass

    # workflow
    steps = parse_workflow_from_sla(data.get("SLA Réclamation"))

    st.divider()

    # Section Informations sur la réclamation (au lieu de Résumé)
    st.markdown("### 📋 Informations sur la réclamation")
    
    # Mise en forme en carte
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    a, b, c = st.columns(3)
    with a:
        st.markdown("**Référence**")
        st.markdown(f"**{ref_out or ref}**")
        if filiale:
            st.caption(f"Filiale : **{filiale}**")
    with b:
        st.markdown("**Date de création**")
        st.write(created)
        st.markdown("**Dernière mise à jour**")
        st.write(updated)
    with c:
        st.markdown("**Statut actuel**")
        st.markdown(pill_status(status), unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # Détails essentiels (sans PII) - modifié selon l'image
    st.markdown("### 📌 Détails")
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    d1, d2 = st.columns(2)
    with d1:
        st.write(f"**Type :** {type_rec or '—'}")
        st.write(f"**Agence :** {agence or '—'}")
        st.write(f"**Activité :** {activite or '—'}")
        st.write(f"**Objet :** {objet or '—'}")
    with d2:
        st.write(f"**Motif :** {motif or '—'}")
        # Caractère de la réclamation (affiché seulement si renseigné)
        if caractere and caractere.strip():
            st.write(f"**Caractère :** {caractere}")
        if montant:
            st.write(f"**Montant :** {montant} {devise}".strip())
        else:
            st.write("**Montant :** —")
    
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # Workflow
    render_workflow(status=status, steps=steps)

    st.divider()

    # Lien vers parcours client réclamation
    st.markdown("### 🔗 Lien vers parcours client réclamation")
    st.markdown(f"Pour plus d'informations, visitez : [https://particuliers.societegenerale.ci/fr/reclamation/](https://particuliers.societegenerale.ci/fr/reclamation/)")
    
    # Message conditionnel pour caractère "non fondé"
    if caractere and "non fondé" in caractere.lower():
        st.markdown(
            '<div class="info-box">'
            'Contactez votre gestionnaire de compte pour tout justificatif de caractère de la réclamation.'
            '</div>',
            unsafe_allow_html=True
        )

    # Section feedback si statut "A Terminer" ou "Résolue"
    terminal_statuses = ["A Terminer", "Résolue"]
    if status in terminal_statuses:
        render_feedback_form(ref_out or ref)

    # Note client-safe
    st.info("🔒 Pour protéger vos données, cette page n'affiche aucune information personnelle (nom, compte, téléphone).")

    # Debug POC optionnel
    # with st.expander("🔍 Debug POC (optionnel)"):
    #     st.write("Données complètes :", data)
