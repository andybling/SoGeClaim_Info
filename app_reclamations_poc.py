
import re
import io
import html
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import streamlit as st
from dateutil import parser as dtparser


# =========================================================
# CONFIG APP
# =========================================================
st.set_page_config(page_title="SGCI | POC Réclamations", page_icon="🟦", layout="wide")

APP_TITLE = "🟦 SGCI | POC Suivi Réclamation (V0/V1)"
APP_SUBTITLE = "V0 : données en dur | V1 : import Excel/CSV et recherche par Réf. Réclamation"


# =========================================================
# WORKFLOW / STATUTS
# =========================================================
STATUSES_ORDER = [
    "SUPPORT",
    "Traitement",
    "Etude Technique",
    "Infos complémentaires",
    "Attente retour tiers",
    "En cours de régularisation",
    "Valider Regularisation",
    "Traitée",
    "A Terminer",
    "Initialisation",
    "Résolue",
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

# Mapping des colonnes "Temps ..." => étapes
TIME_COLUMNS_MAP = {
    "Temps\nEtude Technique": "Etude Technique",
    "Temps\nInfos complémentaires": "Infos complémentaires",
    "Temps\nTraitement": "Traitement",
    "Temps\nSUPPORT": "SUPPORT",
    "Temps\nTraitée": "Traitée",
    "Temps\nA Terminer": "A Terminer",
    "Temps\nInitialisation": "Initialisation",
    "Temps\nValider Regularisation": "Valider Regularisation",
    "Temps\nEn cours de régularisation": "En cours de régularisation",
    "Temps\nAttente retour tiers": "Attente retour tiers",
}

# Regex durée type: "2d 10h 54m 1s" ou "10h 38m 16s" ou "27 MI 45 S"
DUR_DHMS_RE = re.compile(
    r"(?:(?P<d>\d+)\s*d\s*)?"
    r"(?:(?P<h>\d+)\s*h\s*)?"
    r"(?:(?P<m>\d+)\s*m\s*)?"
    r"(?:(?P<s>\d+)\s*s\s*)?$",
    re.IGNORECASE
)
DUR_MI_S_RE = re.compile(r"(?:(?P<m>\d+)\s*mi\s*)?(?:(?P<s>\d+)\s*s\s*)?$", re.IGNORECASE)


# =========================================================
# UTILITAIRES (NETTOYAGE / DATES / DUREES)
# =========================================================
def clean_html_spaces(x: Any) -> str:
    """Nettoie les valeurs contenant '&nbsp;' ou \xa0."""
    if x is None:
        return ""
    s = str(x)
    s = html.unescape(s)  # convertit &nbsp; etc.
    s = s.replace("\xa0", " ").replace("\u00a0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def parse_date_fr_maybe(x: Any) -> Optional[pd.Timestamp]:
    """
    Parse des dates type: '18-12-2024 13:16:36' (avec &nbsp; possiblement).
    """
    s = clean_html_spaces(x)
    if not s:
        return None
    try:
        # dayfirst=True important pour format dd-mm-yyyy
        dt = dtparser.parse(s, dayfirst=True)
        return pd.to_datetime(dt)
    except Exception:
        return None

def duration_to_seconds(x: Any) -> int:
    """
    Convertit:
      - '2d 10h 54m 1s'
      - '10h 38m 16s'
      - '27 MI 45 S'
      - valeurs numériques (secondes) => int
    """
    if x is None:
        return 0
    s = clean_html_spaces(x)
    if not s:
        return 0

    # Si numérique
    if re.fullmatch(r"\d+(\.\d+)?", s):
        return int(float(s))

    # dhms
    m = DUR_DHMS_RE.match(s.lower().replace(" ", ""))
    if m:
        d = int(m.group("d") or 0)
        h = int(m.group("h") or 0)
        mi = int(m.group("m") or 0)
        sec = int(m.group("s") or 0)
        return d*86400 + h*3600 + mi*60 + sec

    # format "MI S"
    s2 = s.lower().replace(" ", "")
    m2 = DUR_MI_S_RE.match(s2)
    if m2 and (m2.group("m") or m2.group("s")):
        mi = int(m2.group("m") or 0)
        sec = int(m2.group("s") or 0)
        return mi*60 + sec

    return 0

def seconds_to_human(seconds: int) -> str:
    if seconds <= 0:
        return "—"
    d, rem = divmod(seconds, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    if s: parts.append(f"{s}s")
    return " ".join(parts) if parts else "—"


# =========================================================
# PARSING WORKFLOW: 1) depuis SLA Réclamation (string [REC - ...])
# =========================================================
def parse_workflow_from_sla(raw: Any) -> List[Dict[str, Any]]:
    """
    Parse:
    [REC - Etude Technique:10h 38m 16s, REC - Traitement Back:2d 10h 54m 1s, ...]
    """
    s = clean_html_spaces(raw).strip()
    s = s.strip("[]")
    if not s:
        return []

    items = [x.strip() for x in s.split(",") if x.strip()]
    out = []
    for it in items:
        if ":" not in it:
            continue
        left, dur = it.split(":", 1)
        step = left.replace("REC -", "").strip()
        # normalise quelques variantes
        step_lower = step.lower()
        if "traitement back" in step_lower:
            step = "Traitement"
        if "en régularisation" in step_lower or "en regularisation" in step_lower:
            step = "En cours de régularisation"
        sec = duration_to_seconds(dur)
        out.append({"step": step, "seconds": sec, "human": seconds_to_human(sec)})
    return out

def parse_workflow_from_time_columns(row: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Construit workflow à partir des colonnes Temps\n...
    Les temps sont souvent fournis en secondes (ex 1303) ou minutes.
    """
    out = []
    for col, step in TIME_COLUMNS_MAP.items():
        if col in row:
            sec = duration_to_seconds(row.get(col))
            if sec > 0:
                out.append({"step": step, "seconds": sec, "human": seconds_to_human(sec)})
    # garder l'ordre logique du pipeline
    out_sorted = sorted(out, key=lambda x: STATUSES_ORDER.index(x["step"]) if x["step"] in STATUSES_ORDER else 999)
    return out_sorted


# =========================================================
# UI HELPERS
# =========================================================
def badge(text: str, color: str) -> str:
    return f"""
    <span style="background:{color};color:white;padding:6px 10px;border-radius:999px;
                 font-weight:900;font-size:0.85rem;display:inline-block;">
        {text}
    </span>
    """

def render_workflow(status: str, steps: List[Dict[str, Any]]):
    st.subheader("🔄 Workflow & Durées")

    # agrégation durées par step
    sec_by = {}
    for s in steps:
        sec_by[s["step"]] = sec_by.get(s["step"], 0) + int(s["seconds"])

    try:
        current_idx = STATUSES_ORDER.index(status)
    except ValueError:
        current_idx = -1

    cols = st.columns(len(STATUSES_ORDER))
    for i, stt in enumerate(STATUSES_ORDER):
        if current_idx == -1:
            state = "future"
        elif i < current_idx:
            state = "done"
        elif i == current_idx:
            state = "current"
        else:
            state = "future"

        bg = "#198754" if state == "done" else ("#ffc107" if state == "current" else "#e9ecef")
        fg = "#fff" if state in ("done", "current") else "#343a40"
        dur = seconds_to_human(sec_by.get(stt, 0)) if sec_by.get(stt, 0) else "—"

        cols[i].markdown(
            f"""
            <div style="padding:10px;border-radius:14px;background:{bg};color:{fg};text-align:center;">
              <div style="font-weight:900;">{stt}</div>
              <div style="font-size:0.85rem;">{dur}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # tableau des durées
    if steps:
        df_steps = pd.DataFrame(steps)
        df_steps = df_steps.groupby("step", as_index=False)["seconds"].sum()
        df_steps["durée"] = df_steps["seconds"].apply(seconds_to_human)
        df_steps = df_steps.sort_values("seconds", ascending=False)

        total_sec = int(df_steps["seconds"].sum())
        st.caption(f"⏱️ Durée totale (somme des étapes connues) : **{seconds_to_human(total_sec)}**")
        st.dataframe(df_steps[["step", "durée", "seconds"]], use_container_width=True, hide_index=True)
    else:
        st.info("Aucune durée d’étape disponible.")


# =========================================================
# V0 : DONNEES EN DUR
# =========================================================
def load_v0_data() -> pd.DataFrame:
    sample = {
        "Filiale": "SGCI",
        "Réf. Réclamation": "SGCI-338245",
        "Créateur": "Amoin Ange Marie KONAN",
        "Date de création": "18-12-2024 13:16:36",
        "Date dernière modification": "18-12-2024 13:39:21",
        "Groupe de résolution": "SGCI PMON Reclamation Group",
        "Etat": "Valider Regularisation",
        "Type": "Monetique",
        "Activité": "Retrait GAB SG",
        "Motif": "RETRAIT CONTESTE-NON RECONNU",
        "Objet de la réclamation": "retrait DAB contesté",
        "Caractère de la réclamation": "Non fondée",
        "Canal de réception": "Email",
        "Durée de traitement (En J)": "27 MI 45 S",
        "Client": "[500505275] POUDIOUGO JACOB",
        "Agence": "00111-PLATEAU",
        "Segment": "10103",
        "Typologie": "Operations non autorisées",
        "Numéro de la carte": "454436******9225",
        "Montant": "100000",
        "Dévise du montant": "XOF",
        "SLA Réclamation": "[REC - Etude Technique:10h 38m 16s, REC - Traitement Back:2d 10h 54m 1s, REC - En Régularisation:4d 10h 54m 52s]",
        "Temps\nEtude Technique": "1303",
        "Temps\nTraitement": "51",
        "Temps\nValider Regularisation": "3",
        "Temps\nEn cours de régularisation": "307",
    }
    df = pd.DataFrame([sample])
    return df


# =========================================================
# V1 : IMPORT EXCEL/CSV
# =========================================================
EXPECTED_KEY_COL = "Réf. Réclamation"

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    - Nettoie les noms de colonnes (garde les retours ligne si présents)
    - Ajoute colonnes manquantes (sans planter)
    - Convertit dates
    """
    df = df.copy()

    # Nettoyage de base des colonnes (conserve '\n' dans "Temps\n...")
    df.columns = [clean_html_spaces(c).replace("\r", "") for c in df.columns]

    # Normalise colonnes temps: parfois "Temps Etude Technique" sans \n
    # => on crée une correspondance tolérante
    rename_map = {}
    for c in df.columns:
        c_norm = c.replace("Temps ", "Temps\n").replace("Temps\t", "Temps\n")
        # exemple: "Temps Etude Technique" -> "Temps\nEtude Technique"
        if c.startswith("Temps ") and "\n" not in c:
            rename_map[c] = c_norm
    if rename_map:
        df = df.rename(columns=rename_map)

    # dates
    if "Date de création" in df.columns:
        df["Date de création"] = df["Date de création"].apply(parse_date_fr_maybe)
    if "Date dernière modification" in df.columns:
        df["Date dernière modification"] = df["Date dernière modification"].apply(parse_date_fr_maybe)

    return df

@st.cache_data(show_spinner=False)
def load_v1_file(uploaded) -> pd.DataFrame:
    name = uploaded.name.lower()
    if name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded, engine="openpyxl")
    return standardize_columns(df)


# =========================================================
# APP UI
# =========================================================
st.title(APP_TITLE)
st.caption(APP_SUBTITLE)

with st.sidebar:
    st.header("⚙️ Mode")
    mode = st.radio("Choisir la version", ["V0 (valeurs en dur)", "V1 (import Excel/CSV)"], index=0)

    st.divider()
    st.header("🔎 Recherche")
    ref = st.text_input("Réf. Réclamation", placeholder="Ex: SGCI-338245")

    st.divider()
    st.header("ℹ️ Aide")
    st.write("Workflow prioritaire : colonne **SLA Réclamation** si elle contient `[REC - ...]`.")
    st.write("Sinon, utilisation des colonnes **Temps\\n...** si présentes.")

# Charger data selon mode
if mode == "V0 (valeurs en dur)":
    df = load_v0_data()
else:
    uploaded = st.file_uploader("Importer un fichier Excel/CSV (V1)", type=["xlsx", "xls", "csv"])
    if uploaded is None:
        st.info("➡️ Importer un fichier Excel/CSV pour activer la V1.")
        st.stop()
    df = load_v1_file(uploaded)

# Vérifier existence colonne clé
if EXPECTED_KEY_COL not in df.columns:
    st.error(f"Colonne clé manquante : **{EXPECTED_KEY_COL}**")
    st.caption("Colonnes détectées : " + ", ".join(df.columns[:80]) + (" ..." if len(df.columns) > 80 else ""))
    st.stop()

if not ref:
    st.info("➡️ Saisis une référence de réclamation dans la sidebar.")
    st.stop()

# Lookup
match = df[df[EXPECTED_KEY_COL].astype(str).str.strip() == ref.strip()]
if match.empty:
    st.warning("Réclamation introuvable dans le fichier.")
    st.caption("Aperçu des 20 dernières lignes :")
    st.dataframe(df.tail(20), use_container_width=True, hide_index=True)
    st.stop()

row = match.iloc[0].to_dict()

# Champs principaux (tolérants)
filiale = row.get("Filiale", "")
etat = row.get("Etat", row.get("État", row.get("Etat ", "")))
type_rec = row.get("Type", "")
activite = row.get("Activité", "")
motif = row.get("Motif", "")
client = row.get("Client", "")
compte = row.get("Numéro de compte", "")
agence = row.get("Agence", "")
segment = row.get("Segment", "")
canal = row.get("Canal de réception", "")
objet = row.get("Objet de la réclamation", "")
montant = clean_html_spaces(row.get("Montant", ""))
devise = clean_html_spaces(row.get("Dévise du montant", ""))

created_at = row.get("Date de création", None)
updated_at = row.get("Date dernière modification", None)

# Statut/Etat -> on aligne sur workflow
status = clean_html_spaces(etat)
if status not in STATUSES_ORDER:
    # tentative de normalisation simple
    if "regular" in status.lower():
        status = "Valider Regularisation" if "valider" in status.lower() else "En cours de régularisation"
    elif "support" in status.lower():
        status = "SUPPORT"
    elif "trait" in status.lower():
        status = "Traitement"
    else:
        # si inconnu, on le garde mais il ne sera pas positionné correctement
        pass

# Workflow: prioritaire SLA Réclamation
sla_raw = row.get("SLA Réclamation", "")
steps = parse_workflow_from_sla(sla_raw)

# fallback: colonnes Temps...
if not steps:
    steps = parse_workflow_from_time_columns(row)

# UI Header
st.markdown("## 🧾 Dossier Réclamation")

c1, c2, c3, c4 = st.columns([1.4, 1.2, 1.2, 1.2])
with c1:
    st.markdown("### Référence")
    st.write(ref)
    if filiale:
        st.caption(f"Filiale : **{filiale}**")
with c2:
    st.markdown("### Création")
    st.write(created_at)
with c3:
    st.markdown("### Dernière modification")
    st.write(updated_at)
with c4:
    st.markdown("### Statut / Etat")
    col = STATUS_COLORS.get(status, "#6c757d")
    st.markdown(badge(status, col), unsafe_allow_html=True)

st.divider()

# Bloc infos (métier)
left, right = st.columns([1.6, 1.0])

with left:
    st.subheader("📌 Informations clés")
    st.write(f"**Type :** {type_rec or '—'}")
    st.write(f"**Activité :** {activite or '—'}")
    st.write(f"**Motif :** {motif or '—'}")
    if objet:
        st.write(f"**Objet :** {objet}")
    if canal:
        st.write(f"**Canal :** {canal}")

with right:
    st.subheader("💳 Contexte")
    st.write(f"**Client :** {client or '—'}")
    st.write(f"**Numéro de compte :** {compte or '—'}")
    st.write(f"**Agence :** {agence or '—'}")
    st.write(f"**Segment :** {segment or '—'}")
    if montant:
        st.write(f"**Montant :** {montant} {devise}".strip())

st.divider()

# Workflow
render_workflow(status=status, steps=steps)

# Détails raw pour debug POC
with st.expander("🔍 Debug POC (valeurs brutes)"):
    st.write("SLA Réclamation (raw) :", sla_raw)
    st.write("Steps parsed :", steps)
    st.write("Colonnes temps détectées :", [c for c in row.keys() if str(c).startswith("Temps")])
