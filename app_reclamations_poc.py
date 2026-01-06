import re
import html
from typing import Dict, Any, List, Optional
from datetime import datetime

import streamlit as st
from dateutil import parser as dtparser
import plotly.graph_objects as go

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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding-bottom: 50px;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Header Glass Effect */
    .header-glass {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(213, 0, 50, 0.1);
        padding: 1.5rem 0;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        position: sticky;
        top: 0;
        z-index: 1000;
    }
    
    /* Neomorphic Cards */
    .card-neo {
        background: linear-gradient(145deg, #ffffff, #f0f0f0);
        border-radius: 24px;
        padding: 2.5rem;
        margin: 1.5rem 0;
        box-shadow: 20px 20px 60px #d9d9d9, -20px -20px 60px #ffffff;
        border: none;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .card-neo:hover {
        transform: translateY(-8px);
        box-shadow: 25px 25px 80px #d0d0d0, -25px -25px 80px #ffffff;
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
        transform: translateY(-3px);
        box-shadow: 0 12px 32px rgba(213, 0, 50, 0.4);
        background: linear-gradient(135deg, #B0002A 0%, #900022 100%);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        border-radius: 16px;
        border: 2px solid #e9ecef;
        padding: 14px 20px;
        font-size: 16px;
        transition: all 0.3s ease;
        background: white;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #D50032;
        box-shadow: 0 0 0 4px rgba(213, 0, 50, 0.1);
    }
    
    /* Pulse Animation */
    @keyframes pulse {
        0% { 
            box-shadow: 0 0 0 0 rgba(213, 0, 50, 0.5);
            transform: scale(1);
        }
        50% {
            box-shadow: 0 0 0 12px rgba(213, 0, 50, 0);
            transform: scale(1.05);
        }
        100% { 
            box-shadow: 0 0 0 0 rgba(213, 0, 50, 0);
            transform: scale(1);
        }
    }
    
    .pulse-dot {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* Fade In Animation */
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
    
    /* Stars */
    .star-container {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin: 24px 0;
    }
    
    .star {
        font-size: 40px;
        color: #e4e5e9;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
    }
    
    .star:hover {
        color: #ffc107;
        transform: scale(1.3) rotate(-10deg);
        filter: drop-shadow(0 4px 8px rgba(255, 193, 7, 0.4));
    }
    
    .star.selected {
        color: #ffc107;
        animation: starPop 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @keyframes starPop {
        0% { transform: scale(1); }
        50% { transform: scale(1.4); }
        100% { transform: scale(1); }
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 24px;
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
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
    
    .info-row {
        display: grid;
        grid-template-columns: 140px 1fr;
        gap: 16px;
        padding: 12px 0;
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
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
    
    /* Timeline Legend */
    .legend-item {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 14px;
        color: #495057;
    }
    
    .legend-dot {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Resource Cards */
    .resource-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        padding: 2rem;
        border-radius: 16px;
        transition: all 0.3s ease;
        border: 1px solid rgba(0, 0, 0, 0.05);
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
    
    /* Loading Animation */
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    .loading {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 1000px 100%;
        animation: shimmer 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# INITIALISATION SESSION
# =========================================================
if 'feedback_data' not in st.session_state:
    st.session_state.feedback_data = {}
if 'selected_stars' not in st.session_state:
    st.session_state.selected_stars = 0

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

def render_stars(rating: int, max_stars: int = 5) -> str:
    stars_html = '<div class="star-container">'
    for i in range(max_stars):
        if i < rating:
            stars_html += '<span class="star selected">★</span>'
        else:
            stars_html += '<span class="star">★</span>'
    stars_html += f'</div><p style="text-align: center; color: #6c757d; margin-top: -10px;">({rating}/{max_stars})</p>'
    return stars_html

def save_feedback(reference: str, rating: int, comment: str = ""):
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

def render_timeline(status: str, steps_data: List[Dict[str, Any]]):
    STATUS_ORDER = [
        "Initialisation", "Etude Technique", "Traitement",
        "Infos complémentaires", "Attente retour tiers",
        "En cours de régularisation", "Valider Regularisation",
        "Traitée", "A Terminer", "Résolue"
    ]
    
    available = [s for s in STATUS_ORDER if any(s in step['step'] for step in steps_data) or s in status]
    
    if not available:
        st.warning("⚠️ Aucune information de statut disponible")
        return
    
    current_idx = -1
    for i, s in enumerate(available):
        if s in status or status in s:
            current_idx = i
            break
    
    fig = go.Figure()
    
    x_pos = list(range(len(available)))
    y_pos = [0] * len(available)
    colors = []
    sizes = []
    
    for i in range(len(available)):
        if i < current_idx:
            colors.append('#28a745')
            sizes.append(20)
        elif i == current_idx:
            colors.append('#D50032')
            sizes.append(30)
        else:
            colors.append('#dee2e6')
            sizes.append(16)
    
    fig.add_trace(go.Scatter(
        x=x_pos, y=y_pos,
        mode='markers',
        marker=dict(size=sizes, color=colors, line=dict(width=3, color='white')),
        hovertemplate='<b>%{text}</b><extra></extra>',
        text=[f"{s}<br>{'✅ Terminé' if i < current_idx else '🔄 En cours' if i == current_idx else '⏳ À venir'}"
              for i, s in enumerate(available)],
        showlegend=False
    ))
    
    for i in range(len(x_pos)-1):
        fig.add_trace(go.Scatter(
            x=[x_pos[i], x_pos[i+1]], y=[0, 0],
            mode='lines',
            line=dict(width=4, color='#D50032' if i < current_idx else '#dee2e6'),
            hoverinfo='none',
            showlegend=False
        ))
    
    fig.update_layout(
        showlegend=False,
        xaxis=dict(
            showgrid=False, zeroline=False,
            tickmode='array', tickvals=x_pos, ticktext=available,
            tickangle=45, tickfont=dict(size=11, color='#495057')
        ),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=320,
        margin=dict(l=20, r=20, t=40, b=100),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(bgcolor="white", font_size=13, font_family="Inter")
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="legend-item"><div class="legend-dot" style="background: #28a745;"></div>Terminé</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="legend-item"><div class="legend-dot pulse-dot" style="background: #D50032;"></div>En cours</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="legend-item"><div class="legend-dot" style="background: #dee2e6;"></div>À venir</div>', unsafe_allow_html=True)

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
    <div style="max-width: 1200px; margin: 0 auto; padding: 0 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 24px;">
                <img src="https://particuliers.societegenerale.ci/fileadmin/user_upload/logos/SGBCI103_2025.svg" 
                     style="height: 55px; filter: drop-shadow(0 2px 8px rgba(0,0,0,0.1));">
                <div>
                    <h1 style="margin: 0; color: #D50032; font-weight: 800; font-size: 28px;">Suivi de Réclamation</h1>
                    <p style="margin: 6px 0 0 0; color: #6c757d; font-size: 14px;">Suivez l'avancement en temps réel</p>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 13px; color: #6c757d; font-weight: 500;">Service Client</div>
                <div style="font-size: 26px; font-weight: 900; color: #D50032; letter-spacing: 1px;">27 20 20 10 10</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="fade-in">', unsafe_allow_html=True)

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
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 2rem;">
            <div>
                <h2 style="color: #212529; margin: 0; font-weight: 800;">📋 Réclamation {ref_out}</h2>
                <p style="color: #6c757d; margin: 8px 0 0 0; font-size: 14px;">
                    Créée le {created} • Mis à jour : {updated}
                </p>
            </div>
            <div class="badge badge-primary">{etat}</div>
        </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    
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
            <div style="display: flex; align-items: center; gap: 12px;">
                <strong style="color: #D50032;">Caractère :</strong>
                <span class="badge {badge_class}">{caractere}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Timeline
    st.markdown("""
    <div class="card-neo fade-in" style="margin-top: 2rem;">
        <h2 style="color: #212529; margin-bottom: 2rem; font-weight: 800;">🔄 Suivi du traitement</h2>
    """, unsafe_allow_html=True)
    
    render_timeline(etat, steps)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Feedback
    if etat in ["A Terminer", "Résolue", "Traitée"]:
        avg = get_average_rating(ref_out)
        
        st.markdown(f"""
        <div class="card-neo fade-in" style="margin-top: 2rem;">
            <h2 style="color: #212529; margin-bottom: 1rem; font-weight: 800;">⭐ Évaluation du service</h2>
            {"<div style='background: rgba(40, 167, 69, 0.1); border-left: 4px solid #28a745; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;'><p style='color: #28a745; margin: 0;'>✅ Vous avez déjà évalué : " + "★" * int(avg) + " (" + str(round(avg, 1)) + "/5)</p></div>" if avg > 0 else "<p style='color: #6c757d; margin-bottom: 1.5rem;'>Partagez votre expérience</p>"}
        """, unsafe_allow_html=True)
        
        with st.form(key=f"form_{ref_out}"):
            st.markdown("### Comment évaluez-vous le traitement ?")
            
            cols_star = st.columns(5)
            rating = 0
            for i in range(5):
                with cols_star[i]:
                    if st.form_submit_button("★", key=f"s_{i}", use_container_width=True):
                        rating = i + 1
                        st.session_state.selected_stars = rating
            
            if st.session_state.selected_stars > 0:
                st.markdown(render_stars(st.session_state.selected_stars), unsafe_allow_html=True)
            
            comment = st.text_area("Commentaire (optionnel)", placeholder="Partagez vos remarques...", height=100)
            
            col_s1, col_s2 = st.columns([3, 1])
            with col_s2:
                submit = st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True)
            
            if submit:
                if st.session_state.selected_stars > 0:
                    save_feedback(ref_out, st.session_state.selected_stars, comment)
                    st.success("✅ Merci pour votre feedback !")
                    st.balloons()
                    st.session_state.selected_stars = 0
                    st.rerun()
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
                <p style="color: #6c757d; font-size: 14px;">Questions fréquentes sur les réclamations</p>
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
