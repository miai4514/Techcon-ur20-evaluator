import base64
import re
from datetime import datetime
from pathlib import Path
import streamlit as st

# -----------------------------------------------------------------------------
# CONFIGURARE PAGINĂ (centered = curat pe desktop, 100% responsive pe telefon)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Tech-Con UR20 | Evaluator Paletizare",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# -----------------------------------------------------------------------------
# HELPERE SIGURE PENTRU IMAGINI (detectează automat .png, .jpg, .jpeg, .webp)
# -----------------------------------------------------------------------------
def find_asset(stem: str):
    assets_dir = Path("assets")
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        candidate = assets_dir / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    return None


def img_to_data_uri(filepath):
    if not filepath:
        return None
    p = Path(filepath)
    if not p.exists():
        return None
    ext = p.suffix.lower().lstrip(".")
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
    return f"data:image/{mime};base64,{b64}"


# -----------------------------------------------------------------------------
# STIL INSPIRAT DIN IDENTITATEA TECH-CON (alb + albastru #005CA9 + outline)
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
:root {
    --tc-blue: #005CA9;
    --tc-blue-dark: #004580;
    --tc-blue-soft: #EEF5FC;
    --tc-border: #D6E2EE;
    --tc-text: #142433;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2.5rem;
    max-width: 860px;
}

/* Header corporate cu logo în stânga sus */
.tc-header {
    display: flex;
    align-items: center;
    gap: 1.1rem;
    background-color: #FFFFFF;
    border: 1px solid var(--tc-border);
    border-top: 4px solid var(--tc-blue);
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 10px rgba(0, 92, 169, 0.06);
}
.tc-logo {
    max-height: 48px;
    max-width: 165px;
    object-fit: contain;
    flex-shrink: 0;
}
.tc-logo-fallback {
    font-weight: 800;
    font-size: 1.1rem;
    color: var(--tc-blue);
    border: 2px solid var(--tc-blue);
    padding: 0.35rem 0.65rem;
    border-radius: 6px;
    letter-spacing: 0.5px;
    flex-shrink: 0;
}
.tc-title-wrap {
    border-left: 1px solid var(--tc-border);
    padding-left: 1rem;
}
.tc-title-wrap h2 {
    margin: 0 0 0.2rem 0;
    font-size: 1.25rem;
    color: var(--tc-text);
    line-height: 1.25;
}
.tc-title-wrap p {
    margin: 0;
    font-size: 0.88rem;
    color: #4A6075;
}

/* Butoane PRIMARE: albastru Tech-Con plin */
div.stButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"] {
    background-color: var(--tc-blue) !important;
    color: #FFFFFF !important;
    border: 1.5px solid var(--tc-blue) !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    transition: all 0.18s ease-in-out !important;
}
div.stButton > button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover {
    background-color: var(--tc-blue-dark) !important;
    border-color: var(--tc-blue-dark) !important;
}

/* Butoane SECUNDARE: transparente, doar cu contur albastru Tech-Con */
div.stButton > button[kind="secondary"],
button[data-testid="stBaseButton-secondary"],
div.stDownloadButton > button {
    background-color: transparent !important;
    color: var(--tc-blue) !important;
    border: 1.5px solid var(--tc-blue) !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    transition: all 0.18s ease-in-out !important;
}
div.stButton > button[kind="secondary"]:hover,
button[data-testid="stBaseButton-secondary"]:hover,
div.stDownloadButton > button:hover {
    background-color: var(--tc-blue-soft) !important;
    color: var(--tc-blue-dark) !important;
    border-color: var(--tc-blue-dark) !important;
}

/* Carduri metrici */
div[data-testid="stMetric"] {
    background-color: #F7FAFD;
    border: 1px solid var(--tc-border);
    border-radius: 8px;
    padding: 0.75rem 0.9rem;
}

/* Carduri pași flux & cutii fapte vs estimări */
.step-card {
    background-color: #F7FAFD;
    border: 1px solid var(--tc-border);
    border-left: 4px solid var(--tc-blue);
    padding: 0.75rem 1rem;
    border-radius: 8px;
    margin-bottom: 0.6rem;
    color: var(--tc-text);
}
.fact-box {
    background-color: #EEF5FC;
    border: 1px solid #BFD9F2;
    padding: 0.9rem 1rem;
    border-radius: 8px;
    color: #103252;
    margin-bottom: 0.8rem;
}
.est-box {
    background-color: #FFFBF0;
    border: 1px solid #F7DF9C;
    padding: 0.9rem 1rem;
    border-radius: 8px;
    color: #6B4707;
    margin-bottom: 0.8rem;
}

