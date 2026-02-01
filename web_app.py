import streamlit as st
from google import genai
from datetime import datetime
import re

# --- KONFIGURACJA ---
st.set_page_config(page_title="CBT Clinical Pro", layout="wide")

# --- INICJALIZACJA STANU ---
keys = ['id_p', 'terapeuta', 'diagnoza', 'ryzyko', 'problemy', 'mysli_raw', 
        'p_sit', 'p_mysl', 'p_emocja', 'p_zach', 'p_koszt', 'relacja', 'historia', 'hipotezy', 'final_report']
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = ""
if 'step' not in st.session_state:
    st.session_state.step = 1

# --- CSS DLA WYGLĄDU I TOOLTIPÓW ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1a365d; color: white; }
    
    .custom-label {
        display: flex; align-items: center;
        margin-bottom: 4px; margin-top: 15px;
    }
    .label-text {
        font-size: 14px; font-weight: 600;
        color: #f0f2f6; margin-right: 8px;
    }
    
    .info-wrapper { position: relative; display: inline-block; cursor: help; }
    .info-icon {
        background-color: #2b6cb0; color: white;
        border-radius: 50%; width: 20px; height: 20px;
        display: flex; align-items: center; justify-content: center;
        font-size: 12px; font-weight: bold; font-family: serif;
    }
    
    .tooltip-content {
        visibility: hidden; width: 280px;
        background-color: #2d3748; color: #fff;
        text-align: left; border-radius: 6px; padding: 12px;
        position: absolute; z-index: 100;
        bottom: 125%; left: 50%; transform: translateX(-50%);
        opacity: 0; transition: opacity 0.3s;
        font-size: 12px; line-height: 1.4;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
    }
    .info-wrapper:hover .tooltip-content { visibility: visible; opacity: 1; }

    .report-card {
        background-color: white; padding: 20mm; color: black;
        font-family: 'Times New Roman', serif; border: 1px solid #000;
        line-height: 1.5;
    }
    .report-card h1, .report-card h2, .report-card h3 { color: #1a365d; margin-top: 20px; }
    .report-card table { width: 100%; border-collapse: collapse; margin: 15px 0; }
    .report-card th, .report-card td { border: 1px solid black !important; padding: 10px; vertical-align: top; }
    .report-card th { background-color: #f2f2f2; }
    
    .stTextArea textarea { border: 1px solid #4a5568 !important; height: 130px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCJE POMOCNICZE ---
def render_info_label(label, tooltip):
    st.markdown(f"""
        <div class="custom-label">
            <span class="label-text">{label}</span>
            <div class="info-wrapper">
                <div class="info-icon">i</div>
                <div class="tooltip-content">{tooltip}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def extract_html(text):
    """Wyciąga czysty HTML, usuwając znaczniki Markdown i zbędny tekst AI."""
    # Usuń znaczniki ```html i ```
    text = re.sub(r'```html', '', text, flags=re.IGNORECASE)
    text = re.sub(r'```', '', text)
    # Znajdź początek i koniec właściwego kodu HTML
    match = re.search(r'(<(h1|div|table|section).*<\/.*>)', text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text.strip()

# --- SŁOWNIK POMOCY ---
TOOLTIPS = {
    "diagnoza": "Wpisz kod ICD-10 lub DSM-5 (np. F32.1).",
    "ryzyko": "Opisz charakter myśli, plany i zabezpieczenia. AI wygeneruje alert bezpieczeństwa.",
    "problemy": "Opisz zgłaszane trudności. AI pogrupuje je w spójny model CBT.",
    "mysli": "Dosłowne cytaty pacjenta. AI nazwie błędy poznawcze (np. katastrofizacja).",
    "p_sit": "Kontekst zdarzenia: Kto? Gdzie? Kiedy?",
    "p_mysl": "Co dokładnie przemknęło przez głowę?",
    "p_emocja": "Emocje i odczucia z ciała.",
    "p_zach": "Co pacjent zrobił lub czego uniknął?",
    "p_koszt": "Skutek: Krótka ulga vs Długi koszt.",
    "hipotezy": "Robocze założenia terapeuty wyjaśniające mechanizm problemu."
}

# --- PANEL BOCZNY ---
with st.sidebar:
    st.title("🛡️ Panel Kontrolny")
    api_key = st.text_input("Klucz Gemini API", type="password")
    st.divider()
    st.write(f"Krok {st.session_state.step} / 5")
    if st.button("🗑️ Resetuj formularz"):
        st.session_state.clear()
        st.rerun()

# --- NAWIGACJA KROKÓW ---
if st.session_state.step == 1:
    st.subheader("🔵 Krok 1: Dane podstawowe")
    st.session_state.id_p = st.text_input("ID Pacjenta", value=st.session_state.id_p, placeholder="Np. 001")
    st.session_state.terapeuta = st.text_input("Imię i nazwisko Terapeuty", value=st.session_state.terapeuta)
    render_info_label("Diagnoza (ICD/DSM)", TOOLTIPS["diagnoza"])
    st.session_state.diagnoza = st.text_input("diag_inp", value=st.session_state.diagnoza, label_visibility="collapsed")
    render_info_label("Ocena ryzyka / Plan bezpieczeństwa", TOOLTIPS["ryzyko"])
    st.session_state.ryzyko = st.text_area("ryz_inp", value=st.session_state.ryzyko, label_visibility="collapsed")
    if st.button("Dalej ➡️"): st.session_state.step = 2; st.rerun()

elif st.session_state.step == 2:
    st.subheader("🟣 Krok 2: Objawy i Myśli")
    render_info_label("Objawy i problemy", TOOLTIPS["problemy"])
    st.session_state.problemy = st.text_area("prob_inp", value=st.session_state.problemy, label_visibility="collapsed")
    render_info_label("Myśli automatyczne (Cytaty)", TOOLTIPS["mysli"])
    st.session_state.mysli_raw = st.text_area("mysli_inp", value=st.session_state.mysli_raw, label_visibility="collapsed")
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 1; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 3; st.rerun()

elif st.session_state.step == 3:
    st.subheader("🟣 Krok 3: Pętla Podtrzymująca")
    
    render_info_label("Sytuacja (Wyzwalacz)", TOOLTIPS["p_sit"])
    st.session_state.p_sit = st.text_area("syt_inp", value=st.session_state.p_sit, label_visibility="collapsed")
    render_info_label("Myśl Automatyczna", TOOLTIPS["p_mysl"])
    st.session_state.p_mysl = st.text_area("mysl_inp", value=st.session_state.p_mysl, label_visibility="collapsed")
    render_info_label("Emocja / Ciało", TOOLTIPS["p_emocja"])
    st.session_state.p_emocja = st.text_area("emo_inp", value=st.session_state.p_emocja, label_visibility="collapsed")
    render_info_label("Zachowanie (Strategia)", TOOLTIPS["p_zach"])
    st.session_state.p_zach = st.text_area("zach_inp", value=st.session_state.p_zach, label_visibility="collapsed")
    render_info_label("Konsekwencja (Koszt)", TOOLTIPS["p_koszt"])
    st.session_state.p_koszt = st.text_area("koszt_inp", value=st.session_state.p_koszt, label_visibility="collapsed")
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 2; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 4; st.rerun()

elif st.session_state.step == 4:
    st.subheader("🔵 Krok 4: Relacja i Hipotezy")
    st.session_state.relacja = st.text_area("Relacja", value=st.session_state.relacja, placeholder="Relacja terapeutyczna...")
    st.session_state.historia = st.text_area("Historia", value=st.session_state.historia, placeholder="Kontekst rodzinny...")
    render_info_label("Hipotezy kliniczne", TOOLTIPS["hipotezy"])
    st.session_state.hipotezy = st.text_area("hipo_inp", value=st.session_state.hipotezy, label_visibility="collapsed")
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 3; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 5; st.rerun()

elif st.session_state.step == 5:
    st.subheader("🚀 Krok 5: Generowanie")
    if st.button("GENERUJ PEŁNY RAPORT KLINICZNY"):
        if not api_key: st.error("Podaj klucz API!")
        else:
            try:
                client = genai.Client(api_key=api_key)
                prompt = f"""Jesteś doświadczonym superwizorem CBT. Na podstawie poniższych danych wygeneruj profesjonalny raport kliniczny wyłącznie w formacie HTML.
                
                ZASADY:
                - NIE używaj znaczników Markdown typu ```html. 
                - Zacznij odpowiedź bezpośrednio od tagów HTML (np. <h1> lub <div>).
                - Używaj tabel (<table>) dla Pętli Becka i Planu SMART.
                - Zidentyfikuj zniekształcenia poznawcze w myślach: {st.session_state.mysli_raw}.
                - Zbuduj kompletną Triadę Becka.
                
                DANE: ID {st.session_state.id_p}, Diagnoza {st.session_state.diagnoza}, Sytuacja {st.session_state.p_sit}, Myśl {st.session_state.p_mysl}, Zachowanie {st.session_state.p_zach}.
                """
                with st.spinner('Analizowanie materiału klinicznego...'):
                    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                    st.session_state.final_report = extract_html(response.text)
            except Exception as e: st.error(f"Błąd: {e}")

    if st.session_state.final_report:
        st.markdown(f"<div class='report-card'>{st.session_state.final_report}</div>", unsafe_allow_html=True)
        st.download_button("Pobierz raport (HTML)", st.session_state.final_report, file_name=f"Raport_CBT_{st.session_state.id_p}.html")
