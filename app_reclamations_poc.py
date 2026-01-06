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

# Logo SGCI
logo_url = "https://particuliers.societegenerale.ci/fileadmin/user_upload/logos/SGBCI103_2025.svg"

st.markdown(
    f"""
    <style>
      /* Réduction marges pour un rendu propre sur mobile */
      .block-container {{ padding-top: 1.5rem; padding-bottom: 1.5rem; }}
      
      /* Thème rouge, noir, blanc */
      :root {{
        --sg-red: #CC0000;
        --sg-black: #000000;
        --sg-white: #FFFFFF;
        --sg-gray: #F5F5F5;
        --sg-dark-gray: #333333;
      }}
      
      /* Amélioration des titres avec thème SG */
      h1, h2, h3 {{ 
        letter-spacing: -0.2px;
        color: var(--sg-black);
      }}
      h1 {{ color: var(--sg-red); }}
      
      /* Cards workflow améliorées */
      .wf-card {{
        border-radius: 12px;
        padding: 12px 8px;
        text-align: center;
        font-size: 0.85rem;
        line-height: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 12px;
        border: 1px solid #E0E0E0;
        transition: all 0.3s ease;
      }}
      .wf-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      }}
      .wf-title {{ font-weight: 700; font-size: 0.9rem; }}
      .wf-dur {{ opacity: 0.8; font-size: 0.75rem; margin-top: 4px; font-weight: 500; }}
      
      /* Pastilles améliorées */
      .pill {{
        display:inline-block;
        padding: 8px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      }}
      
      /* Bloc suivi de traitement */
      .suivi-bloc {{
        background: linear-gradient(135deg, var(--sg-white) 0%, var(--sg-gray) 100%);
        border-radius: 16px;
        padding: 20px;
        margin: 20px 0;
        border: 1px solid rgba(204, 0, 0, 0.2);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
      }}
      
      .caractere-urgent {{
        background-color: #FFE5E5;
        color: var(--sg-red);
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 700;
        display: inline-block;
        margin: 10px 0;
        border-left: 4px solid var(--sg-red);
      }}
      
      /* Boutons améliorés */
      .stButton > button {{
        background-color: var(--sg-red);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
      }}
      .stButton > button:hover {{
        background-color: #B30000;
        transform: translateY(-2px);
      }}
      
      /* Avis section */
      .avis-section {{
        background: linear-gradient(135deg, #FFF9F9 0%, #FFEFEF 100%);
        border-radius: 16px;
        padding: 24px;
        margin: 24px 0;
        border: 2px solid var(--sg-red);
      }}
      
      /* Contact info */
      .contact-info {{
        background-color: var(--sg-gray);
        padding: 16px;
        border-radius: 12px;
        margin-top: 20px;
        text-align: center;
        border: 1px solid #DDD;
      }}
      
      /* Logo container */
      .logo-container {{
        text-align: center;
        margin-bottom: 20px;
      }}
      
      .logo-container img {{
        max-width: 180px;
        height: auto;
      }}
    </style>
    
    <div class="logo-container">
      <img src="{logo_url}" alt="SGCI Logo">
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# DONNÉES SIMULÉES AVEC CARACTÈRE DE LA RÉCLAMATION
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
            "Etat": "Valider Regularisation",
            "Type": "Monetique",
            "Activité": "Retrait GAB SG",
            "Motif": "RETRAIT CONTESTE-NON RECONNU",
            "Objet de la réclamation": "Retrait DAB contesté",
            "Caractère": "Urgente",  # Nouveau champ
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
            "Etat": "A Terminer",
            "Type": "Service",
            "Activité": "Frais de tenue de compte",
            "Motif": "AUTRES",
            "Objet de la réclamation": "Frais de compte non justifiés",
            "Caractère": "Non fondé",  # Nouveau champ
            "Agence": "00225-YAMOUSSOUKRO",
            "Montant": "5000",
            "Dévise du montant": "XOF",
            "SLA Réclamation": "[REC - Traitement:1h 15m 0s, REC - SUPPORT:30m 0s]",
        },
        "SGCI-789012": {
            "Filiale": "SGCI",
            "Réf. Réclamation": "SGCI-789012",
            "Date de création": "15-01-2025 10:30:00",
            "Date dernière modification": "20-01-2025 14:45:00",
            "Etat": "Résolue",
            "Type": "Service",
            "Activité": "Problème de carte",
            "Motif": "CARTE PERDUE",
            "Objet de la réclamation": "Remplacement carte perdue",
            "Caractère": "",  # Champ vide
            "Agence": "00300-ABIDJAN",
            "Montant": "15000",
            "Dévise du montant": "XOF",
            "SLA Réclamation": "[REC - Initialisation:1h 0m 0s, REC - Traitement:2d 5h 30m 0s]",
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
    "A Terminer": "#CC0000",  # Rouge SGCI
    "Initialisation": "#343a40",
    "Résolue": "#198754",
}


# =========================================================
# UTILITAIRES
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
    if x is None:
        return 0
    s = clean_html_spaces(x).lower()
    if not s:
        return 0

    if re.fullmatch(r"\d+", s):
        return int(s)

    s_compact = s.replace(" ", "")
    m = re.fullmatch(r"(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?", s_compact)
    if m:
        d, h, mi, sec = [int(v) if v else 0 for v in m.groups()]
        return d*86400 + h*3600 + mi*60 + sec

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
# PARSING WORKFLOW
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

        if "traitement back" in step.lower():
            step = "Traitement"
        if "en régularisation" in step.lower() or "en regularisation" in step.lower():
            step = "En cours de régularisation"

        sec = duration_to_seconds(dur)
        if sec > 0:
            steps.append({"step": step, "seconds": sec, "human": seconds_to_human(sec)})

    return steps


# =========================================================
# UI COMPONENTS AMÉLIORÉS
# =========================================================
def pill_status(text: str) -> str:
    color = STATUS_COLORS.get(text, "#CC0000")
    return f'<span class="pill" style="background:{color};color:white;">{text}</span>'

def chunk_list(lst: List[str], size: int) -> List[List[str]]:
    return [lst[i:i+size] for i in range(0, len(lst), size)]

def render_suivi_traitement(status: str, caractere: str):
    """
    Affiche le bloc "Suivi du traitement" selon le design demandé
    """
    st.markdown("### 🔄 Suivi du traitement")
    
    # Création du bloc avec style CSS
    with st.container():
        st.markdown('<div class="suivi-bloc">', unsafe_allow_html=True)
        
        # Caractère de la réclamation
        if caractere and caractere.strip():
            st.markdown(f'<div class="caractere-urgent">Caractère de la réclamation : <strong>{caractere}</strong></div>', unsafe_allow_html=True)
        
        # Statut actuel
        st.markdown(f"#### Statut actuel :")
        st.markdown(pill_status(status), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Progression du traitement
        st.markdown("#### Progression du traitement")
        
        # Étapes du workflow
        etapes = ["Initialisation", "Traitement", "Traitée", "Valider régularisation", 
                  "En cours de régularisation", "A terminer", "Résolue"]
        
        # Trouver l'index de l'étape actuelle
        status_lower = status.lower()
        current_index = -1
        for i, etape in enumerate(etapes):
            if etape.lower() in status_lower or status_lower in etape.lower():
                current_index = i
                break
        
        # Afficher les étapes avec indicateur visuel
        cols = st.columns(len(etapes))
        for i, etape in enumerate(etapes):
            with cols[i]:
                if i < current_index:
                    # Étape terminée
                    icon = "✅"
                    color = "#198754"
                elif i == current_index:
                    # Étape en cours
                    icon = "⏳"
                    color = "#CC0000"
                else:
                    # Étape future
                    icon = "○"
                    color = "#6c757d"
                
                st.markdown(
                    f"""
                    <div style="text-align:center;">
                        <div style="font-size:1.5rem;color:{color};margin-bottom:5px;">{icon}</div>
                        <div style="font-size:0.8rem;font-weight:500;">{etape}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_workflow_details(status: str, steps: List[Dict[str, Any]]):
    """
    Affiche les détails du workflow avec durée
    """
    if status not in STATUSES_ORDER:
        st.warning("Le statut actuel n'est pas reconnu dans le référentiel.")
        status_idx = -1
    else:
        status_idx = STATUSES_ORDER.index(status)

    # durées par step
    sec_by_step = {}
    for s in steps:
        sec_by_step[s["step"]] = sec_by_step.get(s["step"], 0) + int(s["seconds"])

    # Affichage en grille
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
                bg = "#CC0000"
                fg = "white"
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
        agg = {}
        for s in steps:
            agg[s["step"]] = agg.get(s["step"], 0) + int(s["seconds"])
        detail = [{"Étape": k, "Durée": seconds_to_human(v), "Secondes": v} for k, v in agg.items()]
        detail = sorted(detail, key=lambda x: x["Secondes"], reverse=True)

        total = sum(x["Secondes"] for x in detail)
        st.caption(f"Durée totale cumulée : **{seconds_to_human(total)}**")
        st.dataframe(detail, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune information de durée disponible pour cette réclamation.")

def render_avis_section(ref: str, status: str):
    """
    Affiche la section pour donner son avis si le statut est au moins "A Terminer"
    """
    # Vérifier si le statut est "A Terminer" ou "Résolue"
    status_lower = status.lower()
    if "a terminer" in status_lower or "résolue" in status_lower or "resolue" in status_lower:
        
        st.markdown('<div class="avis-section">', unsafe_allow_html=True)
        st.markdown("### 💬 Votre avis nous intéresse !")
        st.markdown("**Comment évaluez-vous le traitement de votre réclamation ?**")
        
        # Évaluation par étoiles
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button("⭐", use_container_width=True, key="star1"):
                st.session_state.rating = 1
        with col2:
            if st.button("⭐⭐", use_container_width=True, key="star2"):
                st.session_state.rating = 2
        with col3:
            if st.button("⭐⭐⭐", use_container_width=True, key="star3"):
                st.session_state.rating = 3
        with col4:
            if st.button("⭐⭐⭐⭐", use_container_width=True, key="star4"):
                st.session_state.rating = 4
        with col5:
            if st.button("⭐⭐⭐⭐⭐", use_container_width=True, key="star5"):
                st.session_state.rating = 5
        
        # Commentaire
        comment = st.text_area("Votre commentaire (facultatif)", 
                              placeholder="Partagez votre expérience...",
                              height=100)
        
        # Bouton d'envoi
        if st.button("Envoyer mon avis", type="primary", use_container_width=True):
            if 'rating' in st.session_state:
                st.success(f"Merci pour votre évaluation de {st.session_state.rating} ⭐ ! Votre feedback a été enregistré.")
                # Ici, normalement, on enverrait les données à un backend
            else:
                st.warning("Veuillez sélectionner une évaluation.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# MAIN - UI CLIENT AMÉLIORÉE
# =========================================================
st.markdown("#### 🔎 Rechercher ma réclamation")
st.markdown("Saisissez votre référence de réclamation pour suivre l'avancement")

ref = st.text_input("**Référence de réclamation**", 
                   placeholder="Ex : SGCI-338245",
                   label_visibility="collapsed").strip()

col_btn1, col_btn2 = st.columns([1, 1])
with col_btn1:
    search_clicked = st.button("🔍 Rechercher", type="primary", use_container_width=True)
with col_btn2:
    reset_clicked = st.button("🔄 Réinitialiser", use_container_width=True)

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

    # Extraction champs
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
    
    # workflow
    steps = parse_workflow_from_sla(data.get("SLA Réclamation"))

    st.divider()

    # Informations sur la réclamation (anciennement Résumé)
    st.markdown("### 📋 Informations sur la réclamation")
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

    st.divider()

    # Détails essentiels
    st.markdown("### 📌 Détails")
    d1, d2 = st.columns(2)
    with d1:
        st.write(f"**Type :** {type_rec or '—'}")
        st.write(f"**Activité :** {activite or '—'}")
        st.write(f"**Motif :** {motif or '—'}")
        # Affichage du caractère à la place du canal
        if caractere and caractere.strip():
            st.write(f"**Caractère :** {caractere}")
    with d2:
        st.write(f"**Agence :** {agence or '—'}")
        st.write(f"**Objet :** {objet or '—'}")
        if montant:
            st.write(f"**Montant :** {montant} {devise}".strip())
        else:
            st.write("**Montant :** —")

    # Message pour caractère "non fondé"
    if caractere and "non fondé" in caractere.lower():
        st.warning("**Contactez votre gestionnaire pour plus d'informations sur le caractère non fondé de votre réclamation.**")

    # Lien vers le parcours de réclamation
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align:center; padding:15px; background-color:#F9F9F9; border-radius:10px; margin:10px 0;">
            <p style="margin-bottom:10px;">📋 <strong>Pour plus d'informations sur le processus de réclamation</strong></p>
            <a href="https://particuliers.societegenerale.ci/fr/reclamation/" target="_blank" style="color:#CC0000; text-decoration:none; font-weight:bold;">
                Consultez notre parcours de réclamation →
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # Suivi du traitement
    render_suivi_traitement(status=status, caractere=caractere)
    
    # Détails du workflow
    render_workflow_details(status=status, steps=steps)

    # Section pour donner son avis
    render_avis_section(ref=ref, status=status)

    # Informations de contact
    st.markdown("---")
    st.markdown(
        """
        <div class="contact-info">
            <h4>📞 Besoin d'aide ?</h4>
            <p style="font-size:1.2rem; font-weight:bold; color:#CC0000; margin:10px 0;">
                Votre conseiller clientèle au <strong>27 20 20 10 10</strong>
            </p>
            <p style="font-size:0.9rem; color:#666; margin-top:10px;">
                Du lundi au vendredi de 8h à 17h<br>
                Samedi de 9h à 13h
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Note client-safe
    st.info("🔒 Pour protéger vos données, cette page n'affiche aucune information personnelle (nom, compte, téléphone).")

# Message d'accueil si aucune recherche
else:
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align:center; padding:40px 20px;">
            <h3 style="color:#CC0000;">Bienvenue sur le service de suivi de réclamation SGCI</h3>
            <p style="font-size:1.1rem; margin-top:20px;">
                Entrez votre référence de réclamation pour suivre son avancement en temps réel.
            </p>
            <p style="margin-top:30px; color:#666;">
                Vous trouverez votre référence dans l'email de confirmation ou sur l'accusé de réception.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Exemples de références
    with st.expander("📋 Exemples de formats de référence"):
        st.write("- **SGCI-338245**")
        st.write("- **SGCI-123456**")
        st.write("- **SGCI-789012**")