/* Responsive mobil pentru header */
@media (max-width: 600px) {
    .tc-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.6rem;
    }
    .tc-title-wrap {
        border-left: none;
        border-top: 1px solid var(--tc-border);
        padding-left: 0;
        padding-top: 0.5rem;
    }
}
</style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# DATE DE REFERINȚĂ (CENTRE REGIONALE TECH-CON & LISTE)
# -----------------------------------------------------------------------------
HUB_MAPPING = {
    "Iași": [
        "Iași", "Bacău", "Botoșani", "Galați", "Neamț",
        "Suceava", "Vaslui", "Vrancea",
    ],
    "Timișoara": [
        "Timiș", "Alba", "Arad", "Bihor", "Bistrița-Năsăud",
        "Caraș-Severin", "Cluj", "Hunedoara", "Maramureș",
        "Mehedinți", "Mureș", "Satu Mare", "Sălaj", "Sibiu",
    ],
    "Dragomirești-Deal (Ilfov / București)": [
        "Ilfov", "București", "Argeș", "Brașov", "Brăila", "Buzău",
        "Călărași", "Constanța", "Covasna", "Dâmbovița", "Dolj",
        "Giurgiu", "Gorj", "Harghita", "Ialomița", "Olt", "Prahova",
        "Teleorman", "Tulcea", "Vâlcea",
    ],
}

ALL_COUNTIES = sorted(
    [c for counties in HUB_MAPPING.values() for c in counties]
)

INDUSTRIES = [
    "— Selectați industria —",
    "Industria alimentară – Panificație, patiserie, ciocolaterie",
    "Industria alimentară – Lactate, creme, sosuri, miere",
    "Industria alimentară – Conserve, murături, ingrediente",
    "Altă industrie – Vopsele, adezivi, construcții (necesită validare separată)",
    "Altă industrie – Chimie / Detergenți / Agricultură (necesită validare separată)",
]

PACKAGING_TYPES = [
    "— Selectați tipul ambalajului —",
    "Găleată plastic rigid cu mâner standard (similar PURATOS)",
    "Găleată plastic cu mâner metalic / atipic",
    "Găleată fără mâner / recipient cilindric",
    "Alt tip de ambalaj (cutii, saci, bidoane)",
]

ROLES = [
    "— Selectați rolul —",
    "Director de Producție",
    "Responsabil Investiții / CapEx",
    "Manager Fabrică / Operațiuni",
    "Inginer Automatizări / Mentenanță",
    "Administrator / Director General",
]


def get_nearest_hub(county: str) -> str:
    for hub, counties in HUB_MAPPING.items():
        if county in counties:
            return hub
    return "Dragomirești-Deal (Ilfov / București)"


# -----------------------------------------------------------------------------
# INIȚIALIZARE SESSION STATE
# -----------------------------------------------------------------------------
DEFAULTS = {
    "page": "eval",
    # Secțiunea 1 – Pre-evaluare
    "industry": "— Selectați industria —",
    "packaging": "— Selectați tipul ambalajului —",
    "weight_kg": 13.0,
    "rate_bpm": 7.0,
    "buckets_per_pallet": 44,
    "shifts_per_day": 2,
    "space_two_pos": "Da – avem spațiu pentru 2 poziții de paletizare",
    "bottleneck": "Nu – alimentarea liniei și preluarea paleților sunt stabile",
    "county": "— Selectați județul —",
    "eval_submitted": False,
    "last_eval_result": None,
    # Secțiunea 2 – Formular Demo / CRM (date fictive)
    "crm_company": "",
    "crm_contact": "",
    "crm_role": "— Selectați rolul —",
    "crm_email": "",
    "crm_phone": "",
    "crm_pref": "Evaluare tehnică online (30 min)",
    "crm_notes": "",
    "crm_fictitious_ok": False,
    "crm_submitted": False,
}

for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val


# -----------------------------------------------------------------------------
# CALLBACK-URI PENTRU NAVIGARE ȘI SCENARII RAPIDE DE TEST
# -----------------------------------------------------------------------------
def go_to(page_name: str):
    st.session_state.page = page_name


def load_valid_eval_case():
    st.session_state.industry = "Industria alimentară – Lactate, creme, sosuri, miere"
    st.session_state.packaging = "Găleată plastic rigid cu mâner standard (similar PURATOS)"
    st.session_state.weight_kg = 13.0
    st.session_state.rate_bpm = 7.0
    st.session_state.buckets_per_pallet = 44
    st.session_state.shifts_per_day = 2
    st.session_state.space_two_pos = "Da – avem spațiu pentru 2 poziții de paletizare"
    st.session_state.bottleneck = "Nu – alimentarea liniei și preluarea paleților sunt stabile"
    st.session_state.county = "Cluj"
    st.session_state.eval_submitted = True


