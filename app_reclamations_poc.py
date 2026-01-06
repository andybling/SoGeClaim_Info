import re
import html
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

import streamlit as st
from dateutil import parser as dtparser
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# =========================================================
# CONFIGURATION ET STYLE PREMIUM
# =========================================================
st.set_page_config(
    page_title="Suivi de Réclamation | Société Générale Côte d'Ivoire",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# CSS personnalisé avec effets premium
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
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
    
    /* Header avec effet de verre */
    .header-glass {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        padding: 1rem 0;
        margin-bottom: 2rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.05);
    }
    
    /* Carte avec effet néomorphique */
    .card-neomorphic {
        background: linear-gradient(145deg, #ffffff, #f0f0f0);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 20px 20px 60px #d9d9d9, -20px -20px 60px #ffffff;
        border: none;
        transition: all 0.3s ease;
    }
    
    .card-neomorphic:hover {
        transform: translateY(-5px);
        box-shadow: 25px 25px 75px #d9d9d9, -25px -25px 75px #ffffff;
    }
    
    /* Bouton premium */
    .stButton > button {
        background: linear-gradient(135deg, #D50032 0%, #B0002A 100%);
        color: white;
        border: none;
        padding: 12px 28px;
        border-radius: 50px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(213, 0, 50, 0.3);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(213, 0, 50, 0.4);
        background: linear-gradient(135deg, #B0002A 0%, #900022 100%);
    }
    
    /* Timeline améliorée */
    .timeline-container {
        position: relative;
        padding: 40px 0;
    }
    
    .timeline-line {
        position: absolute;
        top: 50%;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #D50032, #FF3366);
        transform: translateY(-50%);
        z-index: 1;
        border-radius: 2px;
    }
    
    .timeline-point {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: white;
        border: 4px solid #dee2e6;
        position: relative;
        z-index: 2;
        transition: all 0.3s ease;
    }
    
    .timeline-point.active {
        border-color: #D50032;
        background: #D50032;
        box-shadow: 0 0 0 8px rgba(213, 0, 50, 0.2);
        animation: pulse 2s infinite;
    }
    
    .timeline-point.completed {
        border-color: #28a745;
        background: #28a745;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(213, 0, 50, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(213, 0, 50, 0); }
        100% { box-shadow: 0 0 0 0 rgba(213, 0, 50, 0); }
    }
    
    /* Étoiles interactives */
    .star-rating {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin: 20px 0;
    }
    
    .star {
        font-size: 32px;
        color: #e4e5e9;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .star:hover,
    .star.hovered {
        color: #ffc107;
        transform: scale(1.2);
    }
    
    .star.selected {
        color: #ffc107;
        text-shadow: 0 0 10px rgba(255, 193, 7, 0.5);
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-primary {
        background: rgba(213, 0, 50, 0.1);
        color: #D50032;
    }
    
    .badge-success {
        background: rgba(40, 167, 69, 0.1);
        color: #28a745;
    }
    
    .badge-warning {
        background: rgba(255, 193, 7, 0.1);
        color: #ffc107;
    }
    
    /* Stats cards */
    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #D50032;
        margin: 10px 0;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Contact card */
    .contact-card {
        background: linear-gradient(135deg, #D50032 0%, #B0002A 100%);
        border-radius: 20px;
        padding: 2rem;
        color: white;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(213, 0, 50, 0.2);
    }
    
    .phone-number {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 10px 0;
        letter-spacing: 1px;
    }
    
    /* Scrollbar personnalisée */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #D50032 0%, #B0002A 100%);
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# INITIALISATION DE LA SESSION
# =========================================================
if 'feedback_data' not in st.session_state:
    st.session_state.feedback_data = {}
if 'selected_stars' not in st.session_state:
    st.session_state.selected_stars = 0
if 'current_reference' not in st.session_state:
    st.session_state.current_reference = None

# =========================================================
# FONCTIONS UTILITAIRES
# =========================================================
def clean_html_spaces(x: Any) -> str:
    """Nettoie les caractères HTML et espaces spéciaux."""
    if x is None:
        return ""
    s = str(x)
    s = html.unescape(s)
    s = s.replace("\xa0", " ").replace("\u00a0", " ")
    return re.sub(r"\s+", " ", s).strip()

def parse_date_fr_maybe(x: Any) -> Optional[str]:
    """Parse les dates françaises."""
    s = clean_html_spaces(x)
    if not s:
        return None
    try:
        dt = dtparser.parse(s, dayfirst=True)
        return dt.strftime("%d/%m/%Y à %H:%M")
    except Exception:
        return s

# =========================================================
# COMPOSANTS UI AVANCÉS
# =========================================================
def render_star_rating(max_stars: int = 5) -> int:
    """Affiche un composant d'évaluation par étoiles interactif."""
    cols = st.columns(max_stars)
    rating = 0
    
    # Créer les étoiles
    for i in range(max_stars):
        with cols[i]:
            if st.button("★", key=f"star_{i}", 
                        help=f"Noter {i+1} étoile{'s' if i+1 > 1 else ''}",
                        use_container_width=True):
                st.session_state.selected_stars = i + 1
    
    # Afficher le nombre d'étoiles sélectionnées
    rating = st.session_state.get('selected_stars', 0)
    
    # Afficher les étoiles visuellement
    stars_html = ""
    for i in range(max_stars):
        if i < rating:
            stars_html += '<span style="color: #ffc107; font-size: 24px;">★</span>'
        else:
            stars_html += '<span style="color: #e4e5e9; font-size: 24px;">★</span>'
    
    st.markdown(f'<div style="text-align: center; margin: 10px 0;">{stars_html} ({rating}/5)</div>', 
                unsafe_allow_html=True)
    
    return rating

def save_feedback(reference: str, rating: int, comment: str = ""):
    """Sauvegarde le feedback pour une réclamation."""
    if reference not in st.session_state.feedback_data:
        st.session_state.feedback_data[reference] = []
    
    feedback = {
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'rating': rating,
        'comment': comment
    }
    
    st.session_state.feedback_data[reference].append(feedback)

def get_average_rating(reference: str) -> float:
    """Retourne la note moyenne pour une réclamation."""
    if reference in st.session_state.feedback_data:
        feedbacks = st.session_state.feedback_data[reference]
        if feedbacks:
            return sum(f['rating'] for f in feedbacks) / len(feedbacks)
    return 0.0

def render_timeline(status: str, steps_data: List[Dict[str, Any]]) -> None:
    """Affiche une timeline interactive et visuelle des étapes."""
    
    # Définir l'ordre des statuts
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
    
    # Créer une liste des statuts disponibles dans cette réclamation
    available_statuses = []
    for step in STATUS_FLOW:
        # Vérifier si ce statut existe dans les données
        if any(step in s['step'] for s in steps_data) or step in status:
            available_statuses.append(step)
    
    if not available_statuses:
        st.warning("Aucune information de statut disponible.")
        return
    
    # Déterminer l'index du statut actuel
    current_index = -1
    for i, stat in enumerate(available_statuses):
        if stat in status or status in stat:
            current_index = i
            break
    
    # Créer la timeline avec Plotly
    fig = go.Figure()
    
    # Ajouter les points de la timeline
    x_positions = []
    y_positions = []
    colors = []
    sizes = []
    
    for i, statut in enumerate(available_statuses):
        x_positions.append(i)
        y_positions.append(0)
        
        if i < current_index:
            colors.append('#28a745')  # Complété
            sizes.append(20)
        elif i == current_index:
            colors.append('#D50032')  # Actuel
            sizes.append(25)
        else:
            colors.append('#dee2e6')  # Futur
            sizes.append(15)
    
    # Ajouter les points
    fig.add_trace(go.Scatter(
        x=x_positions,
        y=y_positions,
        mode='markers',
        marker=dict(
            size=sizes,
            color=colors,
            line=dict(width=2, color='white')
        ),
        hoverinfo='text',
        text=[f"<b>{statut}</b><br>Statut {'actuel' if i == current_index else 'terminé' if i < current_index else 'à venir'}" 
              for i, statut in enumerate(available_statuses)],
        textposition="bottom center"
    ))
    
    # Ajouter les lignes de connexion
    for i in range(len(x_positions)-1):
        fig.add_trace(go.Scatter(
            x=[x_positions[i], x_positions[i+1]],
            y=[0, 0],
            mode='lines',
            line=dict(width=3, color='#D50032' if i < current_index else '#dee2e6'),
            hoverinfo='none'
        ))
    
    # Mise en page
    fig.update_layout(
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=True,
            tickmode='array',
            tickvals=list(range(len(available_statuses))),
            ticktext=available_statuses,
            tickangle=45
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),
        height=300,
        margin=dict(l=20, r=20, t=40, b=80),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Inter"
        )
    )
    
    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Légende
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div style="display: flex; align-items: center; gap: 10px;">'
                   '<div style="width: 15px; height: 15px; border-radius: 50%; background: #28a745;"></div>'
                   '<span>Terminé</span></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div style="display: flex; align-items: center; gap: 10px;">'
                   '<div style="width: 15px; height: 15px; border-radius: 50%; background: #D50032; animation: pulse 2s infinite;"></div>'
                   '<span>En cours</span></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div style="display: flex; align-items: center; gap: 10px;">'
                   '<div style="width: 15px; height: 15px; border-radius: 50%; background: #dee2e6;"></div>'
                   '<span>À venir</span></div>', unsafe_allow_html=True)

# =========================================================
# DONNÉES SIMULÉES
# =========================================================
def fetch_reclamation_data(ref: str) -> Optional[Dict[str, Any]]:
    """Récupère les données d'une réclamation."""
    reclamations_db = {
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
    
    # Essayer différentes variantes de la référence
    variants = [ref, ref.upper(), ref.replace("-", " "), ref.replace(" ", "-")]
    for variant in variants:
        if variant in reclamations_db:
            return reclamations_db[variant]
    
    return None

# =========================================================
# INTERFACE UTILISATEUR PRINCIPALE
# =========================================================

# Header avec logo et navigation
st.markdown("""
<div class="header-glass">
    <div style="max-width: 1200px; margin: 0 auto;">
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0 20px;">
            <div style="display: flex; align-items: center; gap: 20px;">
                <img src="https://particuliers.societegenerale.ci/fileadmin/user_upload/logos/SGBCI103_2025.svg" 
                     style="height: 50px;">
                <div>
                    <h1 style="margin: 0; color: #D50032; font-weight: 700;">Suivi de Réclamation</h1>
                    <p style="margin: 5px 0 0 0; color: #6c757d;">Suivez l'avancement de votre réclamation en temps réel</p>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 14px; color: #6c757d;">Service Client</div>
                <div style="font-size: 24px; font-weight: 800; color: #D50032;">27 20 20 10 10</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Contenu principal
st.markdown('<div class="fade-in">', unsafe_allow_html=True)

# Section de recherche
st.markdown("""
<div class="card-neomorphic" style="max-width: 800px; margin: 0 auto;">
    <h2 style="color: #212529; margin-bottom: 1.5rem; text-align: center;">🔍 Suivi de votre réclamation</h2>
    <p style="text-align: center; color: #6c757d; margin-bottom: 2rem;">
        Saisissez votre numéro de référence pour visualiser le statut de votre demande
    </p>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    reference = st.text_input(
        " ",
        placeholder="Exemple : SGCI 3325G ou SGCI-338245",
        key="search_input",
        label_visibility="collapsed"
    )

with col2:
    search_clicked = st.button("🔎 Rechercher", use_container_width=True)

with col3:
    if st.button("🔄 Nouvelle recherche", use_container_width=True):
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# Affichage des résultats
if search_clicked and reference:
    st.session_state.current_reference = reference
    
    # Récupérer les données
    data = fetch_reclamation_data(reference)
    
    if not data:
        st.error("❌ Réclamation non trouvée. Vérifiez le numéro de référence.")
        st.stop()
    
    # Extraire les données
    ref_out = clean_html_spaces(data.get("Réf. Réclamation", reference))
    created = parse_date_fr_maybe(data.get("Date de création")) or "Non disponible"
    updated = parse_date_fr_maybe(data.get("Date dernière modification")) or "Non disponible"
    etat = clean_html_spaces(data.get("Etat", "Non spécifié"))
    type_rec = clean_html_spaces(data.get("Type", "Non spécifié"))
    activite = clean_html_spaces(data.get("Activité", "Non spécifié"))
    motif = clean_html_spaces(data.get("Motif", "Non spécifié"))
    objet = clean_html_spaces(data.get("Objet de la réclamation", "Non spécifié"))
    caractere = clean_html_spaces(data.get("Caractère", ""))
    agence = clean_html_spaces(data.get("Agence", "Non spécifié"))
    montant = clean_html_spaces(data.get("Montant", ""))
    devise = clean_html_spaces(data.get("Dévise du montant", "XOF"))
    
    # Parser le workflow
    sla_raw = data.get("SLA Réclamation", "")
    steps = []
    if sla_raw:
        s = clean_html_spaces(sla_raw).strip("[]")
        for item in s.split(","):
            item = item.strip()
            if ":" in item:
                step, dur = item.split(":", 1)
                step = step.replace("REC -", "").strip()
                steps.append({"step": step, "duration": dur})
    
    # Afficher la carte de réclamation
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    # En-tête de la réclamation
    st.markdown(f"""
    <div class="card-neomorphic" style="margin-top: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1.5rem;">
            <div>
                <h2 style="color: #212529; margin: 0;">📋 Réclamation {ref_out}</h2>
                <p style="color: #6c757d; margin: 5px 0 0 0;">
                    Créée le {created} | Dernière mise à jour : {updated}
                </p>
            </div>
            <div style="text-align: right;">
                <div class="badge badge-primary" style="font-size: 14px; padding: 8px 16px;">
                    {etat}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Informations principales
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("### 📄 Informations générales")
        st.markdown(f"""
        <div style="background: rgba(248, 249, 250, 0.5); padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
            <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 12px; margin-bottom: 12px;">
                <div style="font-weight: 600; color: #495057;">Type :</div>
                <div>{type_rec}</div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 12px; margin-bottom: 12px;">
                <div style="font-weight: 600; color: #495057;">Agence :</div>
                <div>{agence}</div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 12px; margin-bottom: 12px;">
                <div style="font-weight: 600; color: #495057;">Activité :</div>
                <div>{activite}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_b:
        st.markdown("### 📊 Détails spécifiques")
        st.markdown(f"""
        <div style="background: rgba(248, 249, 250, 0.5); padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
            <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 12px; margin-bottom: 12px;">
                <div style="font-weight: 600; color: #495057;">Objet :</div>
                <div>{objet}</div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 12px; margin-bottom: 12px;">
                <div style="font-weight: 600; color: #495057;">Motif :</div>
                <div>{motif}</div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 12px;">
                <div style="font-weight: 600; color: #495057;">Montant :</div>
                <div>{montant} {devise if montant else "Non spécifié"}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Caractère de la réclamation (conditionnel)
    if caractere and caractere.strip():
        st.markdown(f"""
        <div style="background: rgba(213, 0, 50, 0.05); border-left: 4px solid #D50032; padding: 1rem; border-radius: 8px; margin: 1.5rem 0;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="font-weight: 600; color: #D50032;">Caractère de la réclamation :</div>
                <div class="badge {'badge-warning' if 'non fondé' in caractere.lower() else 'badge-primary'}">
                    {caractere}
                </div>
            </div>
            {"<p style='color: #D50032; margin: 10px 0 0 0; font-size: 14px;'>Contactez votre gestionnaire de compte pour tout justificatif de caractère de la réclamation</p>" 
             if 'non fondé' in caractere.lower() else ""}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Timeline de suivi
    st.markdown("""
    <div class="card-neomorphic" style="margin-top: 2rem;">
        <h2 style="color: #212529; margin-bottom: 1.5rem;">🔄 Suivi du traitement</h2>
    """, unsafe_allow_html=True)
    
    render_timeline(etat, steps)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Section Feedback (si statut terminal)
    if etat in ["A Terminer", "Résolue", "Traitée"]:
        avg_rating = get_average_rating(ref_out)
        
        st.markdown(f"""
        <div class="card-neomorphic" style="margin-top: 2rem;">
            <h2 style="color: #212529; margin-bottom: 1rem;">⭐ Évaluation du service</h2>
            {"<p style='color: #28a745; margin-bottom: 1.5rem;'>✅ Vous avez déjà évalué ce service : " + 
             "★" * int(avg_rating) + " (" + str(round(avg_rating, 1)) + "/5)</p>" if avg_rating > 0 else 
             "<p style='color: #6c757d; margin-bottom: 1.5rem;'>Partagez votre expérience pour nous aider à améliorer notre service</p>"}
        """, unsafe_allow_html=True)
        
        with st.form(key=f"feedback_form_{ref_out}"):
            st.markdown("### Comment évaluez-vous le traitement de votre réclamation ?")
            
            # Étoiles interactives
            rating = render_star_rating(5)
            
            # Commentaire
            comment = st.text_area(
                "Votre commentaire (optionnel)",
                placeholder="Partagez vos remarques, suggestions ou expérience...",
                height=100
            )
            
            # Bouton de soumission
            submit_col1, submit_col2 = st.columns([3, 1])
            with submit_col2:
                submitted = st.form_submit_button(
                    "💾 Enregistrer mon avis",
                    type="primary",
                    use_container_width=True
                )
            
            if submitted and rating > 0:
                save_feedback(ref_out, rating, comment)
                st.success("✅ Merci pour votre feedback ! Votre avis a été enregistré.")
                st.balloons()
                st.rerun()
            elif submitted and rating == 0:
                st.warning("Veuillez sélectionner une note avant de soumettre.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Liens et informations supplémentaires
    st.markdown("""
    <div class="card-neomorphic" style="margin-top: 2rem;">
        <h2 style="color: #212529; margin-bottom: 1.5rem;">📚 Ressources complémentaires</h2>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 1rem;">
            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 1.5rem; border-radius: 12px;">
                <h4 style="color: #212529; margin-top: 0;">🔗 Parcours client</h4>
                <p style="color: #6c757d; font-size: 14px;">Accédez à votre espace client pour plus d'informations</p>
                <a href="https://particuliers.societegenerale.ci/fr/reclamation/" 
                   target="_blank" 
                   style="color: #D50032; font-weight: 600; text-decoration: none; display: inline-block; margin-top: 10px;">
                    Visiter l'espace client →
                </a>
            </div>
            
            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 1.5rem; border-radius: 12px;">
                <h4 style="color: #212529; margin-top: 0;">📋 FAQ Réclamations</h4>
                <p style="color: #6c757d; font-size: 14px;">Consultez les questions fréquentes sur les réclamations</p>
                <a href="https://particuliers.societegenerale.ci/fr/faq/" 
                   target="_blank" 
                   style="color: #D50032; font-weight: 600; text-decoration: none; display: inline-block; margin-top: 10px;">
                    Consulter la FAQ →
                </a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Carte de contact
    st.markdown("""
    <div class="contact-card">
        <h3 style="color: white; margin-top: 0; margin-bottom: 1rem;">📞 Besoin d'assistance ?</h3>
        <p style="color: rgba(255, 255, 255, 0.9); margin-bottom: 1.5rem;">
            Notre équipe de conseillers est à votre écoute pour vous accompagner
        </p>
        <div class="phone-number">27 20 20 10 10</div>
        <p style="color: rgba(255, 255, 255, 0.8); font-size: 14px; margin-top: 1rem;">
            Du lundi au vendredi : 8h00 - 18h00 | Samedi : 9h00 - 13h00
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 4rem; padding: 2rem 0; color: #6c757d; border-top: 1px solid #e9ecef;">
    <p style="margin: 0;">© 2024 Société Générale Côte d'Ivoire. Tous droits réservés.</p>
    <p style="margin: 10px 0 0 0; font-size: 14px;">
        <a href="https://particuliers.societegenerale.ci/fr/mentions-legales/" 
           style="color: #6c757d; text-decoration: none; margin: 0 10px;">Mentions légales</a> |
        <a href="https://particuliers.societegenerale.ci/fr/confidentialite/" 
           style="color: #6c757d; text-decoration: none; margin: 0 10px;">Confidentialité</a> |
        <a href="https://particuliers.societegenerale.ci/fr/contact/" 
           style="color: #6c757d; text-decoration: none; margin: 0 10px;">Contact</a>
    </p>
</div>
""", unsafe_allow_html=True)
