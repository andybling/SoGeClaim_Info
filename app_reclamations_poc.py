
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

st.markdown(
    """
    <style>
      /* Réduction marges pour un rendu propre sur mobile */
      .block-container { padding-top: 2rem; padding-bottom: 2rem; }
      /* Légère amélioration des titres */
      h1, h2, h3 { letter-spacing: -0.2px; }
      /* Cards workflow */
      .wf-card {
        border-radius: 14px;
        padding: 10px 10px;
        text-align: center;
        font-size: 0.85rem;
        line-height: 1.2rem;
        box-shadow: 0 1px 8px rgba(0,0,0,0.06);
        margin-bottom: 10px;
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
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🆑 Suivi de Réclamation SGCI")
st.caption("Saisissez votre référence de réclamation pour suivre l’avancement. (Lecture seule)")


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
            "Etat": "Valider Regularisation",
            "Type": "Monetique",
            "Activité": "Retrait GAB SG",
            "Motif": "RETRAIT CONTESTE-NON RECONNU",
            "Objet de la réclamation": "Retrait DAB contesté",
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
            "Canal de réception": "Agence",
            "Agence": "00225-YAMOUSSOUKRO",
            "Montant": "5000",
            "Dévise du montant": "XOF",
            "SLA Réclamation": "[REC - Traitement:1h 15m 0s, REC - SUPPORT:30m 0s]",
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
    "A Terminer": "#adb5bd",
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
# MAIN - UI CLIENT
# =========================================================
st.markdown("#### 🔎 Rechercher ma réclamation")
ref = st.text_input("Référence de réclamation", placeholder="Ex : SGCI-338245").strip()

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
    canal = clean_html_spaces(data.get("Canal de réception"))
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

    # Bandeau récap
    st.markdown("### 🧾 Résumé de la réclamation")
    a, b, c = st.columns(3)
    with a:
        st.markdown("**Référence**")
        st.write(ref_out or ref)
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

    # Détails essentiels (sans PII)
    st.markdown("### 📌 Détails")
    d1, d2 = st.columns(2)
    with d1:
        st.write(f"**Type :** {type_rec or '—'}")
        st.write(f"**Activité :** {activite or '—'}")
        st.write(f"**Motif :** {motif or '—'}")
        st.write(f"**Canal :** {canal or '—'}")
    with d2:
        st.write(f"**Agence :** {agence or '—'}")
        st.write(f"**Objet :** {objet or '—'}")
        if montant:
            st.write(f"**Montant :** {montant} {devise}".strip())
        else:
            st.write("**Montant :** —")

    st.divider()

    # Workflow
    render_workflow(status=status, steps=steps)

    # Note client-safe
    st.info("🔒 Pour protéger vos données, cette page n’affiche aucune information personnelle (nom, compte, téléphone).")

    # Debug POC
    #with st.expander("🔍 Debug POC (optionnel)"):
     #   st.write("SLA Réclamation (raw) :", data.get("SLA Réclamation"))
      #  st.write("Steps parsed :", steps)