def load_invalid_eval_case():
    st.session_state.industry = "— Selectați industria —"
    st.session_state.packaging = "— Selectați tipul ambalajului —"
    st.session_state.weight_kg = 0.0
    st.session_state.rate_bpm = 0.0
    st.session_state.buckets_per_pallet = 0
    st.session_state.shifts_per_day = 2
    st.session_state.space_two_pos = "Nu / Nesigur – necesită verificare spațiu"
    st.session_state.bottleneck = "Da – există opriri în amonte (umplere) sau în aval"
    st.session_state.county = "— Selectați județul —"
    st.session_state.eval_submitted = True


def load_valid_crm_case():
    st.session_state.crm_company = "Lactate Demo Transilvania SRL (Fictiv)"
    st.session_state.crm_contact = "Andrei Testescu (Fictiv)"
    st.session_state.crm_role = "Director de Producție"
    st.session_state.crm_email = "productie@exemplu-demo.ro"
    st.session_state.crm_phone = "0700000123"
    st.session_state.crm_pref = "Vizită de evaluare tehnică în fabrică"
    st.session_state.crm_notes = (
        "Linie ambalare găleți 13 kg, 2 schimburi/zi. "
        "Dorim verificarea gripperului pe mostrele noastre."
    )
    st.session_state.crm_fictitious_ok = True
    st.session_state.crm_submitted = True


def load_invalid_crm_case():
    st.session_state.crm_company = ""
    st.session_state.crm_contact = "A"
    st.session_state.crm_role = "— Selectați rolul —"
    st.session_state.crm_email = "email-fara-arond"
    st.session_state.crm_phone = "1234"
    st.session_state.crm_notes = ""
    st.session_state.crm_fictitious_ok = False
    st.session_state.crm_submitted = True


# -----------------------------------------------------------------------------
# LOGICA DE EVALUARE TEHNICĂ (DETERMINISTĂ, TRANSPARENTĂ)
# -----------------------------------------------------------------------------
def evaluate_feasibility():
    errors = []
    warnings = []

    industry = st.session_state.industry
    packaging = st.session_state.packaging
    weight = float(st.session_state.weight_kg)
    rate = float(st.session_state.rate_bpm)
    bpp = int(st.session_state.buckets_per_pallet)
    shifts = int(st.session_state.shifts_per_day)
    space = st.session_state.space_two_pos
    bottleneck = st.session_state.bottleneck
    county = st.session_state.county

    # 1. Validare date lipsă / greșite
    if industry == INDUSTRIES[0]:
        errors.append("Selectați sectorul industrial al fabricii.")
    if packaging == PACKAGING_TYPES[0]:
        errors.append("Selectați tipul ambalajului manipulat.")
    if weight <= 0:
        errors.append("Greutatea găleții trebuie să fie mai mare decât 0 kg.")
    if rate <= 0:
        errors.append("Debitul liniei (găleți/minut) trebuie să fie mai mare decât 0.")
    if bpp <= 0:
        errors.append("Numărul de găleți per palet trebuie să fie cel puțin 1.")
    if county == "— Selectați județul —":
        errors.append("Selectați județul fabricii pentru alocarea centrului regional Tech-Con.")

    if errors:
        return {"status": "INVALID", "errors": errors}

    # 2. Analiză tehnică față de reperele PURATOS + ipoteze declarate
    # Ipoteză de lucru declarată: gripper pneumatic ~3,5 kg -> sarcină totală = greutate + 3,5 kg
    estimated_gripper_kg = 3.5
    total_payload_kg = round(weight + estimated_gripper_kg, 1)

    # Referință PURATOS: 8,6 găleți/min (5 kg) și 7,4 găleți/min (13 kg)
    if weight <= 7.0:
        ref_rate = 8.6
        ref_label = "8,6 găleți/min (test PURATOS 5 kg)"
    else:
        ref_rate = 7.4
        ref_label = "7,4 găleți/min (test PURATOS 13 kg)"

    is_out_of_capacity = False

    if total_payload_kg > 20.0:
        is_out_of_capacity = True
        warnings.append(
            f"Sarcina totală estimată ({weight:.1f} kg găleată + ~{estimated_gripper_kg} kg gripper = "
            f"{total_payload_kg} kg) depășește limita de pre-evaluare de 20 kg a celulei UR20."
        )
    elif weight > 13.0:
        warnings.append(
            f"Greutatea ({weight:.1f} kg) depășește formatul maxim de 13 kg testat la PURATOS. "
            "Este necesară verificarea masei exacte a gripperului și a centrului de greutate."
        )

    if rate > ref_rate:
        warnings.append(
            f"Debitul solicitat ({rate:.1f} găleți/min) depășește rezultatul de test PURATOS ({ref_label}). "
            "Poate fi necesară validare de ciclu sau o configurație cu două celule."
        )
    elif rate < 3.0:
        warnings.append(
            "Debitul introdus este redus (< 3 găleți/min). Merită verificat în discuția tehnică dacă "
            "automatizarea paletizării este prioritară față de alte zone ale liniei."
        )

    if industry.startswith("Altă industrie"):
        warnings.append(
            "Aplicația de referință este din industria alimentară. Pentru alte industrii, "
            "cerințele tehnice, de siguranță și de mediu trebuie validate separat."
        )

    if packaging != PACKAGING_TYPES[1]:
        warnings.append(
            "Ambalajul diferă de găleata rigidă din plastic cu mâner standard. "
            "Gripperul pneumatic și sistemul de vedere SICK 2D necesită testare pe mostre reale."
        )

    if space.startswith("Nu"):
        warnings.append(
            "Spațiul pentru cele două poziții de paletizare, cele 3 scanere de protecție și "
            "accesul pentru schimbul manual al paleților trebuie verificat la fața locului."
        )

    if bottleneck.startswith("Da"):
        warnings.append(
            "Blocaj semnalat în amonte/aval: un robot mai rapid nu crește automat debitul întregii "
            "fabrici. Blocajul din linia de umplere sau din aval trebuie analizat înainte de implementare."
        )

    # Indicatori operaționali (fără ROI / economii salariale)
    pallets_per_hour = round((rate * 60.0) / bpp, 2)
    minutes_per_pallet = round(bpp / rate, 1)
    pct_of_ref = round((rate / ref_rate) * 100)
    hub = get_nearest_hub(county)

    if is_out_of_capacity:
        status = "NEELIGIBIL"
    elif len(warnings) > 0:
        status = "VALIDARE"
    else:
        status = "ELIGIBIL"

    return {
        "status": status,
        "warnings": warnings,
        "industry": industry,
        "packaging": packaging,
        "weight_kg": weight,
        "total_payload_kg": total_payload_kg,
        "estimated_gripper_kg": estimated_gripper_kg,
        "rate_bpm": rate,
        "ref_rate": ref_rate,
        "ref_label": ref_label,
        "pct_of_ref": pct_of_ref,
        "bpp": bpp,
        "shifts": shifts,
        "pallets_per_hour": pallets_per_hour,
        "minutes_per_pallet": minutes_per_pallet,
        "county": county,
        "hub": hub,
    }


