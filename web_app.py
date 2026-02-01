import streamlit as st
from google import genai
from datetime import datetime
import re

# --- KONFIGURACJA ---
st.set_page_config(page_title="CBT Clinical Pro", layout="wide")

# --- INICJALIZACJA STANU (Zapobiega błędom przy odświeżaniu) ---
keys = ['id_p', 'terapeuta', 'diagnoza', 'ryzyko', 'problemy', 'mysli_raw', 
        'p_sit', 'p_mysl', 'p_emocja', 'p_zach', 'p_koszt', 'relacja', 'historia', 'hipotezy', 'final_report']
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = ""
if 'step' not in st.session_state:
    st.session_state.step = 1

# --- CSS (WYGLĄD) ---
st.markdown("""
    <style>
    /* Ukryj standardowe etykiety Streamlit (te małe literki d, r, p) */
    div[data-testid="stWidgetLabel"] { display: none; }

    /* Panel boczny */
    [data-testid="stSidebar"] { background-color: #1a365d; color: white; }
    
    /* Etykiety z ikonkami */
    .custom-label {
        display: flex; align-items: center;
        margin-bottom: 5px; margin-top: 15px;
    }
    .label-text {
        font-size: 14px; font-weight: 600;
        color: #f0f2f6; margin-right: 8px;
    }
    
    /* Ikonka INFO */
    .info-wrapper { position: relative; display: inline-block; cursor: help; }
    .info-icon {
        background-color: #2b6cb0; color: white;
        border-radius: 50%; width: 18px; height: 18px;
        display: flex; align-items: center; justify-content: center;
        font-size: 12px; font-weight: bold; font-family: serif;
    }
    
    /* Dymek (Tooltip) */
    .tooltip-content {
        visibility: hidden; width: 260px;
        background-color: #2d3748; color: #fff;
        text-align: left; border-radius: 6px; padding: 10px;
        position: absolute; z-index: 1000;
        bottom: 130%; left: 50%; transform: translateX(-50%);
        opacity: 0; transition: opacity 0.2s;
        font-size: 12px; line-height: 1.4;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        pointer-events: none;
    }
    .info-wrapper:hover .tooltip-content { visibility: visible; opacity: 1; }

    /* Karta Raportu */
    .report-card {
        background-color: white; padding: 15mm; color: black;
        font-family: 'Times New Roman', serif; border: 1px solid #000;
        line-height: 1.5; margin-top: 20px;
    }
    .report-card h1, .report-card h2, .report-card h3 { color: #000; margin-top: 15px; margin-bottom: 10px; }
    .report-card ul { margin-bottom: 10px; }
    .report-card table { width: 100%; border-collapse: collapse; margin: 15px 0; }
    .report-card th, .report-card td { border: 1px solid black !important; padding: 8px; vertical-align: top; text-align: left; }
    .report-card th { background-color: #f2f2f2; }
    
    /* Pola tekstowe */
    .stTextInput input { border: 1px solid #4a5568 !important; }
    .stTextArea textarea { border: 1px solid #4a5568 !important; height: 130px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCJE POMOCNICZE ---
def render_label(text, tooltip):
    """Renderuje etykietę z tooltipem."""
    st.markdown(f"""
        <div class="custom-label">
            <span class="label-text">{text}</span>
            <div class="info-wrapper">
                <div class="info-icon">i</div>
                <div class="tooltip-content">{tooltip}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def oczysc_html(text):
    """Funkcja naprawcza: Usuwa wszystko co nie jest HTMLem."""
    # 1. Usuń znaczniki Markdown
    text = re.sub(r'```html', '', text, flags=re.IGNORECASE)
    text = re.sub(r'```', '', text)
    
    # 2. Znajdź początek prawdziwego HTMLa (od h1, div lub table)
    # To zapobiega wyświetlaniu tekstu typu "Oto Twój raport:"
    start_match = re.search(r'<(h1|div|table|section)', text, re.IGNORECASE)
    if start_match:
        text = text[start_match.start():]
        
    return text.strip()

# --- SŁOWNIK POMOCY ---
TOOLTIPS = {
    "diagnoza": "Wpisz kod ICD-10 lub DSM-5 (np. F32.1).",
    "ryzyko": "Opisz charakter myśli S., plany i zabezpieczenia. Jeśli ryzyko jest wysokie, AI doda czerwony alert.",
    "problemy": "Główne objawy zgłaszane przez pacjenta. AI pogrupuje je w triadę Becka.",
    "mysli": "Dosłowne cytaty z pacjenta. AI zidentyfikuje w nich błędy poznawcze.",
    "p_sit": "Kontekst zdarzenia: Kto? Gdzie? Kiedy?",
    "p_mysl": "Co dokładnie przemknęło przez głowę?",
    "p_emocja": "Emocje i reakcje z ciała.",
    "p_zach": "Co pacjent zrobił lub czego uniknął?",
    "p_koszt": "Skutek: Krótka ulga vs Długi koszt.",
    "hipotezy": "Twoja interpretacja mechanizmu problemu."
}

# --- PANEL BOCZNY ---
with st.sidebar:
    st.title("🛡️ Panel")
    api_key = st.text_input("Klucz Gemini API", type="password")
    st.divider()
    st.write(f"Krok {st.session_state.step} / 5")
    if st.button("🗑️ Resetuj"):
        st.session_state.clear()
        st.rerun()

# --- KROK 1 ---
if st.session_state.step == 1:
    st.subheader("🔵 Krok 1: Dane podstawowe")
    st.text_input("ID Pacjenta", key="id_p_input", value=st.session_state.id_p)
    st.session_state.id_p = st.session_state.id_p_input # Sync manualny bo ukryliśmy etykiety
    
    st.text_input("Terapeuta", key="terapeuta_input", value=st.session_state.terapeuta)
    st.session_state.terapeuta = st.session_state.terapeuta_input
    
    render_label("Diagnoza (ICD/DSM)", TOOLTIPS["diagnoza"])
    st.session_state.diagnoza = st.text_input("diag_inp", value=st.session_state.diagnoza)
    
    render_label("Ocena ryzyka / Plan bezpieczeństwa", TOOLTIPS["ryzyko"])
    st.session_state.ryzyko = st.text_area("ryz_inp", value=st.session_state.ryzyko)
    
    if st.button("Dalej ➡️"): st.session_state.step = 2; st.rerun()

# --- KROK 2 ---
elif st.session_state.step == 2:
    st.subheader("🟣 Krok 2: Objawy i Myśli")
    render_label("Objawy i problemy", TOOLTIPS["problemy"])
    st.session_state.problemy = st.text_area("prob_inp", value=st.session_state.problemy)
    
    render_label("Myśli automatyczne (Cytaty)", TOOLTIPS["mysli"])
    st.session_state.mysli_raw = st.text_area("mysli_inp", value=st.session_state.mysli_raw)
    
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 1; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 3; st.rerun()

# --- KROK 3 ---
elif st.session_state.step == 3:
    st.subheader("🟣 Krok 3: Pętla Podtrzymująca")
    render_label("Sytuacja (Wyzwalacz)", TOOLTIPS["p_sit"])
    st.session_state.p_sit = st.text_area("sit_inp", value=st.session_state.p_sit)
    render_label("Myśl Automatyczna", TOOLTIPS["p_mysl"])
    st.session_state.p_mysl = st.text_area("mysl_loop_inp", value=st.session_state.p_mysl)
    render_label("Emocja / Ciało", TOOLTIPS["p_emocja"])
    st.session_state.p_emocja = st.text_area("emo_inp", value=st.session_state.p_emocja)
    render_label("Zachowanie (Strategia)", TOOLTIPS["p_zach"])
    st.session_state.p_zach = st.text_area("zach_inp", value=st.session_state.p_zach)
    
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 2; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 4; st.rerun()

# --- KROK 4 ---
elif st.session_state.step == 4:
    st.subheader("🔵 Krok 4: Kontekst")
    st.text_area("Relacja terapeutyczna", key="rel_inp", value=st.session_state.relacja)
    st.session_state.relacja = st.session_state.rel_inp
    
    st.text_area("Historia / Rodzina", key="hist_inp", value=st.session_state.historia)
    st.session_state.historia = st.session_state.hist_inp
    
    render_label("Hipotezy kliniczne", TOOLTIPS["hipotezy"])
    st.session_state.hipotezy = st.text_area("hipo_inp", value=st.session_state.hipotezy)
    
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 3; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 5; st.rerun()

# --- KROK 5 ---
elif st.session_state.step == 5:
    st.subheader("🚀 Krok 5: Generowanie")
    if st.button("GENERUJ PEŁNY RAPORT"):
        if not api_key: st.error("Podaj klucz API!")
        else:
            try:
                client = genai.Client(api_key=api_key)
                prompt = f"""Jesteś superwizorem CBT. Twoim zadaniem jest wygenerowanie raportu w CZYSTYM HTML.
                
                INSTRUKCJA KRYTYCZNA:
                - NIE PISZ "Oto raport". NIE PISZ "```html".
                - Twoja odpowiedź ma się zaczynać od znaku < i kończyć na >.
                
                ZAWARTOŚĆ:
                1. Dane pacjenta i Alert Ryzyka.
                2. Tabela Pętli Becka (Sytuacja, Myśl, Emocja, Zachowanie).
                3. Triada Becka i Zniekształcenia poznawcze.
                4. Tabela Padesky'ego (Z dowodami za/przeciw i myślą alternatywną).
                5. Cele SMART.
                
                DANE PACJENTA:
                ID: {st.session_state.id_p}, Diagnoza: {st.session_state.diagnoza}
                Ryzyko: {st.session_state.ryzyko}
                Problemy: {st.session_state.problemy}
                Myśli: {st.session_state.mysli_raw}
                Pętla: {st.session_state.p_sit} -> {st.session_state.p_mysl} -> {st.session_state.p_emocja} -> {st.session_state.p_zach}.
                """
                with st.spinner('AI pisze raport...'):
                    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                    # TUTAJ JEST KLUCZOWA POPRAWKA - CZYSZCZENIE HTML
                    clean_report = oczysc_html(response.text)
                    st.session_state.final_report = clean_report
            except Exception as e: st.error(f"Błąd: {e}")

    # Wyświetlanie gotowego raportu
    if st.session_state.final_report:
        st.markdown(f"<div class='report-card'>{st.session_state.final_report}</div>", unsafe_allow_html=True)
        st.download_button("Pobierz Raport (HTML)", st.session_state.final_report, file_name=f"Raport_{st.session_state.id_p}.html")
