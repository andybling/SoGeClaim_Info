import re
import html
from typing import Dict, Any, List, Optional
from datetime import datetime

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
    
    @media (max-width: 768px) {
        .responsive-container {
            padding: 0 12px;
        }
    }
    
    /* Header Glass Effect */
    .header-glass {
        background: rgba(255, 255, 255, 0.95);
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
    
    @media (max-width: 768px) {
        .header-glass {
            padding: 1rem 0;
        }
        
        .header-content {
            flex-direction: column !important;
            gap: 16px !important;
            text-align: center !important;
        }
        
        .header-logo {
            justify-content: center !important;
        }
        
        .header-phone {
            text-align: center !important;
        }
    }
    
    /* Neomorphic Cards */
    .card-neo {
        background: linear-gradient(145deg, #ffffff, #f5f7fa);
        border-radius: 24px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 20px 20px 60px #d9dce1, -20px -20px 60px #ffffff;
        border: none;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @media (max-width: 768px) {
        .card-neo {
            padding: 1.5rem;
            border-radius: 20px;
            margin: 1rem 0;
        }
    }
    
    .card-neo:hover {
        transform: translateY(-5px);
        box-shadow: 25px 25px 80px #d0d3d8, -25px -25px 80px #ffffff;
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
    
    @media (max-width: 768px) {
        .stButton > button {
            padding: 12px 24px;
            font-size: 15px;
        }
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(213, 0, 50, 0.4);
        background: linear-gradient(135deg, #B0002A 0%, #900022 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 16px;
        border: 2px solid #e9ecef;
        padding: 14px 20px;
        font-size: 16px;
        transition: all 0.3s ease;
        background: white;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #D50032;
        box-shadow: 0 0 0 4px rgba(213, 0, 50, 0.1);
    }
    
    /* Timeline with Bullets */
    .timeline-wrapper {
        position: relative;
        padding: 40px 0;
        overflow-x: auto;
        overflow-y: hidden;
    }
    
    .timeline-track {
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: relative;
        min-width: 100%;
        padding: 20px 0;
    }
    
    @media (max-width: 768px) {
        .timeline-track {
            flex-direction: column;
            align-items: flex-start;
            padding: 0;
        }
    }
    
    .timeline-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        flex: 1;
        min-width: 120px;
    }
    
    @media (max-width: 768px) {
        .timeline-step {
            flex-direction: row;
            width: 100%;
            min-width: 100%;
            margin: 10px 0;
            align-items: center;
            justify-content: flex-start;
        }
    }
    
    .timeline-bullet {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: white;
        border: 4px solid #dee2e6;
        position: relative;
        z-index: 3;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .timeline-bullet.completed {
        background: linear-gradient(135deg, #28a745, #20c997);
        border-color: #28a745;
        box-shadow: 0 0 0 8px rgba(40, 167, 69, 0.15);
    }
    
    .timeline-bullet.active {
        background: linear-gradient(135deg, #FF1654, #D50032);
        border-color: #D50032;
        box-shadow: 0 0 0 8px rgba(213, 0, 50, 0.2);
        animation: pulse-bullet 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    .timeline-bullet.pending {
        background: white;
        border-color: #dee2e6;
    }
    
    @keyframes pulse-bullet {
        0%, 100% { 
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(213, 0, 50, 0.4);
        }
        50% { 
            transform: scale(1.1);
            box-shadow: 0 0 0 12px rgba(213, 0, 50, 0);
        }
    }
    
    .timeline-connector {
        position: absolute;
        top: 50%;
        left: 0;
        right: 0;
        height: 4px;
        background: #dee2e6;
        z-index: 1;
        transform: translateY(-50%);
    }
    
    @media (max-width: 768px) {
        .timeline-connector {
            display: none;
        }
    }
    
    .timeline-connector.active {
        background: linear-gradient(90deg, #28a745 0%, #D50032 100%);
    }
    
    .timeline-label {
        margin-top: 12px;
        text-align: center;
        font-size: 13px;
        font-weight: 600;
        color: #495057;
        max-width: 120px;
        line-height: 1.3;
    }
    
    @media (max-width: 768px) {
        .timeline-label {
            margin-top: 0;
            margin-left: 16px;
            text-align: left;
            max-width: none;
            flex: 1;
        }
    }
    
    .timeline-label.active {
        color: #D50032;
        font-weight: 700;
    }
    
    .timeline-label.completed {
        color: #28a745;
    }
    
    /* Progress Bar */
    .progress-container {
        width: 100%;
        height: 8px;
        background: #e9ecef;
        border-radius: 10px;
        overflow: hidden;
        margin: 20px 0;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #28a745, #D50032);
        border-radius: 10px;
        transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 8px rgba(213, 0, 50, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .progress-bar::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .progress-text {
        text-align: center;
        font-size: 14px;
        font-weight: 600;
        color: #495057;
        margin-top: 8px;
    }
    
    /* Stars - Interactive and Smooth */
    .star-rating-container {
        display: flex;
        justify-content: center;
        gap: 16px;
        margin: 24px 0;
        padding: 20px;
        background: rgba(255, 255, 255, 0.5);
        border-radius: 16px;
    }
    
    @media (max-width: 768px) {
        .star-rating-container {
            gap: 12px;
            padding: 16px;
        }
    }
    
    .star-btn {
        background: none;
        border: none;
        font-size: 48px;
        color: #e4e5e9;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
        padding: 0;
        line-height: 1;
    }
    
    @media (max-width: 768px) {
        .star-btn {
            font-size: 36px;
        }
    }
    
    .star-btn:hover {
        color: #ffc107;
        transform: scale(1.3) rotate(-10deg);
        filter: drop-shadow(0 4px 8px rgba(255, 193, 7, 0.5));
    }
    
    .star-btn.selected {
        color: #ffc107;
        animation: star-pop 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @keyframes star-pop {
        0% { transform: scale(1); }
        50% { transform: scale(1.4) rotate(15deg); }
        100% { transform: scale(1); }
    }
    
    .star-display {
        text-align: center;
        font-size: 18px;
        color: #495057;
        margin-top: 12px;
        font-weight: 600;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 8px 18px;
        border-radius: 24px;
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    @media (max-width: 768px) {
        .badge {
            padding: 6px 14px;
            font-size: 12px;
        }
    }
    
    .badge-primary {
        background: linear-gradient(135deg, rgba(213, 0, 50, 0.15), rgba(213, 0, 50, 0.25));
        color: #D50032;
        border: 2px solid rgba(213, 0, 50, 0.3);
    }
    
    .badge-success {
        background: linear-gradient(135deg, rgba(40, 167, 69, 0.15), rgba(40, 167, 69, 0.25));
        color: #28a745;
        border: 2px solid rgba(40, 167, 69, 0.3);
    }
    
    /* Info Grid */
    .info-grid {
        background: rgba(248, 249, 250, 0.6);
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    @media (max-width: 768px) {
        .info-grid {
            padding: 1rem;
        }
    }
    
    .info-row {
        display: grid;
        grid-template-columns: 140px 1fr;
        gap: 16px;
        padding: 12px 0;
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    @media (max-width: 768px) {
        .info-row {
            grid-template-columns: 1fr;
            gap: 4px;
        }
    }
    
    .info-row:last-child {
        border-bottom: none;
    }
    
    .info-label {
        font-weight: 600;
        color: #495057;
    }
    
    .info-value {
        color: #212529;
    }
    
    /* Contact Card */
    .contact-card {
        background: linear-gradient(135deg, #D50032 0%, #B0002A 100%);
        border-radius: 24px;
        padding: 2.5rem;
        color: white;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 20px 60px rgba(213, 0, 50, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    @media (max-width: 768px) {
        .contact-card {
            padding: 2rem 1.5rem;
        }
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
        font-size: 3rem;
        font-weight: 900;
        margin: 16px 0;
        letter-spacing: 2px;
        position: relative;
        z-index: 1;
    }
    
    @media (max-width: 768px) {
        .phone-number {
            font-size: 2rem;
            letter-spacing: 1px;
        }
    }
    
    /* Resource Cards */
    .resource-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        padding: 2rem;
        border-radius: 16px;
        transition: all 0.3s ease;
        border: 1px solid rgba(0, 0, 0, 0.05);
        height: 100%;
    }
    
    @media (max-width: 768px) {
        .resource-card {
            padding: 1.5rem;
        }
    }
    
    .resource-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
        border-color: rgba(213, 0, 50, 0.2);
    }
    
    .resource-link {
        color: #D50032;
        font-weight: 600;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        margin-top: 12px;
        transition: all 0.2s ease;
    }
    
    .resource-link:hover {
        gap: 12px;
        color: #B0002A;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
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
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #28a745;
        font-weight: 600;
        animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
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
    """Sauvegarde le feedback sans recharger la page"""
    if reference not in st.session_state.feedback_data:
        st.session_state.feedback_data[reference] = []
    
    st.session_state.feedback_data[reference].append({
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'rating': rating,
        'comment': comment
    })

def get_average_rating(reference: str) -> float:
    if reference in st.session_state.feedback_data:
        feedbacks = st.session_state.feedback_data[reference]
        if feedbacks:
            return sum(f['rating'] for f in feedbacks) / len(feedbacks)
    return 0.0

def render_timeline_bullets(status: str, steps_data: List[Dict[str, Any]]):
    """Affiche la timeline avec des bullets selon l'image fournie"""
    
    STATUS_ORDER = [
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
    
    # Filtrer les statuts disponibles
    available = []
    for s in STATUS_ORDER:
        if any(s in step['step'] for step in steps_data) or s in status:
            available.append(s)
    
    if not available:
        st.warning("⚠️ Aucune information de statut disponible")
        return
    
    # Trouver l'index du statut actuel
    current_idx = -1
    for i, s in enumerate(available):
        if s in status or status in s:
            current_idx = i
            break
    
    # Calculer le pourcentage de progression
    progress_pct = ((current_idx + 1) / len(available)) * 100 if current_idx >= 0 else 0
    
    # Afficher la barre de progression
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {progress_pct}%"></div>
    </div>
    <div class="progress-text">Progression : {int(progress_pct)}%</div>
    """, unsafe_allow_html=True)
    
    # Créer la timeline avec bullets
    timeline_html = '<div class="timeline-wrapper"><div class="timeline-track">'
    
    for i, statut in enumerate(available):
        bullet_class = 'pending'
        if i < current_idx:
            bullet_class = 'completed'
        elif i == current_idx:
            bullet_class = 'active'
        
        label_class = bullet_class
        
        timeline_html += f'''
        <div class="timeline-step">
            <div class="timeline-bullet {bullet_class}"></div>
            <div class="timeline-label {label_class}">{statut}</div>
        </div>
        '''
    
    timeline_html += '</div></div>'
    
    st.markdown(timeline_html, unsafe_allow_html=True)

def render_star_rating_interactive(reference: str, max_stars: int = 5):
    """Affiche un système d'étoiles interactif sans recharger la page"""
    
    # Récupérer la note actuelle pour cette réclamation
    current_rating = 0
    if reference in st.session_state.feedback_data:
        feedbacks = st.session_state.feedback_data[reference]
        if feedbacks:
            current_rating = feedbacks[-1]['rating']
    
    # Créer un conteneur pour les étoiles
    star_html = '<div class="star-rating-container">'
    
    for i in range(1, max_stars + 1):
        selected_class = 'selected' if i <= current_rating else ''
        star_html += f'<button class="star-btn {selected_class}" onclick="return false;">★</button>'
    
    star_html += '</div>'
    
    if current_rating > 0:
        star_html += f'<div class="star-display">⭐ {current_rating}/{max_stars} étoiles</div>'
    else:
        star_html += '<div class="star-display">Cliquez sur les étoiles pour noter</div>'
    
    st.markdown(star_html, unsafe_allow_html=True)
    
    return current_rating

def get_claim_data(ref: str) -> Optional[Dict[str, Any]]:
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

# Header
st.markdown("""
<div class="header-glass">
    <div class="responsive-container">
        <div class="header-content" style="display: flex; justify-content: space-between; align-items: center;">
            <div class="header-logo" style="display: flex; align-items: center; gap: 24px;">
                <img src="https://particuliers.societegenerale.ci/fileadmin/user_upload/logos/SGBCI103_2025.svg" 
                     style="height: 50px; filter: drop-shadow(0 2px 8px rgba(0,0,0,0.1));">
                <div>
                    <h1 style="margin: 0; color: #D50032; font-weight: 800; font-size: 26px;">Suivi de Réclamation</h1>
                    <p style="margin: 6px 0 0 0; color: #6c757d; font-size: 14px;">Suivez l'avancement en temps réel</p>
                </div>
            </div>
            <div class="header-phone" style="text-align: right;">
                <div style="font-size: 13px; color: #6c757d; font-weight: 500;">Service Client</div>
                <div style="font-size: 24px; font-weight: 900; color: #D50032; letter-spacing: 1px;">27 20 20 10 10</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="fade-in responsive-container">', unsafe_allow_html=True)

# Search Section
st.markdown("""
<div class="card-neo" style="max-width: 850px; margin: 0 auto;">
    <h2 style="color: #212529; margin-bottom: 1.5rem; text-align: center; font-weight: 700;">🔍 Rechercher votre réclamation</h2>
    <p style="text-align: center; color: #6c757d; margin-bottom: 2rem; font-size: 15px;">
        Saisissez votre numéro de référence pour visualiser le statut détaillé
    </p>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    reference = st.text_input(" ", placeholder="Ex: SGCI 3325G ou SGCI-338245", key="ref", label_visibility="collapsed")
with col2:
    search = st.button("🔎 Rechercher", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# Results
if search and reference:
    st.session_state.current_reference = reference
    data = get_claim_data(reference)
    
    if not data:
        st.error("❌ Réclamation introuvable. Vérifiez la référence.")
        st.stop()
    
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
    
    sla = data.get("SLA Réclamation", "")
    steps = []
    if sla:
        s = clean_html_spaces(sla).strip("[]")
        for item in s.split(","):
            item = item.strip()
            if ":" in item:
                step, dur = item.split(":", 1)
                steps.append({"step": step.replace("REC -", "").strip(), "duration": dur})
    
    # Claim Card
    st.markdown(f"""
    <div class="card-neo fade-in" style="margin-top: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 2rem; flex-wrap: wrap; gap: 16px;">
            <div style="flex: 1; min-width: 250px;">
                <h2 style="color: #212529; margin: 0; font-weight: 800;">📋 Réclamation {ref_out}</h2>
                <p style="color: #6c757d; margin: 8px 0 0 0; font-size: 14px;">
                    Créée le {created} • Mis à jour : {updated}
                </p>
            </div>
            <div class="badge badge-primary">{etat}</div>
        </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.markdown(f"""
        <h3 style="color: #212529; font-weight: 700; font-size: 18px;">📄 Informations générales</h3>
        <div class="info-grid">
            <div class="info-row">
                <div class="info-label">Type :</div>
                <div class="info-value">{type_rec}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Agence :</div>
                <div class="info-value">{agence}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Activité :</div>
                <div class="info-value">{activite}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_b:
        st.markdown(f"""
        <h3 style="color: #212529; font-weight: 700; font-size: 18px;">📊 Détails spécifiques</h3>
        <div class="info-grid">
            <div class="info-row">
                <div class="info-label">Objet :</div>
                <div class="info-value">{objet}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Motif :</div>
                <div class="info-value">{motif}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Montant :</div>
                <div class="info-value">{montant + ' ' + devise if montant else 'Non spécifié'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if caractere:
        badge_class = 'badge-success' if 'fondé' in caractere.lower() and 'non' not in caractere.lower() else 'badge-primary'
        st.markdown(f"""
        <div style="background: rgba(213, 0, 50, 0.06); border-left: 4px solid #D50032; padding: 1.2rem; border-radius: 12px; margin: 1.5rem 0;">
            <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                <strong style="color: #D50032;">Caractère :</strong>
                <span class="badge {badge_class}">{caractere}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Timeline avec Bullets
    st.markdown("""
    <div class="card-neo fade-in" style="margin-top: 2rem;">
        <h2 style="color: #212529; margin-bottom: 2rem; font-weight: 800;">🔄 Suivi du traitement</h2>
    """, unsafe_allow_html=True)
    
    render_timeline_bullets(etat, steps)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Feedback Section
    if etat in ["A Terminer", "Résolue", "Traitée"]:
        avg = get_average_rating(ref_out)
        
        st.markdown(f"""
        <div class="card-neo fade-in" style="margin-top: 2rem;">
            <h2 style="color: #212529; margin-bottom: 1rem; font-weight: 800;">⭐ Évaluation du service</h2>
            {"<div class='success-message'>✅ Merci ! Vous avez déjà évalué ce service : " + "★" * int(avg) + " (" + str(round(avg, 1)) + "/5)</div>" if avg > 0 else "<p style='color: #6c757d; margin-bottom: 1.5rem;'>Partagez votre expérience</p>"}
        """, unsafe_allow_html=True)
        
        st.markdown("### Comment évaluez-vous le traitement ?")
        
        # Étoiles interactives
        cols = st.columns(5)
        rating = 0
        
        for i in range(5):
            with cols[i]:
                if st.button("★", key=f"star_{ref_out}_{i}", help=f"{i+1} étoile{'s' if i+1 > 1 else ''}", use_container_width=True):
                    rating = i + 1
        
        # Afficher les étoiles sélectionnées
        if avg > 0:
            stars_display = "★" * int(avg) + "☆" * (5 - int(avg))
            st.markdown(f"<div class='star-display'>{stars_display} ({round(avg, 1)}/5)</div>", unsafe_allow_html=True)
        elif rating > 0:
            stars_display = "★" * rating + "☆" * (5 - rating)
            st.markdown(f"<div class='star-display'>{stars_display} ({rating}/5)</div>", unsafe_allow_html=True)
        
        comment = st.text_area("💬 Commentaire (optionnel)", placeholder="Partagez vos remarques...", height=100, key=f"comment_{ref_out}")
        
        col_s1, col_s2, col_s3 = st.columns([2, 1, 2])
        with col_s2:
            if st.button("💾 Enregistrer", type="primary", use_container_width=True, key=f"submit_{ref_out}"):
                if rating > 0:
                    save_feedback(ref_out, rating, comment)
                    st.success("✅ Merci pour votre feedback !")
                    st.balloons()
                else:
                    st.warning("⚠️ Veuillez sélectionner une note")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Resources
    st.markdown("""
    <div class="card-neo fade-in" style="margin-top: 2rem;">
        <h2 style="color: #212529; margin-bottom: 2rem; font-weight: 800;">📚 Ressources utiles</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px;">
            <div class="resource-card">
                <h4 style="color: #212529; margin-top: 0; font-weight: 700;">🔗 Parcours client</h4>
                <p style="color: #6c757d; font-size: 14px;">Accédez à votre espace personnel</p>
                <a href="https://particuliers.societegenerale.ci/fr/reclamation/" target="_blank" class="resource-link">
                    Visiter →
                </a>
            </div>
            <div class="resource-card">
                <h4 style="color: #212529; margin-top: 0; font-weight: 700;">📋 FAQ</h4>
                <p style="color: #6c757d; font-size: 14px;">Questions fréquentes</p>
                <a href="https://particuliers.societegenerale.ci/fr/faq/" target="_blank" class="resource-link">
                    Consulter →
                </a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Contact
    st.markdown("""
    <div class="contact-card">
        <h3 style="color: white; margin: 0; font-weight: 800; font-size: 22px; position: relative; z-index: 1;">📞 Besoin d'aide ?</h3>
        <p style="color: rgba(255, 255, 255, 0.95); margin: 12px 0 20px 0; position: relative; z-index: 1; font-size: 15px;">
            Notre équipe est à votre écoute
        </p>
        <div class="phone-number">27 20 20 10 10</div>
        <p style="color: rgba(255, 255, 255, 0.85); font-size: 13px; margin-top: 16px; position: relative; z-index: 1;">
            Lun-Ven : 8h-18h • Sam : 9h-13h
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 4rem; padding: 2.5rem 0; color: #6c757d; border-top: 1px solid #e9ecef;">
    <p style="margin: 0; font-weight: 500;">© 2025 Société Générale Côte d'Ivoire. Tous droits réservés.</p>
    <p style="margin: 12px 0 0 0; font-size: 13px;">
        <a href="https://particuliers.societegenerale.ci/fr/mentions-legales/" style="color: #6c757d; text-decoration: none; margin: 0 12px; transition: color 0.2s;">Mentions légales</a> •
        <a href="https://particuliers.societegenerale.ci/fr/confidentialite/" style="color: #6c757d; text-decoration: none; margin: 0 12px; transition: color 0.2s;">Confidentialité</a> •
        <a href="https://particuliers.societegenerale.ci/fr/contact/" style="color: #6c757d; text-decoration: none; margin: 0 12px; transition: color 0.2s;">Contact</a>
    </p>
</div>
""", unsafe_allow_html=True)