# -----------------------------------------------------------------------------
# HEADER CU LOGO TECH-CON + BARĂ DE NAVIGARE SUS (3 SECȚIUNI SELECTABILE)
# -----------------------------------------------------------------------------
logo_path = find_asset("logo_techcon")
logo_uri = img_to_data_uri(logo_path)
if logo_uri:
    logo_html = f'<img src="{logo_uri}" alt="Tech-Con Logo" class="tc-logo" />'
else:
    logo_html = '<div class="tc-logo-fallback">TECH-CON</div>'

st.markdown(
    f"""
<div class="tc-header">
    {logo_html}
    <div class="tc-title-wrap">
        <h2>Evaluator Paletizare Găleți – UR20</h2>
        <p>Instrument demonstrativ pentru fabrici din România • Bazat pe aplicația UR20 implementată la PURATOS</p>
    </div>
</div>
    """,
    unsafe_allow_html=True,
)

nav1, nav2, nav3 = st.columns(3)
with nav1:
    st.button(
        "1. Pre-evaluare UR20",
        use_container_width=True,
        type="primary" if st.session_state.page == "eval" else "secondary",
        on_click=go_to,
        args=("eval",),
    )
with nav2:
    st.button(
        "2. Solicită Demo",
        use_container_width=True,
        type="primary" if st.session_state.page == "demo" else "secondary",
        on_click=go_to,
        args=("demo",),
    )
with nav3:
    st.button(
        "3. Cazul PURATOS",
        use_container_width=True,
        type="primary" if st.session_state.page == "case" else "secondary",
        on_click=go_to,
        args=("case",),
    )

st.divider()

