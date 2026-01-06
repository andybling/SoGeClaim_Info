import re
import html
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import time

import streamlit as st
from dateutil import parser as dtparser

# =========================================================
# CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Suivi de Réclamation | SGCI",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# STYLE CSS PREMIUM OPTIMISÉ
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f9fafb 0%, #f0f2f5 100%);
    }
    
    /* Header Premium */
    .header-premium {
        background: linear-gradient(135deg, #D50032 0%, #B0002A 100%);
        padding: 1.5rem 0;
        margin-bottom: 3rem;
        box-shadow: 0 8px 32px rgba(213, 0, 50, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .header-premium::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        animation: shine 3s infinite;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    /* Cards Modernes */
    .card-modern {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(213, 0, 50, 0.1);
        transition: all 0.3s ease;
    }
    
    .card-modern:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
        border-color: rgba(213, 0, 50, 0.2);
    }
    
    /* Boutons Premium */
    .stButton > button {
        background: linear-gradient(135deg, #D50032 0%, #B0002A 100%);
        color: white;
        border: none;
        padding: 12px 28px;
        border-radius: 50px;
        font-weight: 600;
        font-size: 15px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 6px 20px rgba(213, 0, 50, 0.3);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(213, 0, 50, 0.4);
        background: linear-gradient(135deg, #B0002A 0%, #900022 100%);
    }
    
    /* Input Fields améliorés */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e5e7eb;
        padding: 14px 18px;
        font-size: 15px;
        transition: all 0.3s ease;
        background: white;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #D50032;
        box-shadow: 0 0 0 3px rgba(213, 0, 50, 0.1);
    }
    
    /* TIMELINE EXACTE COMME L'IMAGE */
    .timeline-simple {
        position: relative;
        padding: 40px 0 60px 0;
        margin: 2rem 0;
    }
    
    .timeline-line {
        position: absolute;
        top: 30px;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, 
            #28a745 0%, 
            #28a745 var(--progress, 0%), 
            #e5e7eb var(--progress, 0%), 
            #e5e7eb 100%);
        z-index: 1;
    }
    
    .timeline-step {
        position: relative;
        z-index: 2;
        display: inline-block;
        width: 20%;
        text-align: center;
        vertical-align: top;
    }
    
    .timeline-point {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: #e5e7eb;
        border: 3px solid white;
        margin: 0 auto 12px;
        position: relative;
        z-index: 3;
        transition: all 0.3s ease;
        box-shadow: 0 0 0 0 rgba(213, 0, 50, 0);
    }
    
    .timeline-point.completed {
        background: #28a745;
        border-color: white;
        box-shadow: 0 0 0 4px rgba(40, 167, 69, 0.2);
    }
    
    .timeline-point.active {
        background: #D50032;
        border-color: white;
        box-shadow: 0 0 0 4px rgba(213, 0, 50, 0.3);
        animation: pulse-active 2s infinite;
    }
    
    @keyframes pulse-active {
        0%, 100% {
            box-shadow: 0 0 0 4px rgba(213, 0, 50, 0.3);
        }
        50% {
            box-shadow: 0 0 0 8px rgba(213, 0, 50, 0.1);
        }
    }
    
    .timeline-label {
        font-size: 12px;
        font-weight: 600;
        color: #6b7280;
        margin-top: 8px;
        line-height: 1.3;
        padding: 0 5px;
        transition: all 0.3s ease;
    }
    
    .timeline-label.active {
        color: #D50032;
        font-weight: 700;
        transform: scale(1.05);
    }
    
    .timeline-label.completed {
        color: #28a745;
    }
    
    /* Système d'étoiles FLUIDE */
    .stars-container {
        display: flex;
        justify-content: center;
        gap: 4px;
        margin: 25px 0 15px;
    }
    
    .star {
        font-size: 40px;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        color: #e5e7eb;
        line-height: 1;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
    }
    
    .star:hover {
        transform: scale(1.2);
    }
    
    .star.selected {
        color: #ffc107;
        transform: scale(1.1);
        filter: drop-shadow(0 0 15px rgba(255, 193, 7, 0.4));
    }
    
    .star-rating-text {
        text-align: center;
        font-size: 18px;
        font-weight: 600;
        color: #374151;
        margin-top: 10px;
    }
    
    /* Badges modernes */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.3px;
        text-transform: uppercase;
        gap: 6px;
    }
    
    .badge-primary {
        background: linear-gradient(135deg, rgba(213, 0, 50, 0.1), rgba(213, 0, 50, 0.15));
        color: #D50032;
        border: 1.5px solid rgba(213, 0, 50, 0.2);
    }
    
    .badge-success {
        background: linear-gradient(135deg, rgba(40, 167, 69, 0.1), rgba(40, 167, 69, 0.15));
        color: #28a745;
        border: 1.5px solid rgba(40, 167, 69, 0.2);
    }
    
    /* Layout amélioré */
    .info-section {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
    }
    
    .info-item {
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid #f1f5f9;
    }
    
    .info-item:last-child {
        border-bottom: none;
    }
    
    .info-label {
        font-weight: 600;
        color: #4b5563;
        font-size: 14px;
    }
    
    .info-value {
        color: #1f2937;
        font-weight: 500;
        font-size: 14px;
        text-align: right;
        max-width: 60%;
    }
    
    /* Contact Card améliorée */
    .contact-card-premium {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border-radius: 20px;
        padding: 2.5rem;
        color: white;
        text-align: center;
        margin: 2.5rem 0;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .contact-card-premium::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.05) 0%, transparent 70%);
        animation: rotate-slow 30s linear infinite;
    }
    
    @keyframes rotate-slow {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .phone-number-premium {
        font-size: 2.8rem;
        font-weight: 900;
        margin: 1.5rem 0;
        letter-spacing: 1px;
        position: relative;
        z-index: 2;
        background: linear-gradient(135deg, #ffffff 0%, #e5e7eb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    /* Progress Circle */
    .progress-circle {
        width: 120px;
        height: 120px;
        margin: 0 auto 2rem;
        position: relative;
    }
    
    .progress-circle svg {
        width: 100%;
        height: 100%;
        transform: rotate(-90deg);
    }
    
    .progress-circle-bg {
        fill: none;
        stroke: #e5e7eb;
        stroke-width: 8;
    }
    
    .progress-circle-fill {
        fill: none;
        stroke: #D50032;
        stroke-width: 8;
        stroke-linecap: round;
        stroke-dasharray: 314;
        stroke-dashoffset: calc(314 - (314 * var(--progress)) / 100);
        transition: stroke-dashoffset 1.5s ease;
    }
    
    .progress-circle-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 28px;
        font-weight: 800;
        color: #D50032;
    }
    
    /* Success Message amélioré */
    .success-message-premium {
        background: linear-gradient(135deg, rgba(40, 167, 69, 0.08), rgba(40, 167, 69, 0.04));
        border: 2px solid rgba(40, 167, 69, 0.3);
        padding: 1.5rem;
        border-radius: 16px;
        margin: 2rem 0;
        color: #28a745;
        font-weight: 600;
        animation: slide-in-right 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    @keyframes slide-in-right {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Animation fade-in */
    @keyframes fade-in-up {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in-up {
        animation: fade-in-up 0.6s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# INITIALISATION SESSION
# =========================================================
if 'feedback_data' not in st.session_state:
    st.session_state.feedback_data = {}
if 'current_reference' not in st.session_state:
    st.session_state.current_reference = None
if 'current_rating' not in st.session_state:
    st.session_state.current_rating = {}
if 'hover_star' not in st.session_state:
    st.session_state.hover_star = 0

# =========================================================
# FONCTIONS UTILITAIRES OPTIMISÉES
# =========================================================
def clean_html_spaces(x: Any) -> str:
    if x is None:
        return ""
    s = str(x)
    s = html.unescape(s)
    s = s.replace("\xa0", " ").replace("\u00a0", " ")
    return re.sub(r"\s+", " ", s).strip()

def parse_date_fr(x: Any) -> Optional[str]:
    s = clean_html_spaces(x)
    if not s:
        return None
    try:
        dt = dtparser.parse(s, dayfirst=True)
        return dt.strftime("%d/%m/%Y à %H:%M")
    except:
        return s

def save_feedback(reference: str, rating: int, comment: str = ""):
    """Sauvegarde le feedback pour une réclamation"""
    if reference not in st.session_state.feedback_data:
        st.session_state.feedback_data[reference] = []
    
    feedback_entry = {
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'rating': rating,
        'comment': comment
    }
    
    st.session_state.feedback_data[reference].append(feedback_entry)
    st.session_state.current_rating[reference] = rating

def get_average_rating(reference: str) -> Tuple[float, int]:
    """Retourne la note moyenne et le nombre d'avis"""
    if reference in st.session_state.feedback_data:
        feedbacks = st.session_state.feedback_data[reference]
        if feedbacks:
            total = sum(f['rating'] for f in feedbacks)
            return total / len(feedbacks), len(feedbacks)
    return 0.0, 0

def render_timeline_simple(status: str, steps_data: List[Dict[str, Any]]):
    """Affiche une timeline simple et efficace comme sur l'image"""
    
    # Ordre des statuts
    STATUS_FLOW = [
        "Initialisation",
        "Etude Technique", 
        "Traitement",
        "Infos complémentaires",
        "Attente retour tiers",
        "En cours de régularisation",
        "Valider Regularisation",
        "Traitée",
        "A Terminer",
        "Résolue"
    ]
    
    # Filtrer les statuts présents
    available_statuses = []
    for s in STATUS_FLOW:
        if any(s in step['step'] for step in steps_data) or s in status:
            available_statuses.append(s)
    
    if not available_statuses:
        st.warning("Aucune information de progression disponible")
        return
    
    # Déterminer l'index du statut actuel
    current_index = -1
    for i, s in enumerate(available_statuses):
        if s in status or status in s:
            current_index = i
            break
    
    # Calcul du pourcentage de progression
    progress_pct = ((current_index + 1) / len(available_statuses)) * 100 if current_index >= 0 else 0
    
    # Créer la timeline HTML simple
    timeline_html = f"""
    <div class="timeline-simple">
        <div class="timeline-line" style="--progress: {progress_pct}%"></div>
        <div style="display: flex; justify-content: space-between; position: relative;">
    """
    
    for i, step in enumerate(available_statuses):
        point_class = "pending"
        label_class = ""
        
        if i < current_index:
            point_class = "completed"
            label_class = "completed"
        elif i == current_index:
            point_class = "active"
            label_class = "active"
        
        timeline_html += f"""
            <div class="timeline-step">
                <div class="timeline-point {point_class}"></div>
                <div class="timeline-label {label_class}">{step}</div>
            </div>
        """
    
    timeline_html += "</div></div>"
    
    # Afficher le cercle de progression
    st.markdown(f"""
    <div style="text-align: center; margin: 2rem 0;">
        <div class="progress-circle">
            <svg viewBox="0 0 100 100">
                <circle class="progress-circle-bg" cx="50" cy="50" r="45"/>
                <circle class="progress-circle-fill" cx="50" cy="50" r="45" 
                        style="--progress: {progress_pct}"/>
            </svg>
            <div class="progress-circle-text">{int(progress_pct)}%</div>
        </div>
        <div style="color: #6b7280; font-size: 14px; margin-top: 1rem;">
            {current_index + 1} sur {len(available_statuses)} étapes
            {f"• Statut actuel : <strong style='color: #D50032;'>{available_statuses[current_index] if current_index >= 0 else 'Non déterminé'}</strong>" if current_index >= 0 else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(timeline_html, unsafe_allow_html=True)
    
    # Légende simplifiée
    st.markdown("""
    <div style="display: flex; justify-content: center; gap: 25px; margin-top: 2rem; flex-wrap: wrap;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <div class="timeline-point completed" style="width: 12px; height: 12px; margin: 0;"></div>
            <span style="color: #28a745; font-weight: 600; font-size: 13px;">Terminé</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div class="timeline-point active" style="width: 12px; height: 12px; margin: 0; animation: none;"></div>
            <span style="color: #D50032; font-weight: 600; font-size: 13px;">En cours</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div class="timeline-point" style="width: 12px; height: 12px; margin: 0; background: #e5e7eb;"></div>
            <span style="color: #9ca3af; font-weight: 600; font-size: 13px;">À venir</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_star_rating_fluid(reference: str, max_stars: int = 5):
    """Affiche un système d'étoiles fluide et interactif"""
    
    # Initialiser la note si nécessaire
    if reference not in st.session_state.current_rating:
        st.session_state.current_rating[reference] = 0
    
    current_rating = st.session_state.current_rating[reference]
    
    # Créer les étoiles avec Streamlit
    cols = st.columns(max_stars)
    selected_rating = current_rating
    
    for i in range(max_stars):
        with cols[i]:
            star_value = i + 1
            if st.button("★", key=f"star_{reference}_{i}", 
                       help=f"Noter {star_value} étoile{'s' if star_value > 1 else ''}",
                       use_container_width=True):
                selected_rating = star_value
                st.session_state.current_rating[reference] = selected_rating
                st.rerun()
    
    # Afficher les étoiles visuellement
    stars_html = ""
    for i in range(max_stars):
        if i < selected_rating:
            stars_html += '<span class="star selected">★</span>'
        else:
            stars_html += '<span class="star">★</span>'
    
    st.markdown(f"""
    <div class="stars-container">
        {stars_html}
    </div>
    <div class="star-rating-text">
        {selected_rating}/5 étoile{'s' if selected_rating > 1 else ''}
    </div>
    """, unsafe_allow_html=True)
    
    return selected_rating

def get_claim_data(ref: str) -> Optional[Dict[str, Any]]:
    """Récupère les données de réclamation"""
    db = {
        "SGCI 3325G": {
            "Réf. Réclamation": "SGCI 3325G",
            "Date de création": "15-01-2025 10:30:00",
            "Date dernière modification": "20-01-2025 14:15:00",
            "Etat": "En cours de régularisation",
            "Type": "Monetique",
            "Activité": "Hôtel 648 56",
            "Motif": "RETRAIT CONTESTE-NON RECONNU",
            "Objet de la réclamation": "Hôtel 1080 central",
            "Caractère": "En étude",
            "Agence": "00111 PLATEAU",
            "Montant": "10000",
            "Dévise du montant": "XOF",
            "SLA Réclamation": "[REC - Etude Technique:5h 20m 10s, REC - Traitement Back:1d 2h 30m 0s]",
        },
        "SGCI-338245": {
            "Réf. Réclamation": "SGCI-338245",
            "Date de création": "18-12-2024 13:16:36",
            "Date dernière modification": "19-12-2024 11:00:00",
            "Etat": "A Terminer",
            "Type": "Monetique",
            "Activité": "Retrait GAB SG",
            "Motif": "RETRAIT CONTESTE-NON RECONNU",
            "Objet de la réclamation": "Retrait DAB contesté",
            "Caractère": "Non fondé",
            "Agence": "00111-PLATEAU",
            "Montant": "100000",
            "Dévise du montant": "XOF",
            "SLA Réclamation": "[REC - Etude Technique:10h 38m 16s, REC - Traitement Back:2d 10h 54m 1s]",
        }
    }
    
    for variant in [ref, ref.upper(), ref.replace("-", " "), ref.replace(" ", "-")]:
        if variant in db:
            return db[variant]
    return None

# =========================================================
# INTERFACE PRINCIPALE OPTIMISÉE
# =========================================================

# Header premium
st.markdown("""
<div class="header-premium">
    <div style="max-width: 1200px; margin: 0 auto; padding: 0 20px; position: relative; z-index: 2;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 20px;">
                <img src="https://particuliers.societegenerale.ci/fileadmin/user_upload/logos/SGBCI103_2025.svg" 
                     style="height: 50px; filter: brightness(0) invert(1);">
                <div>
                    <h1 style="margin: 0; color: white; font-weight: 800; font-size: 24px;">
                        Suivi de Réclamation
                    </h1>
                    <p style="margin: 5px 0 0 0; color: rgba(255, 255, 255, 0.9); font-size: 14px;">
                        Service Client - Suivi en temps réel
                    </p>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 12px; color: rgba(255, 255, 255, 0.8); font-weight: 600; text-transform: uppercase;">Support Client</div>
                <div style="font-size: 22px; font-weight: 800; color: white; margin-top: 3px;">
                    27 20 20 10 10
                </div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Contenu principal
st.markdown('<div style="max-width: 1200px; margin: 0 auto; padding: 0 20px;">', unsafe_allow_html=True)

# Section recherche simplifiée
st.markdown('<div class="fade-in-up">', unsafe_allow_html=True)

col_title, col_space, col_phone = st.columns([3, 1, 2])
with col_title:
    st.markdown("""
    <h2 style="color: #111827; margin-bottom: 1rem; font-weight: 800;">
        🔍 Rechercher votre réclamation
    </h2>
    <p style="color: #6b7280; margin-bottom: 1.5rem; font-size: 15px;">
        Saisissez votre référence pour suivre l'avancement de votre dossier
    </p>
    """, unsafe_allow_html=True)

with st.container():
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        reference = st.text_input(" ", 
                                placeholder="Ex: SGCI 3325G ou SGCI-338245",
                                key="search_input",
                                label_visibility="collapsed")
    with col_btn:
        search_clicked = st.button("Rechercher", type="primary", use_container_width=True)

# Affichage des résultats
if search_clicked and reference:
    st.session_state.current_reference = reference
    data = get_claim_data(reference)
    
    if not data:
        st.error("""
        <div style='background: linear-gradient(135deg, rgba(239, 68, 68, 0.08), rgba(239, 68, 68, 0.04)); 
                   border: 2px solid rgba(239, 68, 68, 0.3); padding: 1.5rem; border-radius: 16px; margin: 2rem 0;'>
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="font-size: 24px;">❌</div>
                <div>
                    <strong style="color: #dc2626;">Réclamation introuvable</strong><br>
                    <span style="color: #6b7280;">Vérifiez la référence et réessayez</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    # Extraction des données
    ref_out = clean_html_spaces(data.get("Réf. Réclamation", reference))
    created = parse_date_fr(data.get("Date de création")) or "Non disponible"
    updated = parse_date_fr(data.get("Date dernière modification")) or "Non disponible"
    etat = clean_html_spaces(data.get("Etat", "Non spécifié"))
    type_rec = clean_html_spaces(data.get("Type", "Non spécifié"))
    activite = clean_html_spaces(data.get("Activité", "Non spécifié"))
    motif = clean_html_spaces(data.get("Motif", "Non spécifié"))
    objet = clean_html_spaces(data.get("Objet de la réclamation", "Non spécifié"))
    caractere = clean_html_spaces(data.get("Caractère", ""))
    agence = clean_html_spaces(data.get("Agence", "Non spécifié"))
    montant = clean_html_spaces(data.get("Montant", ""))
    devise = clean_html_spaces(data.get("Dévise du montant", "XOF"))
    
    # Traitement du workflow
    sla = data.get("SLA Réclamation", "")
    steps = []
    if sla:
        s = clean_html_spaces(sla).strip("[]")
        for item in s.split(","):
            item = item.strip()
            if ":" in item:
                step, dur = item.split(":", 1)
                step = step.replace("REC -", "").strip()
                steps.append({"step": step, "duration": dur})
    
    # Carte principale de la réclamation
    st.markdown(f"""
    <div class="card-modern fade-in-up">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2rem; flex-wrap: wrap; gap: 15px;">
            <div style="flex: 1; min-width: 250px;">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px;">
                    <div style="background: linear-gradient(135deg, #D50032, #B0002A); width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                        <span style="color: white; font-size: 20px;">📋</span>
                    </div>
                    <div>
                        <h2 style="color: #111827; margin: 0; font-weight: 800; font-size: 22px;">
                            Réclamation {ref_out}
                        </h2>
                        <p style="color: #6b7280; margin: 4px 0 0 0; font-size: 13px;">
                            Créée le {created}
                        </p>
                    </div>
                </div>
            </div>
            <div class="badge {'badge-success' if etat in ['Résolue', 'Traitée'] else 'badge-primary'}" 
                 style="font-size: 11px; padding: 6px 14px;">
                {etat}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Informations en grille moderne
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown('<div class="info-section">', unsafe_allow_html=True)
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1rem;">
            <div style="background: rgba(213, 0, 50, 0.1); width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                <span style="color: #D50032; font-size: 16px;">📄</span>
            </div>
            <h3 style="color: #111827; margin: 0; font-weight: 700; font-size: 16px;">
                Informations générales
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="display: grid; gap: 8px;">
            <div class="info-item">
                <span class="info-label">Type</span>
                <span class="info-value">{type_rec}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Agence</span>
                <span class="info-value">{agence}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Activité</span>
                <span class="info-value">{activite}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_info2:
        st.markdown('<div class="info-section">', unsafe_allow_html=True)
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1rem;">
            <div style="background: rgba(213, 0, 50, 0.1); width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                <span style="color: #D50032; font-size: 16px;">📊</span>
            </div>
            <h3 style="color: #111827; margin: 0; font-weight: 700; font-size: 16px;">
                Détails spécifiques
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="display: grid; gap: 8px;">
            <div class="info-item">
                <span class="info-label">Objet</span>
                <span class="info-value">{objet}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Motif</span>
                <span class="info-value">{motif}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Montant</span>
                <span class="info-value">{montant + ' ' + devise if montant else 'Non spécifié'}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Caractère de la réclamation
    if caractere and caractere.strip():
        st.markdown(f"""
        <div style="background: {'rgba(213, 0, 50, 0.05)' if 'non fondé' in caractere.lower() else 'rgba(40, 167, 69, 0.05)'}; 
                    border: 2px solid {'rgba(213, 0, 50, 0.2)' if 'non fondé' in caractere.lower() else 'rgba(40, 167, 69, 0.2)'}; 
                    padding: 1.25rem; border-radius: 16px; margin: 1.5rem 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: {'rgba(213, 0, 50, 0.1)' if 'non fondé' in caractere.lower() else 'rgba(40, 167, 69, 0.1)'}; 
                         width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                        <span style="color: {'#D50032' if 'non fondé' in caractere.lower() else '#28a745'}; font-size: 18px;">
                            {'⚠️' if 'non fondé' in caractere.lower() else '✅'}
                        </span>
                    </div>
                    <div>
                        <div style="color: {'#D50032' if 'non fondé' in caractere.lower() else '#28a745'}; font-weight: 700; font-size: 15px;">
                            Caractère de la réclamation
                        </div>
                        <div style="color: #4b5563; font-size: 14px; margin-top: 4px;">
                            {caractere}
                        </div>
                    </div>
                </div>
                <div class="badge {'badge-primary' if 'non fondé' in caractere.lower() else 'badge-success'}" 
                     style="font-size: 11px; padding: 5px 12px;">
                    {caractere}
                </div>
            </div>
            {"<div style='margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(213, 0, 50, 0.1);'>"
             "<div style='color: #D50032; font-size: 13px; font-weight: 600;'>"
             "⚠️ Contactez votre gestionnaire de compte pour tout justificatif"
             "</div></div>" 
             if 'non fondé' in caractere.lower() else ""}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Section Suivi du traitement
    st.markdown("""
    <div class="card-modern fade-in-up">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 2rem;">
            <div style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                <span style="color: white; font-size: 20px;">🔄</span>
            </div>
            <div>
                <h2 style="color: #111827; margin: 0; font-weight: 800; font-size: 20px;">
                    Suivi du traitement
                </h2>
                <p style="color: #6b7280; margin: 4px 0 0 0; font-size: 13px;">
                    Visualisez l'avancement de votre dossier
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    render_timeline_simple(etat, steps)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Section Feedback fluide
    if etat in ["A Terminer", "Résolue", "Traitée"]:
        avg_rating, num_reviews = get_average_rating(ref_out)
        
        st.markdown(f"""
        <div class="card-modern fade-in-up">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1.5rem;">
                <div style="background: linear-gradient(135deg, #f59e0b, #d97706); width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                    <span style="color: white; font-size: 20px;">⭐</span>
                </div>
                <div>
                    <h2 style="color: #111827; margin: 0; font-weight: 800; font-size: 20px;">
                        Évaluation du service
                    </h2>
                    <p style="color: #6b7280; margin: 4px 0 0 0; font-size: 13px;">
                        Partagez votre expérience avec nous
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Vérifier si un feedback existe déjà
        has_feedback = ref_out in st.session_state.feedback_data and st.session_state.feedback_data[ref_out]
        
        if has_feedback:
            current_rating = st.session_state.current_rating.get(ref_out, 0)
            if current_rating > 0:
                stars_display = "★" * current_rating + "☆" * (5 - current_rating)
                st.markdown(f"""
                <div class="success-message-premium">
                    <div style="font-size: 28px;">✅</div>
                    <div>
                        <div style="font-weight: 700; margin-bottom: 4px;">Merci pour votre évaluation !</div>
                        <div style="font-size: 14px; color: rgba(40, 167, 69, 0.9);">
                            Votre feedback est précieux pour nous améliorer
                        </div>
                    </div>
                </div>
                <div style="text-align: center; padding: 1.5rem; background: rgba(255, 193, 7, 0.05); border-radius: 16px; margin: 1rem 0;">
                    <div style="font-size: 32px; color: #ffc107; letter-spacing: 3px; margin-bottom: 10px;">
                        {stars_display}
                    </div>
                    <div style="font-size: 16px; color: #4b5563; font-weight: 600;">
                        {current_rating}/5 étoile{'s' if current_rating > 1 else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Afficher le système d'étoiles fluide
            st.markdown("### Comment évaluez-vous le traitement ?")
            
            # Étoiles interactives
            rating = render_star_rating_fluid(ref_out, 5)
            
            # Zone de commentaire
            comment = st.text_area(
                "💬 Votre commentaire (optionnel)",
                placeholder="Partagez votre expérience, suggestions ou remarques...",
                height=100,
                key=f"comment_{ref_out}"
            )
            
            # Bouton de soumission
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📤 Soumettre mon évaluation", type="primary", use_container_width=True, key=f"submit_{ref_out}"):
                    if rating > 0:
                        save_feedback(ref_out, rating, comment)
                        st.success("✅ Merci ! Votre évaluation a été enregistrée.")
                        st.balloons()
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.warning("Veuillez sélectionner une note avant de soumettre")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Ressources utiles
    st.markdown("""
    <div class="card-modern fade-in-up">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1.5rem;">
            <div style="background: linear-gradient(135deg, #8b5cf6, #7c3aed); width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                <span style="color: white; font-size: 20px;">📚</span>
            </div>
            <div>
                <h2 style="color: #111827; margin: 0; font-weight: 800; font-size: 20px;">
                    Ressources utiles
                </h2>
                <p style="color: #6b7280; margin: 4px 0 0 0; font-size: 13px;">
                    Accédez à nos services en ligne
                </p>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 1.5rem;">
            <a href="https://particuliers.societegenerale.ci/fr/reclamation/" 
               target="_blank" 
               style="text-decoration: none;">
                <div style="background: white; border: 2px solid #e5e7eb; border-radius: 16px; padding: 1.5rem; transition: all 0.3s ease; height: 100%;">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                        <div style="background: rgba(213, 0, 50, 0.1); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                            <span style="color: #D50032; font-size: 20px;">🔗</span>
                        </div>
                        <h3 style="color: #111827; margin: 0; font-weight: 700; font-size: 16px;">
                            Espace client
                        </h3>
                    </div>
                    <p style="color: #6b7280; font-size: 14px; line-height: 1.5; margin-bottom: 15px;">
                        Accédez à votre espace personnel pour consulter vos documents.
                    </p>
                    <div style="color: #D50032; font-weight: 600; font-size: 14px; display: flex; align-items: center; gap: 6px;">
                        Visiter l'espace <span style="font-size: 18px;">→</span>
                    </div>
                </div>
            </a>
            
            <a href="https://particuliers.societegenerale.ci/fr/faq/" 
               target="_blank" 
               style="text-decoration: none;">
                <div style="background: white; border: 2px solid #e5e7eb; border-radius: 16px; padding: 1.5rem; transition: all 0.3s ease; height: 100%;">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                        <div style="background: rgba(213, 0, 50, 0.1); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                            <span style="color: #D50032; font-size: 20px;">📋</span>
                        </div>
                        <h3 style="color: #111827; margin: 0; font-weight: 700; font-size: 16px;">
                            Centre d'aide
                        </h3>
                    </div>
                    <p style="color: #6b7280; font-size: 14px; line-height: 1.5; margin-bottom: 15px;">
                        Consultez notre FAQ et guides pratiques.
                    </p>
                    <div style="color: #D50032; font-weight: 600; font-size: 14px; display: flex; align-items: center; gap: 6px;">
                        Consulter la FAQ <span style="font-size: 18px;">→</span>
                    </div>
                </div>
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Carte de contact premium
    st.markdown("""
    <div class="contact-card-premium">
        <div style="position: relative; z-index: 2;">
            <h3 style="color: white; margin: 0; font-weight: 800; font-size: 22px;">
                📞 Besoin d'assistance ?
            </h3>
            <p style="color: rgba(255, 255, 255, 0.9); margin: 12px 0 20px 0; font-size: 15px;">
                Notre équipe de conseillers dédiés est à votre écoute
            </p>
            <div class="phone-number-premium">27 20 20 10 10</div>
            <p style="color: rgba(255, 255, 255, 0.8); font-size: 13px; margin-top: 20px;">
                📅 Du lundi au vendredi : 8h00 - 18h00<br>
                📅 Samedi : 9h00 - 13h00
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Footer simplifié
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding: 2.5rem 0; color: #6b7280; border-top: 1px solid #e5e7eb;">
    <p style="margin: 0; font-weight: 600; font-size: 13px; letter-spacing: 0.3px;">
        © 2026 Société Générale Côte d'Ivoire. Tous droits réservés.
    </p>
    <div style="display: flex; justify-content: center; gap: 20px; margin-top: 12px; font-size: 12px;">
        <a href="https://particuliers.societegenerale.ci/fr/mentions-legales/" 
           style="color: #6b7280; text-decoration: none; font-weight: 500;">
            Mentions légales
        </a>
        <a href="https://particuliers.societegenerale.ci/fr/confidentialite/" 
           style="color: #6b7280; text-decoration: none; font-weight: 500;">
            Confidentialité
        </a>
        <a href="https://particuliers.societegenerale.ci/fr/contact/" 
           style="color: #6b7280; text-decoration: none; font-weight: 500;">
            Contact
        </a>
    </div>
</div>
""", unsafe_allow_html=True)
