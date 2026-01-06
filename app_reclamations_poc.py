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
# STYLE CSS PREMIUM EXACTEMENT COMME L'IMAGE
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
    
    .main {
        background: #f8f9fa;
        padding-bottom: 30px;
    }
    
    .stApp {
        background: #f8f9fa;
    }
    
    /* Container principal */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 15px;
    }
    
    /* Header */
    .app-header {
        background: white;
        padding: 20px 0;
        border-bottom: 2px solid #e9ecef;
        margin-bottom: 30px;
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .logo-img {
        height: 45px;
    }
    
    .app-title {
        color: #D50032;
        font-weight: 800;
        font-size: 24px;
        margin: 0;
        line-height: 1.2;
    }
    
    .app-subtitle {
        color: #6c757d;
        font-size: 13px;
        font-weight: 500;
        margin: 3px 0 0 0;
    }
    
    .contact-info {
        text-align: right;
    }
    
    .contact-label {
        font-size: 12px;
        color: #6c757d;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .contact-number {
        font-size: 22px;
        font-weight: 800;
        color: #D50032;
        margin-top: 2px;
        letter-spacing: 1px;
    }
    
    /* Carte de réclamation */
    .claim-card {
        background: white;
        border-radius: 12px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e9ecef;
    }
    
    .claim-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 25px;
        padding-bottom: 20px;
        border-bottom: 1px solid #e9ecef;
    }
    
    .claim-title {
        color: #212529;
        font-weight: 700;
        font-size: 22px;
        margin: 0 0 8px 0;
    }
    
    .claim-date {
        display: flex;
        gap: 25px;
        color: #6c757d;
        font-size: 14px;
    }
    
    .date-item {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .status-badge {
        background: linear-gradient(135deg, #D50032 0%, #B0002A 100%);
        color: white;
        padding: 8px 24px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 14px;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 12px rgba(213, 0, 50, 0.2);
    }
    
    .status-badge.resolved {
        background: linear-gradient(135deg, #28a745 0%, #218838 100%);
    }
    
    /* Informations Grid */
    .info-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        margin: 25px 0;
    }
    
    .info-section {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
    }
    
    .section-title {
        color: #212529;
        font-weight: 600;
        font-size: 16px;
        margin: 0 0 15px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .info-item {
        display: grid;
        grid-template-columns: 180px 1fr;
        gap: 15px;
        padding: 12px 0;
        border-bottom: 1px solid #e9ecef;
        align-items: center;
    }
    
    .info-item:last-child {
        border-bottom: none;
    }
    
    .info-label {
        color: #495057;
        font-weight: 600;
        font-size: 14px;
    }
    
    .info-value {
        color: #212529;
        font-weight: 500;
        font-size: 14px;
    }
    
    /* Caractère de la réclamation */
    .character-section {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 25px 0;
        border-left: 4px solid #D50032;
    }
    
    .character-badge {
        display: inline-block;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 14px;
        margin-top: 10px;
    }
    
    .character-badge.founded {
        background: linear-gradient(135deg, rgba(40, 167, 69, 0.15), rgba(40, 167, 69, 0.25));
        color: #28a745;
        border: 2px solid rgba(40, 167, 69, 0.3);
    }
    
    .character-badge.not-founded {
        background: linear-gradient(135deg, rgba(213, 0, 50, 0.15), rgba(213, 0, 50, 0.25));
        color: #D50032;
        border: 2px solid rgba(213, 0, 50, 0.3);
    }
    
    /* TIMELINE EXACTEMENT COMME L'IMAGE */
    .timeline-section {
        background: white;
        border-radius: 12px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e9ecef;
    }
    
    .timeline-title {
        color: #212529;
        font-weight: 700;
        font-size: 20px;
        margin: 0 0 30px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .timeline-container {
        position: relative;
        padding: 40px 0 30px 0;
        margin: 20px 0;
    }
    
    .timeline-line {
        position: absolute;
        top: 30px;
        left: 40px;
        right: 40px;
        height: 3px;
        background: #e9ecef;
        z-index: 1;
    }
    
    .timeline-progress {
        position: absolute;
        top: 30px;
        left: 40px;
        height: 3px;
        background: #28a745;
        z-index: 2;
        transition: width 1.5s ease;
    }
    
    .timeline-steps {
        display: flex;
        justify-content: space-between;
        position: relative;
        z-index: 3;
        margin: 0 30px;
    }
    
    .timeline-step {
        position: relative;
        text-align: center;
        min-width: 120px;
    }
    
    .step-number {
        position: absolute;
        top: -35px;
        left: 50%;
        transform: translateX(-50%);
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: white;
        border: 2px solid #e9ecef;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 14px;
        color: #6c757d;
        z-index: 4;
    }
    
    .step-number.completed {
        background: #28a745;
        border-color: #28a745;
        color: white;
    }
    
    .step-number.active {
        background: #D50032;
        border-color: #D50032;
        color: white;
    }
    
    .step-dot {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: white;
        border: 3px solid #e9ecef;
        margin: 0 auto 12px;
        position: relative;
        z-index: 4;
        box-shadow: 0 0 0 5px white;
    }
    
    .step-dot.completed {
        background: #28a745;
        border-color: #28a745;
        box-shadow: 0 0 0 5px white, 0 0 0 8px rgba(40, 167, 69, 0.1);
    }
    
    .step-dot.active {
        background: #D50032;
        border-color: #D50032;
        box-shadow: 0 0 0 5px white, 0 0 0 8px rgba(213, 0, 50, 0.1);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% {
            box-shadow: 0 0 0 5px white, 0 0 0 8px rgba(213, 0, 50, 0.1);
        }
        50% {
            box-shadow: 0 0 0 5px white, 0 0 0 12px rgba(213, 0, 50, 0.05);
        }
        100% {
            box-shadow: 0 0 0 5px white, 0 0 0 8px rgba(213, 0, 50, 0.1);
        }
    }
    
    .step-label {
        font-size: 13px;
        font-weight: 600;
        color: #6c757d;
        line-height: 1.3;
        text-align: center;
        min-height: 35px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .step-label.active {
        color: #D50032;
        font-weight: 700;
    }
    
    .step-label.completed {
        color: #28a745;
    }
    
    /* Section de progression */
    .progress-section {
        text-align: center;
        margin: 25px 0 15px 0;
        padding: 20px;
        background: #f8f9fa;
        border-radius: 10px;
    }
    
    .progress-percentage {
        font-size: 42px;
        font-weight: 800;
        color: #D50032;
        margin: 5px 0;
    }
    
    .progress-text {
        color: #6c757d;
        font-size: 14px;
        margin-top: 8px;
    }
    
    /* Section feedback */
    .feedback-section {
        background: white;
        border-radius: 12px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e9ecef;
    }
    
    .star-container {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin: 25px 0 15px;
    }
    
    .star-button {
        background: none;
        border: none;
        font-size: 40px;
        cursor: pointer;
        padding: 0;
        line-height: 1;
        transition: transform 0.2s;
    }
    
    .star-button:hover {
        transform: scale(1.2);
    }
    
    .star-button.active {
        color: #ffc107;
    }
    
    .star-button.inactive {
        color: #e9ecef;
    }
    
    .rating-text {
        text-align: center;
        font-size: 18px;
        font-weight: 600;
        color: #495057;
        margin-top: 10px;
    }
    
    /* Section contact */
    .contact-section {
        background: linear-gradient(135deg, #D50032 0%, #B0002A 100%);
        border-radius: 12px;
        padding: 30px;
        margin: 30px 0;
        color: white;
        text-align: center;
    }
    
    .contact-title {
        font-size: 22px;
        font-weight: 700;
        margin: 0 0 15px 0;
    }
    
    .contact-phone {
        font-size: 32px;
        font-weight: 800;
        margin: 15px 0;
        letter-spacing: 1px;
    }
    
    /* Section recherche */
    .search-section {
        background: white;
        border-radius: 12px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e9ecef;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .search-title {
        text-align: center;
        color: #212529;
        font-weight: 700;
        font-size: 20px;
        margin: 0 0 15px 0;
    }
    
    .search-description {
        text-align: center;
        color: #6c757d;
        font-size: 14px;
        margin: 0 0 25px 0;
        line-height: 1.5;
    }
    
    /* Boutons */
    .stButton > button {
        background: linear-gradient(135deg, #D50032 0%, #B0002A 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(213, 0, 50, 0.3);
    }
    
    /* Input */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #e9ecef;
        padding: 12px 16px;
        font-size: 14px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #D50032;
        box-shadow: 0 0 0 3px rgba(213, 0, 50, 0.1);
    }
    
    /* Message d'erreur */
    .error-message {
        background: #fee;
        border-left: 4px solid #dc3545;
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
        color: #721c24;
    }
    
    /* Footer */
    .app-footer {
        text-align: center;
        margin-top: 40px;
        padding: 25px 0;
        color: #6c757d;
        border-top: 1px solid #e9ecef;
        font-size: 13px;
    }
    
    .footer-links {
        margin-top: 10px;
    }
    
    .footer-links a {
        color: #6c757d;
        text-decoration: none;
        margin: 0 10px;
        transition: color 0.2s;
    }
    
    .footer-links a:hover {
        color: #D50032;
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
if 'submitted_feedback' not in st.session_state:
    st.session_state.submitted_feedback = {}

# =========================================================
# FONCTIONS UTILITAIRES
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
    st.session_state.submitted_feedback[reference] = True
    st.session_state.current_rating[reference] = rating

def get_average_rating(reference: str) -> Tuple[float, int]:
    """Retourne la note moyenne et le nombre d'avis"""
    if reference in st.session_state.feedback_data:
        feedbacks = st.session_state.feedback_data[reference]
        if feedbacks:
            total = sum(f['rating'] for f in feedbacks)
            return total / len(feedbacks), len(feedbacks)
    return 0.0, 0

def render_timeline_exact(status: str):
    """Affiche la timeline exactement comme sur l'image"""
    
    # Définition des étapes EXACTEMENT comme sur l'image
    steps = [
        "Étude technique",
        "Initialisation",
        "Traitement",
        "Traitée",
        "Valider régularisation",
        "En cours de régularisation",
        "A terminer",
        "Résolue"
    ]
    
    # Déterminer l'index de l'étape actuelle
    current_step = status
    current_index = -1
    
    # Recherche de correspondance
    for i, step in enumerate(steps):
        if step.lower() == current_step.lower() or current_step.lower() in step.lower():
            current_index = i
            break
    
    # Si non trouvé, essayer avec d'autres formats
    if current_index == -1:
        status_mapping = {
            "étude technique": 0,
            "initialisation": 1,
            "traitement": 2,
            "traitée": 3,
            "valider régularisation": 4,
            "valider regularisation": 4,
            "en cours de régularisation": 5,
            "a terminer": 6,
            "résolue": 7,
            "resolue": 7
        }
        
        for key, value in status_mapping.items():
            if key in current_step.lower():
                current_index = value
                break
    
    # Calcul de la progression
    if current_index >= 0:
        progress_percentage = ((current_index + 1) / len(steps)) * 100
        progress_width = f"calc({progress_percentage}% - 80px)"
    else:
        progress_width = "0px"
        current_index = 0
    
    # Générer le HTML de la timeline
    timeline_html = f"""
    <div class="timeline-container">
        <div class="timeline-line"></div>
        <div class="timeline-progress" style="width: {progress_width};"></div>
        <div class="timeline-steps">
    """
    
    for i, step in enumerate(steps):
        step_class = ""
        number_class = ""
        dot_class = ""
        label_class = ""
        
        if i < current_index:
            step_class = "completed"
            number_class = "completed"
            dot_class = "completed"
            label_class = "completed"
            number = "✓"
        elif i == current_index:
            step_class = "active"
            number_class = "active"
            dot_class = "active"
            label_class = "active"
            number = str(i + 1)
        else:
            step_class = ""
            number = str(i + 1)
        
        timeline_html += f"""
            <div class="timeline-step">
                <div class="step-number {number_class}">{number}</div>
                <div class="step-dot {dot_class}"></div>
                <div class="step-label {label_class}">{step}</div>
            </div>
        """
    
    timeline_html += "</div></div>"
    
    # Afficher la section de progression
    st.markdown(f"""
    <div class="progress-section">
        <div style="font-size: 15px; color: #6c757d; font-weight: 600;">Progression du traitement</div>
        <div class="progress-percentage">{int(progress_percentage) if current_index >= 0 else 0}%</div>
        <div class="progress-text">
            {current_index + 1 if current_index >= 0 else 0} sur {len(steps)} étapes complétées
            <br>
            Statut actuel : <strong style="color: #D50032;">{steps[current_index] if current_index >= 0 else 'Non déterminé'}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Afficher la timeline
    st.markdown(timeline_html, unsafe_allow_html=True)

def render_star_rating(reference: str):
    """Affiche le système d'étoiles pour l'évaluation"""
    
    current_rating = st.session_state.current_rating.get(reference, 0)
    has_submitted = st.session_state.submitted_feedback.get(reference, False)
    
    # Afficher les étoiles
    st.markdown('<div class="star-container">', unsafe_allow_html=True)
    
    cols = st.columns(5)
    
    for i in range(5):
        with cols[i]:
            star_value = i + 1
            
            if has_submitted:
                # Mode lecture seule
                is_active = star_value <= current_rating
                emoji = "★" if is_active else "☆"
                color = "#ffc107" if is_active else "#e9ecef"
                st.markdown(f'<div style="font-size: 40px; color: {color}; text-align: center;">{emoji}</div>', 
                           unsafe_allow_html=True)
            else:
                # Mode interactif
                if st.button(f"★", key=f"star_{reference}_{i}", 
                           help=f"Noter {star_value} étoile{'s' if star_value > 1 else ''}",
                           use_container_width=True):
                    st.session_state.current_rating[reference] = star_value
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Afficher la note
    if current_rating > 0:
        st.markdown(f"""
        <div class="rating-text">
            {"★" * current_rating}{"☆" * (5 - current_rating)}
            <div style="font-size: 14px; color: #6c757d; margin-top: 5px;">
                {current_rating}/5 étoile{'s' if current_rating > 1 else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    return current_rating

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
            "Caractère": "Fondée",  # Modifié comme demandé
            "Agence": "00111 PLATEAU",
            "Montant": "10000",
            "Dévise du montant": "XOF",
        },
        "SGCI-338245": {
            "Réf. Réclamation": "SGCI-338245",
            "Date de création": "18-12-2024 13:16:36",
            "Date dernière modification": "19-12-2024 11:00:00",
            "Etat": "A terminer",
            "Type": "Monetique",
            "Activité": "Retrait GAB SG",
            "Motif": "RETRAIT CONTESTE-NON RECONNU",
            "Objet de la réclamation": "Retrait DAB contesté",
            "Caractère": "Non fondée",  # Modifié comme demandé
            "Agence": "00111-PLATEAU",
            "Montant": "100000",
            "Dévise du montant": "XOF",
        }
    }
    
    for variant in [ref, ref.upper(), ref.replace("-", " "), ref.replace(" ", "-")]:
        if variant in db:
            return db[variant]
    return None

# =========================================================
# INTERFACE PRINCIPALE
# =========================================================

# Header
st.markdown("""
<div class="app-header">
    <div class="main-container">
        <div class="header-content">
            <div class="logo-section">
                <img src="https://particuliers.societegenerale.ci/fileadmin/user_upload/logos/SGBCI103_2025.svg" 
                     class="logo-img">
                <div>
                    <h1 class="app-title">Suivi de Réclamation</h1>
                    <p class="app-subtitle">Service Client - Suivi en temps réel</p>
                </div>
            </div>
            <div class="contact-info">
                <div class="contact-label">Support Client</div>
                <div class="contact-number">27 20 20 10 10</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Contenu principal
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Section recherche
st.markdown("""
<div class="search-section">
    <h2 class="search-title">🔍 Recherche de réclamation</h2>
    <p class="search-description">
        Entrez votre numéro de référence pour suivre l'avancement de votre dossier en temps réel
    </p>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    reference = st.text_input(" ", 
                            placeholder="Exemple : SGCI 3325G, SGCI-338245",
                            key="search_input",
                            label_visibility="collapsed")
with col2:
    search_clicked = st.button("🔎 Rechercher", type="primary", use_container_width=True)
with col3:
    if st.button("🔄 Nouvelle recherche", use_container_width=True):
        st.session_state.current_reference = None
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# Affichage des résultats
if search_clicked and reference:
    st.session_state.current_reference = reference
    data = get_claim_data(reference)
    
    if not data:
        st.markdown("""
        <div class="error-message">
            <strong>❌ Réclamation introuvable</strong><br>
            Veuillez vérifier le numéro de référence et réessayer
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
    
    # Carte principale de la réclamation
    st.markdown(f"""
    <div class="claim-card">
        <div class="claim-header">
            <div>
                <h2 class="claim-title">📋 Réclamation {ref_out}</h2>
                <div class="claim-date">
                    <div class="date-item">📅 Créée le {created}</div>
                    <div class="date-item">🔄 Dernière mise à jour {updated}</div>
                </div>
            </div>
            <div class="status-badge{' resolved' if etat in ['Résolue', 'Traitée', 'A terminer'] else ''}">
                {etat}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Grille d'informations
    st.markdown('<div class="info-grid">', unsafe_allow_html=True)
    
    # Colonne gauche
    st.markdown("""
    <div class="info-section">
        <h3 class="section-title">📄 Informations générales</h3>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="info-item">
            <div class="info-label">Type de réclamation</div>
            <div class="info-value">{type_rec}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Agence concernée</div>
            <div class="info-value">{agence}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Activité</div>
            <div class="info-value">{activite}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Motif</div>
            <div class="info-value">{motif}</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Colonne droite
    st.markdown("""
    <div class="info-section">
        <h3 class="section-title">📊 Détails spécifiques</h3>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="info-item">
            <div class="info-label">Objet principal</div>
            <div class="info-value">{objet}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Montant concerné</div>
            <div class="info-value">{montant + ' ' + devise if montant else 'Non spécifié'}</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Caractère de la réclamation
    if caractere:
        is_founded = "fondée" in caractere.lower()
        
        st.markdown(f"""
        <div class="character-section">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>Caractère de la réclamation</strong>
                    <div style="margin-top: 8px; color: #495057;">La réclamation est jugée {caractere.lower()}</div>
                    {"<div style='font-size: 13px; color: #D50032; margin-top: 8px;'>Contactez votre gestionnaire de compte pour tout justificatif</div>" 
                     if not is_founded else ""}
                </div>
                <div class="character-badge{' founded' if is_founded else ' not-founded'}">
                    {caractere}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Section Suivi du traitement avec timeline exacte
    st.markdown("""
    <div class="timeline-section">
        <h2 class="timeline-title">🔄 Suivi du traitement</h2>
    """, unsafe_allow_html=True)
    
    render_timeline_exact(etat)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Section Feedback
    if etat in ["A terminer", "Résolue", "Traitée"]:
        avg_rating, num_reviews = get_average_rating(ref_out)
        has_submitted = st.session_state.submitted_feedback.get(ref_out, False)
        
        st.markdown("""
        <div class="feedback-section">
            <h2 class="timeline-title">⭐ Évaluation du service</h2>
        """, unsafe_allow_html=True)
        
        if has_submitted:
            current_rating = st.session_state.current_rating.get(ref_out, 0)
            if current_rating > 0:
                stars = "★" * current_rating + "☆" * (5 - current_rating)
                st.markdown(f"""
                <div style="background: #f0f9f0; border-left: 4px solid #28a745; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                        <div style="font-size: 24px;">✅</div>
                        <div>
                            <strong>Merci pour votre évaluation !</strong><br>
                            <span style="font-size: 14px; color: #6c757d;">Votre feedback nous aide à améliorer nos services</span>
                        </div>
                    </div>
                    <div style="text-align: center; margin-top: 15px;">
                        <div style="font-size: 32px; color: #ffc107; letter-spacing: 3px; margin-bottom: 8px;">
                            {stars}
                        </div>
                        <div style="font-size: 16px; color: #495057; font-weight: 600;">
                            {current_rating}/5 étoile{'s' if current_rating > 1 else ''}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Afficher les étoiles interactives
            st.markdown("#### Comment évaluez-vous le traitement de votre réclamation ?")
            
            rating = render_star_rating(ref_out)
            
            # Zone de commentaire
            comment = st.text_area(
                "💬 Votre commentaire (optionnel)",
                placeholder="Partagez votre expérience, vos remarques ou suggestions...",
                height=100,
                key=f"comment_{ref_out}"
            )
            
            # Bouton de soumission
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button("📤 Soumettre mon évaluation", type="primary", use_container_width=True, key=f"submit_{ref_out}"):
                    if rating > 0:
                        save_feedback(ref_out, rating, comment)
                        st.success("✅ Merci pour votre feedback ! Votre évaluation a été enregistrée.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning("⚠️ Veuillez sélectionner une note avant de soumettre")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Section Contact
    st.markdown("""
    <div class="contact-section">
        <h3 class="contact-title">📞 Besoin d'assistance ?</h3>
        <p style="margin: 0 0 15px 0; opacity: 0.95; font-size: 15px;">
            Notre équipe de conseillers dédiés est à votre écoute pour vous accompagner
        </p>
        <div class="contact-phone">27 20 20 10 10</div>
        <div style="font-size: 14px; opacity: 0.9; margin-top: 15px;">
            📅 Du lundi au vendredi : 8h00 - 18h00<br>
            📅 Samedi : 9h00 - 13h00
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="app-footer">
    <div style="font-weight: 600; margin-bottom: 10px;">
        © 2025 Société Générale Côte d'Ivoire. Tous droits réservés.
    </div>
    <div class="footer-links">
        <a href="https://particuliers.societegenerale.ci/fr/mentions-legales/" target="_blank">Mentions légales</a> •
        <a href="https://particuliers.societegenerale.ci/fr/confidentialite/" target="_blank">Confidentialité</a> •
        <a href="https://particuliers.societegenerale.ci/fr/contact/" target="_blank">Contact</a>
    </div>
</div>
""", unsafe_allow_html=True)