# =============================================================================
# SECȚIUNEA 1: PRE-EVALUARE TEHNICĂ UR20 (FUNCȚIA PRINCIPALĂ TESTABILĂ)
# =============================================================================
if st.session_state.page == "eval":
    st.subheader("Verifică rapid dacă linia ta se potrivește pentru o celulă UR20")
    st.caption(
        "Testare rapidă pentru evaluatori: folosește butoanele de mai jos sau completează manual date fictive."
    )

    q1, q2 = st.columns(2)
    with q1:
        st.button(
            "✅ Încarcă caz demo valid",
            use_container_width=True,
            on_click=load_valid_eval_case,
        )
    with q2:
        st.button(
            "⚠️ Simulează date invalide / lipsă",
            use_container_width=True,
            on_click=load_invalid_eval_case,
        )

    st.markdown("#### Parametrii liniei de ambalare (date de test)")

    col_a, col_b = st.columns(2)
    with col_a:
        st.selectbox("Sector industrial *", INDUSTRIES, key="industry")
        st.selectbox("Tip ambalaj și mâner *", PACKAGING_TYPES, key="packaging")
        st.number_input(
            "Greutate găleată (kg) *",
            min_value=0.0,
            max_value=30.0,
            step=0.5,
            key="weight_kg",
            help="Exemplu PURATOS: găleți de 5 kg sau 13 kg.",
        )
        st.number_input(
            "Debit dorit al liniei (găleți / minut) *",
            min_value=0.0,
            max_value=25.0,
            step=0.2,
            key="rate_bpm",
            help="Ținta PURATOS: min. 6 găleți/min; testat: 7,4 (13 kg) și 8,6 (5 kg).",
        )

    with col_b:
        st.number_input(
            "Găleți per europalet *",
            min_value=0,
            max_value=250,
            step=1,
            key="buckets_per_pallet",
            help="Exemplu PURATOS: 100 găleți (5 kg) sau 44 găleți (13 kg).",
        )
        st.selectbox("Număr schimburi / zi", [1, 2, 3], key="shifts_per_day")
        st.selectbox(
            "Județul fabricii *",
            ["— Selectați județul —"] + ALL_COUNTIES,
            key="county",
        )
        st.selectbox(
            "Spațiu & acces pentru 2 poziții paletizare",
            [
                "Da – avem spațiu pentru 2 poziții de paletizare",
                "Nu / Nesigur – necesită verificare spațiu",
            ],
            key="space_two_pos",
        )

    st.selectbox(
        "Există blocaje cunoscute în amonte (umplere) sau în aval?",
        [
            "Nu – alimentarea liniei și preluarea paleților sunt stabile",
            "Da – există opriri în amonte (umplere) sau în aval",
        ],
        key="bottleneck",
    )

    if st.button("🔍 Evaluează fezabilitatea UR20", type="primary", use_container_width=True):
        st.session_state.eval_submitted = True

    if st.session_state.eval_submitted:
        res = evaluate_feasibility()
        st.session_state.last_eval_result = res
        st.divider()

        if res["status"] == "INVALID":
            st.error("Nu putem genera evaluarea – lipsesc date sau există valori invalide:")
            for err in res["errors"]:
                st.markdown(f"- ❌ {err}")
            st.info(
                "Corectați câmpurile semnalate mai sus sau apăsați **„✅ Încarcă caz demo valid”** "
                "pentru a vedea un scenariu complet."
            )
        else:
            if res["status"] == "ELIGIBIL":
                st.success(
                    f"**Verdict: Eligibil pentru replicare UR20** • "
                    f"Centru Tech-Con alocat: **{res['hub']}**"
                )
            elif res["status"] == "VALIDARE":
                st.warning(
                    f"**Verdict: Necesită validare tehnică Tech-Con** • "
                    f"Centru Tech-Con alocat: **{res['hub']}**"
                )
            else:
                st.error(
                    f"**Verdict: În afara domeniului standard UR20 (necesită altă configurație)** • "
                    f"Centru Tech-Con alocat: **{res['hub']}**"
                )

            m1, m2, m3 = st.columns(3)
            m1.metric(
                "Ritmul față de testul PURATOS",
                f"{res['pct_of_ref']}%",
                f"Ref: {res['ref_rate']} găleți/min",
                delta_color="off",
            )
            m2.metric(
                "Paleți estimați / oră",
                f"{res['pallets_per_hour']}",
                f"{res['bpp']} găleți/palet",
                delta_color="off",
            )
            m3.metric(
                "Schimb manual palet",
                f"~{res['minutes_per_pallet']} min",
                "Intervenție operator",
                delta_color="off",
            )

            if res["warnings"]:
                st.markdown("#### Puncte de verificat înaintea implementării")
                for w in res["warnings"]:
                    st.markdown(f"- ⚠️ {w}")

            c_fact, c_est = st.columns(2)
            with c_fact:
                st.markdown(
                    """
<div class="fact-box">
    <strong>📌 Fapte din testul PURATOS (Tech-Con)</strong><br><br>
    • Găleți din plastic: 5 kg (100/palet) și 13 kg (44/palet).<br>
    • Testat: 8,6 găleți/min (5 kg) și 7,4 găleți/min (13 kg) vs. ținta de min. 6/min.<br>
    • Vedere SICK 2D pentru orientarea mânerului + gripper pneumatic + 3 scanere protecție.<br>
    • Schimbarea paleților și așezarea separatoarelor rămân <strong>manuale</strong>.
</div>
                    """,
                    unsafe_allow_html=True,
                )
            with c_est:
                st.markdown(
                    f"""
<div class="est-box">
    <strong>🧮 Estimări & ipoteze pentru scenariul tău</strong><br><br>
    • Sarcină totală estimată: <strong>{res['total_payload_kg']} kg</strong>
    (găleată {res['weight_kg']} kg + ipoteză gripper ~{res['estimated_gripper_kg']} kg).<br>
    • Ritm estimat: <strong>{res['pallets_per_hour']} paleți/oră</strong>
    (schimb manual palet la ~{res['minutes_per_pallet']} min, fără opriri).<br>
    • <em>Valorile PURATOS sunt rezultate de test, nu garanții universale.</em><br>
    • <em>Înfolierea, expedierea și transportul automat către logistică nu sunt incluse.</em>
</div>
                    """,
                    unsafe_allow_html=True,
                )

            st.button(
                "📩 Continuă către Solicitare Demo & Evaluare Tehnică →",
                type="primary",
                use_container_width=True,
                on_click=go_to,
                args=("demo",),
            )

