import streamlit as st
from google import genai
from datetime import datetime
import re

# --- KONFIGURACJA I STYL ---
st.set_page_config(page_title="CBT Clinical Professional", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1a365d; color: white; }
    .stProgress > div > div > div > div { background-color: #1a365d; }
    
    /* --- CSS DLA TOOLTIPÓW (DYMKÓW) --- */
    
    /* Kontener dla całej linii: Tekst Etykiety + Ikonka */
    .custom-label-box {
        display: flex;
        align-items: center;
        margin-bottom: 2px; /* Mały odstęp od pola tekstowego */
        margin-top: 10px;
    }
    
    /* Tekst etykiety (np. "Sytuacja") */
    .custom-label-text {
        font-size: 14px;
        font-weight: 600; /* Pogrubienie jak w Streamlit */
        color: #31333F;
        margin-right: 8px; /* Odstęp od ikonki */
    }

    /* Kontener samej ikonki (żeby dymek wiedział gdzie się pojawić) */
    .tooltip-container {
        position: relative;
        display: inline-block;
        cursor: help;
    }

    /* Wygląd ikonki [i] - SVG */
    .info-icon-svg {
        width: 18px;
        height: 18px;
        fill: #3b82f6; /* Twój niebieski kolor */
        vertical-align: middle;
        transition: opacity 0.2s;
    }
    .info-icon-svg:hover {
        opacity: 0.7;
    }

    /* Wygląd dymka z tekstem */
    .tooltip-content {
        visibility: hidden;
        width: 280px;
        background-color: #1e293b; /* Ciemnogranatowe tło */
        color: #fff;
        text-align: left;
        border-radius: 6px;
        padding: 10px 12px;
        font-size: 12px;
        font-weight: normal;
        line-height: 1.4;
        
        /* Pozycjonowanie dymka */
        position: absolute;
        z-index: 1000;
        bottom: 135%; /* Nad ikonką */
        left: 50%; 
        transform: translateX(-50%); /* Wycentrowanie */
        
        opacity: 0;
        transition: opacity 0.3s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

    /* Strzałka w dół pod dymkiem */
    .tooltip-content::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #1e293b transparent transparent transparent;
    }

    /* Pokazanie dymka po najechaniu */
    .tooltip-container:hover .tooltip-content {
        visibility: visible;
        opacity: 1;
    }
    
    /* --- INNE STYLE --- */
    .report-card { background-color: white; padding: 20mm; color: black; font-family: 'Times New Roman', serif; border: 1px solid #ccc; }
    .stTextArea textarea { border: 1px solid #cbd5e0 !important; height: 130px !important; }
    .clinician-zone { border-left: 5px solid #2b6cb0; padding-left: 15px; background-color: #f7fafc; padding: 10px; margin-bottom: 15px;}
    .ai-zone { border-left: 5px solid #805ad5; padding-left: 15px; background-color: #f3e8ff; padding: 10px; margin-bottom: 15px;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCJA RENDERUJĄCA ETYKIETĘ Z IKONKĄ ---
def render_custom_label(label_text, tooltip_text):
    # Ikona SVG (niebieskie kółko z "i")
    icon_html = """
    <svg class="info-icon-svg" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
    </svg>
    """
    
    html_code = f"""
    <div class="custom-label-box">
        <span class="custom-label-text">{label_text}</span>
        <div class="tooltip-container">
            {icon_html}
            <span class="tooltip-content">{tooltip_text}</span>
        </div>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

def wyczysc_html(tekst):
    tekst = re.sub(r'```html', '', tekst, flags=re.IGNORECASE)
    tekst = re.sub(r'```', '', tekst)
    return tekst.strip()

# --- SŁOWNIK TOOLTIPÓW ---
TOOLTIPS = {
    "diagnoza": "Wpisz oficjalny kod ICD-10 lub DSM-5 (np. F32.1).",
    "ryzyko_opis": "Opisz charakter myśli, plany, dostępność środków. Wymagane przy ryzyku umiarkowanym/wysokim.",
    "problemy": "Wymień główne objawy zgłaszane przez pacjenta (np. bezsenność, anhedonia).",
    "mysli": "Wpisz dosłowne cytaty: 'Jestem beznadziejny', 'Nic mi nie wyjdzie'. AI nazwie błędy poznawcze.",
    "p_sytuacja": "Kontekst: Kto? Gdzie? Kiedy? Co wyzwoliło zmianę nastroju?",
    "p_mysl": "Co dokładnie przemknęło przez głowę w TEJ chwili? (Myśl automatyczna lub obraz)",
    "p_emocja": "Nazwa emocji (np. lęk, złość) i jej nasilenie (0-100%).",
    "p_zachowanie": "Co pacjent zrobił (lub czego uniknął)? Strategie radzenia sobie.",
    "p_konsekwencja": "Krótkotrwała ulga vs Długoterminowe koszty (mechanizm błędnego koła).",
    "hipotezy": "Twoja interpretacja mechanizmu (np. schemat niekompetencji)."
}

# --- LOGIKA SESJI ---
if 'step' not in st.session_state: st.session_state.step = 1
def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1

# --- PANEL BOCZNY ---
with st.sidebar:
    st.title("🛡️ Panel Kontrolny")
    api_key = st.text_input("Klucz Gemini API", type="password")
    st.divider()
    st.info(f"Krok {st.session_state.step} / 5")
    st.progress(st.session_state.step / 5)

# --- KROK 1: FAKTY KLINICZNE ---
if st.session_state.step == 1:
    st.markdown("<div class='clinician-zone'><h3>🔵 Krok 1: Fakty Kliniczne</h3></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("ID Pacjenta", value=st.session_state.get('id_p', ""))
        st.session_state.id_p = st.session_state.get('id_p', "") # Sync
        
        # Przykład użycia nowej funkcji:
        render_custom_label("Diagnoza (ICD/DSM)", TOOLTIPS["diagnoza"])
        st.session_state.diagnoza = st.text_input("diag_hidden", value=st.session_state.get('diagnoza', ""), label_visibility="collapsed")
        
    with c2:
        st.text_input("Terapeuta", key="terapeuta_input", value=st.session_state.get('terapeuta', ""))
        st.session_state.terapeuta = st.session_state.get('terapeuta_input')
        
        st.text_input("Leczenie", key="leki_input", value=st.session_state.get('leki', ""))
        st.session_state.leki = st.session_state.get('leki_input')
    
    st.markdown("---")
    st.subheader("⚠️ Ocena Ryzyka")
    st.session_state.ryzyko_poziom = st.selectbox("Poziom ryzyka", ["Brak / Niskie", "Umiarkowane (plan bezp.)", "Wysokie (interwencja)"], index=0)
    
    render_custom_label("Opis ryzyka / Plan bezpieczeństwa", TOOLTIPS["ryzyko_opis"])
    st.session_state.ryzyko_opis = st.text_area("ryzyko_hidden", value=st.session_state.get('ryzyko_opis', ""), label_visibility="collapsed")
    
    st.button("Dalej ➡️", on_click=next_step)

# --- KROK 2: OBJAWY ---
elif st.session_state.step == 2:
    st.markdown("<div class='clinician-zone'><h3>🟣 Krok 2: Objawy i Myśli</h3></div>", unsafe_allow_html=True)
    
    render_custom_label("Objawy i problemy", TOOLTIPS["problemy"])
    st.session_state.problemy = st.text_area("problemy_hidden", value=st.session_state.get('problemy', ""), label_visibility="collapsed")
    
    render_custom_label("Myśli automatyczne (Cytaty)", TOOLTIPS["mysli"])
    st.session_state.mysli_raw = st.text_area("mysli_hidden", value=st.session_state.get('mysli_raw', ""), label_visibility="collapsed")
    
    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej ➡️", on_click=next_step)

# --- KROK 3: PĘTLA BECKA ---
elif st.session_state.step == 3:
    st.markdown("<div class='clinician-zone'><h3>🟣 Krok 3: Pętla Podtrzymująca</h3></div>", unsafe_allow_html=True)
    
    # Sytuacja
    render_custom_label("Sytuacja (Wyzwalacz)", TOOLTIPS["p_sytuacja"])
    st.session_state.p_sytuacja = st.text_area("syt_hidden", value=st.session_state.get('p_sytuacja', ""), label_visibility="collapsed")
    
    # Myśl
    render_custom_label("Myśl Automatyczna", TOOLTIPS["p_mysl"])
    st.session_state.p_mysl = st.text_area("mysl_hidden", value=st.session_state.get('p_mysl', ""), label_visibility="collapsed")
    
    # Emocja
    render_custom_label("Emocja / Ciało", TOOLTIPS["p_emocja"])
    st.session_state.p_emocja = st.text_area("emocja_hidden", value=st.session_state.get('p_emocja', ""), label_visibility="collapsed")
    
    # Zachowanie
    render_custom_label("Zachowanie (Strategia)", TOOLTIPS["p_zachowanie"])
    st.session_state.p_zachowanie = st.text_area("zach_hidden", value=st.session_state.get('p_zachowanie', ""), label_visibility="collapsed")
    
    # Konsekwencja
    render_custom_label("Konsekwencja", TOOLTIPS["p_konsekwencja"])
    st.session_state.p_konsekwencja = st.text_area("kons_hidden", value=st.session_state.get('p_konsekwencja', ""), label_visibility="collapsed")
    
    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej ➡️", on_click=next_step)

# --- KROK 4: DANE JAKOŚCIOWE ---
elif st.session_state.step == 4:
    st.markdown("<div class='clinician-zone'><h3>🔵 Krok 4: Relacja i Hipotezy</h3></div>", unsafe_allow_html=True)
    
    st.text_area("Relacja terapeutyczna", key="relacja_input", value=st.session_state.get('relacja', ""))
    st.session_state.relacja = st.session_state.get('relacja_input')
    
    st.text_area("Kontekst historyczny", key="historia_input", value=st.session_state.get('historia', ""))
    st.session_state.historia = st.session_state.get('historia_input')
    
    render_custom_label("Hipotezy kliniczne", TOOLTIPS["hipotezy"])
    st.session_state.hipotezy = st.text_area("hipotezy_hidden", value=st.session_state.get('hipotezy', ""), label_visibility="collapsed")
    
    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej ➡️", on_click=next_step)

# --- KROK 5: GENEROWANIE ---
elif st.session_state.step == 5:
    st.header("Krok 5: Finalizacja")
    
    add_goals = st.checkbox("✅ Zaproponuj Cele Terapeutyczne (SMART)", value=True)
    add_protocol = st.checkbox("✅ Zaproponuj Protokół Leczenia (Plan Terapii)", value=True)
    
    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    
    if c2.button("🚀 GENERUJ PEŁNĄ DOKUMENTACJĘ"):
        if not api_key:
            st.error("Brak klucza API!")
        else:
            try:
                client = genai.Client(api_key=api_key)
                
                # Budowanie instrukcji dla AI
                goals_instruction = ""
                if add_goals:
                    goals_instruction = """
                    6. CELE TERAPEUTYCZNE:
                       - Zaproponuj 3 konkretne cele SMART.
                       - Podziel na krótko- i długoterminowe.
                    """
                protocol_instruction = ""
                if add_protocol:
                    protocol_instruction = f"""
                    7. PROTOKÓŁ LECZENIA:
                       - Zaproponuj ramowy plan terapii dla diagnozy {st.session_state.diagnoza}.
                       - Etapy i techniki (np. dialog sokratejski).
                    """

                prompt = f"""Jesteś profesjonalnym superwizorem CBT. Stwórz SZCZEGÓŁOWY raport kliniczny.

                WYMAGANIA:
                - Kod HTML (bez markdown ```html).
                - Używaj tagów <h1>, <h2>, <table>, <ul>, <div class="alert">, <li class="propozycja">.
                
                TREŚĆ:
                1. DANE I ALERT RYZYKA: Jeśli ryzyko > Niskie, dodaj czerwony alert.
                2. OBJAWY I ZNIEKSZTAŁCENIA: Pogrupuj myśli ({st.session_state.mysli_raw}) wg błędów poznawczych.
                3. MODEL KONCEPTUALIZACJI: Stwórz Tabelę Pętli Becka z: {st.session_state.p_sytuacja}, {st.session_state.p_mysl}, {st.session_state.p_emocja}, {st.session_state.p_zachowanie}, {st.session_state.p_konsekwencja}.
                4. TRIADA DEPRESYJNA: Opisz JA, ŚWIAT, PRZYSZŁOŚĆ.
                5. RELACJA: Przepisz dokładnie: {st.session_state.relacja}, {st.session_state.historia}, {st.session_state.hipotezy}.
                {goals_instruction}
                {protocol_instruction}

                DANE PACJENTA:
                ID: {st.session_state.id_p}, Diagnoza: {st.session_state.diagnoza}, Terapeuta: {st.session_state.terapeuta}
                Ryzyko Opis: {st.session_state.ryzyko_opis}
                Problemy: {st.session_state.problemy}
                """

                with st.spinner('Generowanie szczegółowego raportu...'):
                    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                    wynik = wyczysc_html(response.text)
                    st.markdown(f"<div class='report-card'>{wynik}</div>", unsafe_allow_html=True)
                    st.download_button("Pobierz Raport (HTML)", wynik, file_name=f"Karta_CBT_{st.session_state.id_p}.html")
                    
            except Exception as e:
                st.error(f"Błąd: {e}")
