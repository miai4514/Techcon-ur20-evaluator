import re
from datetime import datetime
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

# Stil minimal pentru lizibilitate mobilă și carduri curate
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        max-width: 820px;
    }
    .hero-box {
        background: linear-gradient(135deg, #0f2942 0%, #1b4965 100%);
        color: #ffffff;
        padding: 1.2rem 1.4rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .hero-box h2 {
        margin: 0 0 0.3rem 0;
        font-size: 1.35rem;
        color: #ffffff;
    }
    .hero-box p {
        margin: 0;
        font-size: 0.92rem;
        color: #dbe9f4;
    }
    .step-card {
        background-color: #f4f7fa;
        border-left: 4px solid #1b4965;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.6rem;
        color: #111827;
    }
    .fact-box {
        background-color: #eef6ff;
        border: 1px solid #bfdbfe;
        padding: 0.9rem 1rem;
        border-radius: 10px;
        color: #1e3a5f;
        margin-bottom: 0.8rem;
    }
    .est-box {
        background-color: #fffbeb;
        border: 1px solid #fde68a;
        padding: 0.9rem 1rem;
        border-radius: 10px;
        color: #78350f;
        margin-bottom: 0.8rem;
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
    "crm_valid_payload": None,
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
    st.session_state.crm_notes = "Linie ambalare găleți 13 kg, 2 schimburi/zi. Dorim verificarea gripperului pe mostrele noastre."
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
# HEADER + BARĂ DE NAVIGARE SUS (3 SECȚIUNI SELECTABILE)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-box">
        <h2>🤖 Tech-Con UR20 | Evaluator Paletizare Găleți</h2>
        <p>Instrument demonstrativ pentru fabrici din România • Bazat pe aplicația UR20 implementată la PURATOS</p>
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
            # Banner verdict
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

            # Indicatori operaționali (fără ROI/economii salariale)
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

            # Separare clară: Fapte PURATOS vs. Estimări scenariu
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

    # Preluare automată a rezumatului din Secțiunea 1
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

            # Generare rezumat descărcabil pentru echipa comercială / CRM
            summary_lines = [
                f"FISA SOLICITARE EVALUARE TEHNICA TECH-CON UR20 (DEMO)",
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