# =============================================================================
# SECȚIUNEA 2: SOLICITARE EVALUARE TEHNICĂ & DEMO (CTA + CRM)
# =============================================================================
elif st.session_state.page == "demo":
    st.subheader("Solicită o evaluare tehnică sau o demonstrație UR20")

    st.info(
        "🔒 **Regulă de confidențialitate (prototip concurs):** Introduceți exclusiv **date fictive** "
        "de test. Nu introduceți date personale reale sau informații confidențiale."
    )

    eval_data = st.session_state.last_eval_result
    if eval_data and eval_data.get("status") != "INVALID":
        st.success(
            f"**Fișă tehnică atașată automat din Secțiunea 1:** "
            f"{eval_data['weight_kg']} kg | {eval_data['rate_bpm']} găleți/min | "
            f"{eval_data['bpp']} găleți/palet | Verdict: **{eval_data['status']}** | "
            f"Centru Tech-Con: **{eval_data['hub']}**"
        )
    else:
        st.caption(
            "Nu ai rulat încă o pre-evaluare validă în Secțiunea 1. Poți trimite solicitarea și "
            "direct sau te poți întoarce la Secțiunea 1."
        )

    b1, b2 = st.columns(2)
    with b1:
        st.button(
            "✅ Completează date fictive valide",
            use_container_width=True,
            on_click=load_valid_crm_case,
        )
    with b2:
        st.button(
            "⚠️ Testează formular incomplet / invalid",
            use_container_width=True,
            on_click=load_invalid_crm_case,
        )

    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Denumire fabrică / firmă (fictiv) *", key="crm_company")
        st.text_input("Persoană de contact (fictiv) *", key="crm_contact")
        st.selectbox("Rol în decizie *", ROLES, key="crm_role")
    with c2:
        st.text_input("E-mail de test *", key="crm_email", placeholder="ex: contact@exemplu-demo.ro")
        st.text_input("Telefon de test *", key="crm_phone", placeholder="ex: 0700000123")
        st.selectbox(
            "Tip interacțiune dorită",
            [
                "Evaluare tehnică online (30 min)",
                "Vizită de evaluare tehnică în fabrică",
                "Demonstrație celulă UR20",
            ],
            key="crm_pref",
        )

    st.text_area(
        "Detalii suplimentare despre linie (opțional)",
        key="crm_notes",
        placeholder="Ex: tip transportor existent, necesar separatoare, ferestre de instalare...",
    )
    st.checkbox(
        "Confirm că datele introduse sunt fictive (pentru testarea prototipului) *",
        key="crm_fictitious_ok",
    )

    if st.button("📤 Trimite solicitarea către Tech-Con (Demo)", type="primary", use_container_width=True):
        st.session_state.crm_submitted = True

    if st.session_state.crm_submitted:
        crm_errors = []
        comp = st.session_state.crm_company.strip()
        contact = st.session_state.crm_contact.strip()
        role = st.session_state.crm_role
        email = st.session_state.crm_email.strip()
        phone = re.sub(r"[\s\-\.]", "", st.session_state.crm_phone.strip())

        if len(comp) < 3:
            crm_errors.append("Introduceți o denumire fictivă de firmă (minim 3 caractere).")
        if len(contact) < 3:
            crm_errors.append("Introduceți un nume fictiv de contact (minim 3 caractere).")
        if role == ROLES[0]:
            crm_errors.append("Selectați rolul persoanei de contact.")
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            crm_errors.append("Adresa de e-mail de test nu are un format valid (ex: nume@exemplu.ro).")
        if not phone.isdigit() or len(phone) < 10:
            crm_errors.append("Numărul de telefon de test trebuie să conțină cel puțin 10 cifre.")
        if not st.session_state.crm_fictitious_ok:
            crm_errors.append("Bifați confirmarea că datele introduse sunt fictive.")

        st.divider()
        if crm_errors:
            st.error("Solicitarea nu poate fi înregistrată. Verificați câmpurile:")
            for err in crm_errors:
                st.markdown(f"- ❌ {err}")
        else:
            hub = (
                eval_data["hub"]
                if (eval_data and eval_data.get("status") != "INVALID")
                else "Dragomirești-Deal (Ilfov / București)"
            )
            ticket_id = f"TC-UR20-{datetime.now().strftime('%H%M%S')}"

            st.success(f"Solicitare demo înregistrată cu succes! Cod intern CRM: **{ticket_id}**")
            st.markdown(
                f"""
                **Următorii pași în fluxul Tech-Con ({hub}):**
                1. **Verificare cerere relevantă:** confirmarea dimensiunilor găleții, mânerului și spațiului din fabrică.
                2. **Discuție tehnică / Demo:** prezentarea celulei UR20 și testarea prinderii pe mostre reale.
                3. **Evaluare de integrare:** analiza transportorului, semnalelor de proces și a cerințelor de siguranță
                   *(în proiectul PURATOS, livrarea a fost de aproximativ 4 luni)*.
                """
            )

            summary_lines = [
                "FISA SOLICITARE EVALUARE TEHNICA TECH-CON UR20 (DEMO)",
                f"Cod cerere: {ticket_id}",
                f"Centru Tech-Con alocat: {hub}",
                f"Firma (fictiv): {comp}",
                f"Contact (fictiv): {contact} ({role})",
                f"Email test: {email} | Telefon test: {phone}",
                f"Tip interactiune: {st.session_state.crm_pref}",
                f"Observatii: {st.session_state.crm_notes or '-'}",
                "-" * 55,
            ]
            if eval_data and eval_data.get("status") != "INVALID":
                summary_lines += [
                    "DATE PRE-EVALUARE TEHNICA:",
                    f"Verdict pre-evaluare: {eval_data['status']}",
                    f"Industrie: {eval_data['industry']}",
                    f"Ambalaj: {eval_data['packaging']}",
                    f"Greutate galeata: {eval_data['weight_kg']} kg (total estimat cu gripper: {eval_data['total_payload_kg']} kg)",
                    f"Debit dorit: {eval_data['rate_bpm']} galeti/min (Ref PURATOS: {eval_data['ref_label']})",
                    f"Configuratie palet: {eval_data['bpp']} galeti/palet | {eval_data['shifts']} schimburi/zi",
                    f"Estimare operationala: {eval_data['pallets_per_hour']} paleti/ora (~{eval_data['minutes_per_pallet']} min/palet)",
                    f"Judet fabrica: {eval_data['county']}",
                ]
            else:
                summary_lines.append("DATE PRE-EVALUARE TEHNICA: Necompletate in Sectiunea 1.")

            summary_lines += [
                "-" * 55,
                "Nota: Schimbul paletilor si asezarea separatoarelor raman manuale.",
                "Infolierea, expedierea si transportul autonom catre logistica nu fac parte din aceasta oferta.",
            ]

            st.download_button(
                "⬇️ Descarcă rezumatul solicitării (.txt)",
                data="\n".join(summary_lines),
                file_name=f"{ticket_id}_rezumat_UR20.txt",
                mime="text/plain",
                use_container_width=True,
            )

