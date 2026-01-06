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
# STYLE CSS PREMIUM
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
        background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
        padding-bottom: 50px;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
    }
    
    /* Responsive Container */
    .responsive-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 20px;
    }
    
    /* Header Glass Effect */
    .header-glass {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(213, 0, 50, 0.1);
        padding: 1.2rem 0;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
        position: sticky;
        top: 0;
        z-index: 1000;
    }
    
    /* Neomorphic Cards */
    .card-neo {
        background: linear-gradient(145deg, #ffffff, #f5f7fa);
        border-radius: 24px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 20px 20px 60px #d9dce1, -20px -20px 60px #ffffff;
        border: 1px solid rgba(213, 0, 50, 0.08);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .card-neo:hover {
        transform: translateY(-5px);
        box-shadow: 25px 25px 80px #d0d3d8, -25px -25px 80px #ffffff;
        border-color: rgba(213, 0, 50, 0.15);
    }
    
    /* Premium Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #D50032 0%, #B0002A 100%);
        color: white;
        border: none;
        padding: 14px 32px;
        border-radius: 50px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 24px rgba(213, 0, 50, 0.3);
        width: 100%;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(213, 0, 50, 0.4);
        background: linear-gradient(135deg, #B0002A 0%, #900022 100%);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        border-radius: 16px;
        border: 2px solid #e9ecef;
        padding: 16px 20px;
        font-size: 16px;
        transition: all 0.3s ease;
        background: white;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #D50032;
        box-shadow: 0 0 0 4px rgba(213, 0, 50, 0.1), inset 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Timeline Container */
    .timeline-container {
        position: relative;
        padding: 50px 20px;
        margin: 2rem 0;
    }
    
    .timeline-line {
        position: absolute;
        top: 50%;
        left: 50px;
        right: 50px;
        height: 6px;
        background: linear-gradient(90deg, #28a745 0%, #D50032 50%, #e9ecef 50%, #e9ecef 100%);
        transform: translateY(-50%);
        z-index: 1;
        border-radius: 3px;
        overflow: hidden;
    }
    
    .timeline-progress {
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        background: linear-gradient(90deg, #28a745, #D50032);
        border-radius: 3px;
        transition: width 1.5s ease-in-out;
        box-shadow: 0 0 20px rgba(213, 0, 50, 0.3);
    }
    
    .timeline-step {
        position: relative;
        z-index: 2;
        text-align: center;
        padding: 0 15px;
    }
    
    .timeline-bullet {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: white;
        border: 4px solid #e9ecef;
        margin: 0 auto 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        font-weight: 700;
        color: #6c757d;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        position: relative;
    }
    
    .timeline-bullet.completed {
        background: linear-gradient(135deg, #28a745, #20c997);
        border-color: #28a745;
        color: white;
        box-shadow: 0 0 0 10px rgba(40, 167, 69, 0.15), 0 4px 12px rgba(40, 167, 69, 0.3);
        transform: scale(1.1);
    }
    
    .timeline-bullet.active {
        background: linear-gradient(135deg, #FF1654, #D50032);
        border-color: #D50032;
        color: white;
        box-shadow: 0 0 0 12px rgba(213, 0, 50, 0.2), 0 4px 20px rgba(213, 0, 50, 0.4);
        animation: pulse 2s infinite;
        transform: scale(1.2);
    }
    
    .timeline-bullet.pending {
        background: white;
        border-color: #e9ecef;
        color: #adb5bd;
    }
    
    @keyframes pulse {
        0%, 100% { 
            box-shadow: 0 0 0 12px rgba(213, 0, 50, 0.2), 0 4px 20px rgba(213, 0, 50, 0.4);
        }
        50% { 
            box-shadow: 0 0 0 20px rgba(213, 0, 50, 0.1), 0 4px 20px rgba(213, 0, 50, 0.4);
        }
    }
    
    .timeline-label {
        font-size: 14px;
        font-weight: 600;
        color: #495057;
        margin-top: 10px;
        line-height: 1.4;
        transition: all 0.3s ease;
    }
    
    .timeline-label.active {
        color: #D50032;
        font-weight: 700;
        transform: translateY(-2px);
    }
    
    .timeline-label.completed {
        color: #28a745;
    }
    
    /* Star Rating System */
    .star-rating-container {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin: 30px 0 20px;
        padding: 20px;
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        border-radius: 20px;
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .star-button {
        background: none;
        border: none;
        font-size: 48px;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        padding: 0;
        line-height: 1;
        position: relative;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
    }
    
    .star-button:hover {
        transform: scale(1.3) rotate(-10deg);
    }
    
    .star-button.active {
        color: #ffc107;
        animation: starPop 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        transform: scale(1.2);
        filter: drop-shadow(0 0 20px rgba(255, 193, 7, 0.5));
    }
    
    .star-button.inactive {
        color: #e4e5e9;
    }
    
    @keyframes starPop {
        0% { transform: scale(1); }
        50% { transform: scale(1.5) rotate(15deg); }
        100% { transform: scale(1.2); }
    }
    
    .rating-display {
        text-align: center;
        font-size: 24px;
        font-weight: 700;
        margin: 10px 0;
        color: #495057;
    }
    
    .rating-display span {
        color: #ffc107;
        text-shadow: 0 0 10px rgba(255, 193, 7, 0.3);
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 8px 20px;
        border-radius: 24px;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    .badge-primary {
        background: linear-gradient(135deg, rgba(213, 0, 50, 0.15), rgba(213, 0, 50, 0.25));
        color: #D50032;
        border: 2px solid rgba(213, 0, 50, 0.3);
        box-shadow: 0 4px 12px rgba(213, 0, 50, 0.1);
    }
    
    .badge-success {
        background: linear-gradient(135deg, rgba(40, 167, 69, 0.15), rgba(40, 167, 69, 0.25));
        color: #28a745;
        border: 2px solid rgba(40, 167, 69, 0.3);
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.1);
    }
    
    /* Info Grid */
    .info-grid {
        background: rgba(248, 249, 250, 0.7);
        padding: 2rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .info-row {
        display: grid;
        grid-template-columns: 180px 1fr;
        gap: 20px;
        padding: 16px 0;
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        align-items: center;
    }
    
    .info-row:last-child {
        border-bottom: none;
    }
    
    .info-label {
        font-weight: 600;
        color: #495057;
        font-size: 15px;
    }
    
    .info-value {
        color: #212529;
        font-weight: 500;
        font-size: 15px;
    }
    
    /* Contact Card */
    .contact-card {
        background: linear-gradient(135deg, #D50032 0%, #B0002A 100%);
        border-radius: 24px;
        padding: 3rem;
        color: white;
        text-align: center;
        margin: 3rem 0;
        box-shadow: 0 25px 60px rgba(213, 0, 50, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .contact-card::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .phone-number {
        font-size: 3.5rem;
        font-weight: 900;
        margin: 20px 0;
        letter-spacing: 2px;
        position: relative;
        z-index: 1;
        text-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    /* Resource Cards */
    .resource-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        padding: 2rem;
        border-radius: 20px;
        transition: all 0.3s ease;
        border: 1px solid rgba(0, 0, 0, 0.05);
        height: 100%;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
    }
    
    .resource-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.1);
        border-color: rgba(213, 0, 50, 0.2);
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(40px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #D50032 0%, #B0002A 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #B0002A 0%, #900022 100%);
    }
    
    /* Success Message */
    .success-message {
        background: linear-gradient(135deg, rgba(40, 167, 69, 0.1), rgba(40, 167, 69, 0.05));
        border-left: 4px solid #28a745;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 2rem 0;
        color: #28a745;
        font-weight: 600;
        animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Status Colors */
    .status-dot {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        vertical-align: middle;
    }
    
    .status-active { background: #D50032; }
    .status-completed { background: #28a745; }
    .status-pending { background: #e9ecef; }
    
    /* Grid Layout */
    .grid-2-col {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 24px;
        margin: 2rem 0;
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

def render_timeline_progress(status: str, steps_data: List[Dict[str, Any]]):
    """Affiche une timeline de progression professionnelle"""
    
    # Ordre des statuts définitif
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
    
    # Créer la timeline HTML
    timeline_html = f"""
    <div class="timeline-container">
        <div class="timeline-line">
            <div class="timeline-progress" style="width: {progress_pct}%"></div>
        </div>
        <div style="display: flex; justify-content: space-between; position: relative; z-index: 2;">
    """
    
    for i, step in enumerate(available_statuses):
        bullet_class = "pending"
        label_class = ""
        
        if i < current_index:
            bullet_class = "completed"
            label_class = "completed"
            icon = "✓"
        elif i == current_index:
            bullet_class = "active"
            label_class = "active"
            icon = "⏳"
        else:
            bullet_class = "pending"
            icon = f"{i+1}"
        
        timeline_html += f"""
            <div class="timeline-step">
                <div class="timeline-bullet {bullet_class}">{icon}</div>
                <div class="timeline-label {label_class}">{step}</div>
            </div>
        """
    
    timeline_html += "</div></div>"
    
    # Affichage de la progression
    st.markdown(f"""
    <div style="text-align: center; margin: 2rem 0;">
        <h3 style="color: #495057; margin-bottom: 1rem;">Progression du traitement</h3>
        <div style="font-size: 3rem; font-weight: 800; color: #D50032; margin: 1rem 0;">
            {int(progress_pct)}%
        </div>
        <div style="color: #6c757d; font-size: 14px;">
            {current_index + 1} sur {len(available_statuses)} étapes complétées
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(timeline_html, unsafe_allow_html=True)
    
    # Légende
    st.markdown("""
    <div style="display: flex; justify-content: center; gap: 30px; margin-top: 2rem; flex-wrap: wrap;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div class="timeline-bullet completed" style="width: 20px; height: 20px; margin: 0;">✓</div>
            <span style="color: #28a745; font-weight: 600;">Terminé</span>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <div class="timeline-bullet active" style="width: 20px; height: 20px; margin: 0; animation: none;">⏳</div>
            <span style="color: #D50032; font-weight: 600;">En cours</span>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <div class="timeline-bullet pending" style="width: 20px; height: 20px; margin: 0;">•</div>
            <span style="color: #adb5bd; font-weight: 600;">À venir</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_star_rating_interactive(reference: str, max_stars: int = 5):
    """Affiche et gère un système d'étoiles interactif"""
    
    # Initialiser la note si nécessaire
    if reference not in st.session_state.current_rating:
        st.session_state.current_rating[reference] = 0
    
    # Vérifier si un feedback a déjà été soumis
    has_submitted = st.session_state.submitted_feedback.get(reference, False)
    current_rating = st.session_state.current_rating[reference]
    
    # Afficher les étoiles
    st.markdown('<div class="star-rating-container">', unsafe_allow_html=True)
    
    # Créer les colonnes pour les étoiles
    cols = st.columns(max_stars)
    
    for i in range(max_stars):
        with cols[i]:
            star_value = i + 1
            star_emoji = "★" if star_value <= current_rating else "☆"
            
            # Si feedback déjà soumis, désactiver les étoiles
            if has_submitted:
                st.markdown(f'<div style="text-align: center;"><span style="font-size: 48px; color: {"#ffc107" if star_value <= current_rating else "#e4e5e9"};">{star_emoji}</span></div>', 
                           unsafe_allow_html=True)
            else:
                if st.button(f"★", key=f"star_{reference}_{i}", 
                           help=f"Noter {star_value} étoile{'s' if star_value > 1 else ''}",
                           use_container_width=True):
                    st.session_state.current_rating[reference] = star_value
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Afficher la note actuelle
    if current_rating > 0:
        stars = "★" * current_rating + "☆" * (max_stars - current_rating)
        st.markdown(f"""
        <div class="rating-display">
            <span>{stars}</span>
            <div style="font-size: 16px; color: #6c757d; margin-top: 10px;">
                {current_rating}/{max_stars} étoile{'s' if current_rating > 1 else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align: center; color: #6c757d; margin-top: 20px;">Cliquez sur les étoiles pour noter</div>', 
                   unsafe_allow_html=True)
    
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
# INTERFACE PRINCIPALE
# =========================================================

# Header avec logo
st.markdown("""
<div class="header-glass">
    <div class="responsive-container">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 24px;">
                <img src="https://particuliers.societegenerale.ci/fileadmin/user_upload/logos/SGBCI103_2025.svg" 
                     style="height: 60px; filter: drop-shadow(0 4px 12px rgba(0,0,0,0.1));">
                <div>
                    <h1 style="margin: 0; color: #D50032; font-weight: 900; font-size: 28px; letter-spacing: -0.5px;">
                        Suivi de Réclamation
                    </h1>
                    <p style="margin: 6px 0 0 0; color: #6c757d; font-size: 14px; font-weight: 500;">
                        Service Client - Suivi en temps réel
                    </p>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 13px; color: #6c757d; font-weight: 600; text-transform: uppercase;">Support Client</div>
                <div style="font-size: 26px; font-weight: 900; color: #D50032; letter-spacing: 1px; margin-top: 4px;">
                    27 20 20 10 10
                </div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Contenu principal
st.markdown('<div class="responsive-container fade-in">', unsafe_allow_html=True)

# Section recherche
st.markdown("""
<div class="card-neo" style="max-width: 900px; margin: 0 auto;">
    <h2 style="color: #212529; margin-bottom: 1.5rem; text-align: center; font-weight: 800; font-size: 24px;">
        🔍 Recherche de réclamation
    </h2>
    <p style="text-align: center; color: #6c757d; margin-bottom: 2rem; font-size: 15px; line-height: 1.6;">
        Entrez votre numéro de référence pour suivre l'avancement de votre dossier en temps réel
    </p>
""", unsafe_allow_html=True)

# Interface de recherche
col_search1, col_search2, col_search3 = st.columns([3, 1, 1])
with col_search1:
    reference = st.text_input(" ", 
                            placeholder="Exemple : SGCI 3325G, SGCI-338245",
                            key="search_input",
                            label_visibility="collapsed")
with col_search2:
    search_clicked = st.button("🔎 Rechercher", type="primary", use_container_width=True)
with col_search3:
    if st.button("🔄 Nouvelle recherche", use_container_width=True):
        st.session_state.current_reference = None
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# Affichage des résultats
if search_clicked and reference:
    st.session_state.current_reference = reference
    data = get_claim_data(reference)
    
    if not data:
        st.error("""
        <div style='background: linear-gradient(135deg, rgba(220, 53, 69, 0.1), rgba(220, 53, 69, 0.05)); 
                   border-left: 4px solid #dc3545; padding: 1.5rem; border-radius: 12px; margin: 2rem 0;'>
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="font-size: 24px;">❌</div>
                <div>
                    <strong style="color: #dc3545;">Réclamation introuvable</strong><br>
                    <span style="color: #6c757d;">Veuillez vérifier le numéro de référence et réessayer</span>
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
    <div class="card-neo fade-in">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2.5rem; flex-wrap: wrap; gap: 16px;">
            <div style="flex: 1; min-width: 300px;">
                <h2 style="color: #212529; margin: 0 0 8px 0; font-weight: 800; font-size: 28px;">
                    📋 Réclamation {ref_out}
                </h2>
                <div style="display: flex; align-items: center; gap: 20px; margin-top: 12px; flex-wrap: wrap;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #6c757d; font-size: 14px;">📅 Créée le</span>
                        <span style="font-weight: 600; color: #495057;">{created}</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #6c757d; font-size: 14px;">🔄 Dernière mise à jour</span>
                        <span style="font-weight: 600; color: #495057;">{updated}</span>
                    </div>
                </div>
            </div>
            <div class="badge {'badge-success' if etat in ['Résolue', 'Traitée'] else 'badge-primary'}" 
                 style="font-size: 15px; padding: 10px 24px;">
                {etat}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Grille d'informations en 2 colonnes
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("""
        <h3 style="color: #212529; font-weight: 700; font-size: 18px; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 10px;">
            <span>📄</span> Informations générales
        </h3>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="info-grid">
            <div class="info-row">
                <div class="info-label">Type de réclamation</div>
                <div class="info-value">{type_rec}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Agence concernée</div>
                <div class="info-value">{agence}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Activité</div>
                <div class="info-value">{activite}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Motif</div>
                <div class="info-value">{motif}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_info2:
        st.markdown("""
        <h3 style="color: #212529; font-weight: 700; font-size: 18px; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 10px;">
            <span>📊</span> Détails spécifiques
        </h3>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="info-grid">
            <div class="info-row">
                <div class="info-label">Objet principal</div>
                <div class="info-value">{objet}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Montant concerné</div>
                <div class="info-value">{montant + ' ' + devise if montant else 'Non spécifié'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Caractère de la réclamation
    if caractere and caractere.strip():
        st.markdown(f"""
        <div style="background: {'rgba(213, 0, 50, 0.08)' if 'non fondé' in caractere.lower() else 'rgba(40, 167, 69, 0.08)'}; 
                    border-left: 4px solid {'#D50032' if 'non fondé' in caractere.lower() else '#28a745'}; 
                    padding: 1.5rem; border-radius: 12px; margin: 2rem 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                <div>
                    <strong style="color: {'#D50032' if 'non fondé' in caractere.lower() else '#28a745'}; font-size: 16px;">
                        Caractère de la réclamation
                    </strong>
                    <div style="color: #495057; margin-top: 8px;">
                        {caractere}
                        {"<br><span style='font-size: 14px; color: #D50032; margin-top: 8px; display: block;'>Contactez votre gestionnaire de compte pour tout justificatif</span>" 
                         if 'non fondé' in caractere.lower() else ""}
                    </div>
                </div>
                <div class="badge {'badge-primary' if 'non fondé' in caractere.lower() else 'badge-success'}">
                    {caractere}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Section Suivi du traitement avec timeline
    st.markdown("""
    <div class="card-neo fade-in">
        <h2 style="color: #212529; margin-bottom: 2.5rem; font-weight: 800; font-size: 24px; display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 28px;">🔄</span> Suivi du traitement
        </h2>
    """, unsafe_allow_html=True)
    
    render_timeline_progress(etat, steps)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Section Feedback avec étoiles interactives
    if etat in ["A Terminer", "Résolue", "Traitée"]:
        avg_rating, num_reviews = get_average_rating(ref_out)
        has_submitted = st.session_state.submitted_feedback.get(ref_out, False)
        
        st.markdown(f"""
        <div class="card-neo fade-in">
            <h2 style="color: #212529; margin-bottom: 1.5rem; font-weight: 800; font-size: 24px; display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 28px;">⭐</span> Évaluation du service
            </h2>
        """, unsafe_allow_html=True)
        
        if has_submitted:
            current_rating = st.session_state.current_rating.get(ref_out, 0)
            if current_rating > 0:
                stars_display = "★" * current_rating + "☆" * (5 - current_rating)
                st.markdown(f"""
                <div class="success-message">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px;">
                        <div style="font-size: 24px;">✅</div>
                        <div>
                            <strong>Merci pour votre évaluation !</strong><br>
                            <span style="font-size: 15px;">Votre feedback nous aide à améliorer nos services</span>
                        </div>
                    </div>
                    <div style="text-align: center; margin-top: 20px;">
                        <div style="font-size: 36px; color: #ffc107; letter-spacing: 4px; margin-bottom: 10px;">
                            {stars_display}
                        </div>
                        <div style="font-size: 18px; color: #495057; font-weight: 600;">
                            {current_rating}/5 étoile{'s' if current_rating > 1 else ''}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Afficher les étoiles interactives
            st.markdown("### Comment évaluez-vous le traitement de votre réclamation ?")
            
            # Afficher le système d'étoiles
            rating = render_star_rating_interactive(ref_out, 5)
            
            # Zone de commentaire
            comment = st.text_area(
                "💬 Votre commentaire (optionnel)",
                placeholder="Partagez votre expérience, vos remarques ou suggestions...",
                height=120,
                key=f"comment_{ref_out}"
            )
            
            # Boutons d'action
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button("📤 Soumettre mon évaluation", type="primary", use_container_width=True, key=f"submit_{ref_out}"):
                    if rating > 0:
                        save_feedback(ref_out, rating, comment)
                        st.success("✅ Merci pour votre feedback ! Votre évaluation a été enregistrée.")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning("⚠️ Veuillez sélectionner une note avant de soumettre")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Ressources utiles
    st.markdown("""
    <div class="card-neo fade-in">
        <h2 style="color: #212529; margin-bottom: 2rem; font-weight: 800; font-size: 24px; display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 28px;">📚</span> Ressources utiles
        </h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px;">
            <div class="resource-card">
                <h4 style="color: #212529; margin-top: 0; font-weight: 700; font-size: 18px;">🔗 Espace client</h4>
                <p style="color: #6c757d; font-size: 15px; line-height: 1.6;">
                    Accédez à votre espace personnel pour consulter tous vos documents et services.
                </p>
                <a href="https://particuliers.societegenerale.ci/fr/reclamation/" 
                   target="_blank" 
                   class="resource-link" style="color: #D50032; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; gap: 8px; margin-top: 16px;">
                    Visiter l'espace client <span style="font-size: 18px;">→</span>
                </a>
            </div>
            <div class="resource-card">
                <h4 style="color: #212529; margin-top: 0; font-weight: 700; font-size: 18px;">📋 Centre d'aide</h4>
                <p style="color: #6c757d; font-size: 15px; line-height: 1.6;">
                    Consultez notre FAQ et guides pratiques pour toutes vos questions.
                </p>
                <a href="https://particuliers.societegenerale.ci/fr/faq/" 
                   target="_blank" 
                   class="resource-link" style="color: #D50032; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; gap: 8px; margin-top: 16px;">
                    Consulter la FAQ <span style="font-size: 18px;">→</span>
                </a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Carte de contact
    st.markdown("""
    <div class="contact-card">
        <h3 style="color: white; margin: 0; font-weight: 800; font-size: 24px; position: relative; z-index: 1;">
            📞 Besoin d'assistance ?
        </h3>
        <p style="color: rgba(255, 255, 255, 0.95); margin: 16px 0 24px 0; font-size: 16px; position: relative; z-index: 1;">
            Notre équipe de conseillers dédiés est à votre écoute pour vous accompagner
        </p>
        <div class="phone-number">27 20 20 10 10</div>
        <p style="color: rgba(255, 255, 255, 0.9); font-size: 14px; margin-top: 20px; position: relative; z-index: 1;">
            📅 Du lundi au vendredi : 8h00 - 18h00<br>
            📅 Samedi : 9h00 - 13h00
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 4rem; padding: 3rem 0; color: #6c757d; border-top: 1px solid #e9ecef;">
    <p style="margin: 0; font-weight: 600; font-size: 14px; letter-spacing: 0.5px;">
        © 2025 Société Générale Côte d'Ivoire. Tous droits réservés.
    </p>
    <p style="margin: 16px 0 0 0; font-size: 13px;">
        <a href="https://particuliers.societegenerale.ci/fr/mentions-legales/" 
           style="color: #6c757d; text-decoration: none; margin: 0 12px; transition: color 0.2s; font-weight: 500;">
            Mentions légales
        </a> •
        <a href="https://particuliers.societegenerale.ci/fr/confidentialite/" 
           style="color: #6c757d; text-decoration: none; margin: 0 12px; transition: color 0.2s; font-weight: 500;">
            Confidentialité
        </a> •
        <a href="https://particuliers.societegenerale.ci/fr/contact/" 
           style="color: #6c757d; text-decoration: none; margin: 0 12px; transition: color 0.2s; font-weight: 500;">
            Contact
        </a>
    </p>
</div>
""", unsafe_allow_html=True)