# =============================================================================
# SECȚIUNEA 3: CAZUL PURATOS & CUM FUNCȚIONEAZĂ CELULA UR20
# =============================================================================
elif st.session_state.page == "case":
    st.subheader("Studiu de caz: Paletizarea găleților cu UR20 la PURATOS")
    st.write(
        "Tech-Con a implementat **două celule de paletizare cu roboți Universal Robots UR20** pentru "
        "găleți din plastic de **5 kg** (100 găleți/europalet) și **13 kg** (44 găleți/europalet), "
        "înlocuind ridicarea manuală repetitivă (anterior: 2 operatori/schimb, 2–3 schimburi/zi)."
    )

    # Galerie imagini reprezentative – Cazul PURATOS
    img_celula = find_asset("puratos_celula")
    img_detaliu = find_asset("puratos_detaliu")

    if img_celula and img_detaliu:
        g1, g2 = st.columns(2)
        with g1:
            st.image(
                str(img_celula),
                caption="Celule de paletizare UR20 implementate la PURATOS (Sursă: prezentarea Tech-Con, slide 9)",
                use_container_width=True,
            )
        with g2:
            st.image(
                str(img_detaliu),
                caption="Detaliu aplicație UR20 – prindere găleți, vedere SICK 2D și poziții de paletizare",
                use_container_width=True,
            )
    elif img_celula:
        st.image(
            str(img_celula),
            caption="Celule de paletizare UR20 implementate la PURATOS (Sursă: prezentarea Tech-Con, slide 9)",
            use_container_width=True,
        )
    elif img_detaliu:
        st.image(
            str(img_detaliu),
            caption="Detaliu aplicație UR20 – prindere găleți, vedere SICK 2D și poziții de paletizare",
            use_container_width=True,
        )
    else:
        st.info(
            "📸 Adaugă imaginile în folderul `assets/` (`puratos_celula.jpg`/`.png` și opțional "
            "`puratos_detaliu.jpg`/`.png`) pentru afișare automată aici."
        )

    st.markdown("#### Fluxul celulei UR20 (pas cu pas)")
    steps = [
        ("1. Alimentare", "Gălețile umplute ajung pe transportorul (conveyorul) de alimentare."),
        ("2. Vedere SICK 2D", "Camera verifică orientarea mânerului pentru a evita interferența cu zona de prindere."),
        ("3. Gripper pneumatic", "Dispozitivul personalizat preia sigur găleata de pe transportor."),
        ("4. Paletizare UR20", "Robotul așază găleata după modelul programat pe una dintre cele 2 poziții ale celulei."),
        ("5. Protecție & Operatori", "3 scanere monitorizează zona de acces (reducere viteză / oprire). Operatorii schimbă paleții și așază separatoarele manual."),
    ]
    for title, desc in steps:
        st.markdown(
            f'<div class="step-card"><strong>{title}:</strong> {desc}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("#### Rezultate de test PURATOS (repere reale, nu garanții universale)")
    k1, k2, k3 = st.columns(3)
    k1.metric("Găleți 5 kg", "8,6 / min", "+43% peste ținta de 6/min")
    k2.metric("Găleți 13 kg", "7,4 / min", "+23% peste ținta de 6/min")
    k3.metric("Preluări eșuate la FAT", "0", "Livrare ~4 luni")

    st.markdown("#### Ce intră și ce NU intră în domeniul soluției")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown("**✅ Face celula UR20**")
        st.markdown(
            "- Detectează orientarea mânerului (SICK 2D)\n"
            "- Preia gălețile de pe transportor\n"
            "- Așază ordonat pe 2 poziții de paletizare\n"
            "- Monitorizează accesul cu 3 scanere"
        )
    with sc2:
        st.markdown("**👷 Rămâne manual**")
        st.markdown(
            "- Schimbarea paleților plini cu paleți goi\n"
            "- Amplasarea separatoarelor între straturi\n"
            "- Supravegherea fluxului și procedurile de operare"
        )
    with sc3:
        st.markdown("**🚫 În afara proiectului**")
        st.markdown(
            "- Transportul autonom către logistică (ex. MiR – etapă separată)\n"
            "- Înfolierea paleților\n"
            "- Expedierea și logistica de depozit"
        )

    st.divider()
    st.markdown("#### Întrebări frecvente pentru directori de producție (Q&A verificat)")
    faq = {
        "Ce trebuie verificat înainte să replicăm soluția în fabrica noastră?": (
            "Se verifică greutatea, forma, materialul, mânerul și stabilitatea găleții (sarcina totală "
            "include gripperul), debitul de intrare, modelul de paletizare, separatorul, spațiul pentru "
            "2 poziții, evaluarea riscurilor, igiena și integrarea cu transportorul existent."
        ),
        "Dacă robotul este mai rapid, crește automat producția fabricii?": (
            "Nu automat. Dacă există un blocaj în amonte (linia de umplere) sau în aval (ritmul de "
            "schimb al paleților), viteza robotului nu poate elimina singură blocajul."
        ),
        "Funcționează și pentru alte industrii (ex. vopsele, chimie)?": (
            "Principiul de paletizare a găleților poate fi analizat, dar cerințele tehnice, de ambalaj "
            "și de siguranță pentru industrii din afara celei alimentare trebuie validate separat."
        ),
        "Unde are Tech-Con sedii / echipe în România?": (
            "Tech-Con operează din Dragomirești-Deal (zona București-Ilfov), Iași și Timișoara, "
            "acoperind evaluări tehnice și demonstrații la nivel național."
        ),
    }
    selected_q = st.selectbox("Selectează o întrebare:", list(faq.keys()))
    st.info(faq[selected_q])

    st.button(
        "🔍 Testează acum fabrica ta în Evaluatorul UR20 →",
        type="primary",
        use_container_width=True,
        on_click=go_to,
        args=("eval",),
    )

# Footer discret
st.divider()
st.caption(
    "Prototip web demonstrativ (Start Your StartUP 2026 – AI-Powered Business Challenge) • "
    "Folosiți exclusiv date fictive de test."
)