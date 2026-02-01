import streamlit as st
from google import genai
from datetime import datetime
import re

# --- KONFIGURACJA I STYL ---
st.set_page_config(page_title="CBT Clinical Pro", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1a365d; color: white; }
    
    /* STYLE DLA ETYKIET I IKONEK INFO */
    .label-container { display: flex; align-items: center; margin-bottom: -15px; margin-top: 10px; }
    .label-text { font-size: 14px; font-weight: 600; color: #31333F; margin-right: 5px; }
    .info-tag { 
        background-color: #2b6cb0; color: white; border-radius: 50%; 
        width: 16px; height: 16px; display: inline-flex; 
        align-items: center; justify-content: center; 
        font-size: 10px; font-weight: bold; cursor: help;
        font-family: sans-serif;
    }

    /* RAPORT FINALNY */
    .report-card {
        background-color: white; padding: 20mm; color: black;
        font-family: 'Times New Roman', serif; border: 1px solid #000;
        line-height: 1.5;
    }
    .report-card h1 { text-align: center; border-bottom: 2px solid black; padding-bottom: 10px; }
    .report-card h2 { color: #1a365d; border-bottom: 1px solid #ccc; margin-top: 20px; }
    .report-card table { width: 100%; border-collapse: collapse; margin: 15px 0; }
    .report-card th, .report-card td { border: 1px solid black; padding: 8px; text-align: left; vertical-align: top; }
    .report-card th { background-color: #f2f2f2; }
    .warning { color: #c53030; font-weight: bold; }
    
    /* Ukrywanie domyślnych etykiet Streamlit */
    div[data-testid="stWidgetLabel"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCJA FILTRUJĄCA (NAPRAWIA PROBLEM KODU NA STRONIE) ---
def extract_html(text):
    """Wyciąga tylko zawartość między tagami HTML, usuwając komentarze AI."""
    # Szukaj wszystkiego od pierwszego tagu (np. <h1> lub <div>) do ostatniego
    match = re.search(r'(<(h1|div|table|section).*<\/.*>)', text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1)
    # Jeśli nie znalazło tagów, usuń chociaż backticki markdowna
    text = re.sub(r'```html', '', text, flags=re.IGNORECASE)
    text = re.sub(r'```', '', text)
    return text

def render_label(text, tooltip):
    """Renderuje tekst etykiety z małą niebieską ikonką info."""
    st.markdown(f"""
        <div class="label-container">
            <span class="label-text">{text}</span>
            <span class="info-tag" title="{tooltip}">i</span>
        </div>
    """, unsafe_allow_html=True)

# --- SŁOWNIK POMOCY ---
INFO = {
    "diagnoza": "Wpisz kod ICD-10/DSM-5. AI użyje tego do zaproponowania protokołu.",
    "ryzyko": "Opisz myśli S., plany i czynniki chroniące. Krytyczne dla bezpieczeństwa.",
    "problemy": "Główne trudności pacjenta. AI pogrupuje je w triadę i zidentyfikuje procesy.",
    "mysli": "Dosłowne cytaty. AI zidentyfikuje w nich zniekształcenia poznawcze.",
    "p_sytuacja": "Kontekst zdarzenia: Kto, co, gdzie, kiedy?",
    "p_mysl": "Co dokładnie przemknęło przez głowę w tej chwili?",
    "p_emocja": "Emocje i odczucia z ciała.",
    "p_zachowanie": "Co pacjent zrobił lub czego uniknął?",
    "p_koszt": "Skutek zachowania: Krótka ulga vs długi koszt.",
    "hipotezy": "Twoja interpretacja (np. schemat wadliwości)."
}

# --- LOGIKA SESJI ---
if 'step' not in st.session_state: st.session_state.step = 1
def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1

# --- PANEL BOCZNY ---
with st.sidebar:
    st.title("⚙️ Nawigacja")
    api_key = st.text_input("Klucz Gemini API", type="password")
    st.divider()
    st.progress(st.session_state.step / 5)
    if st.button("🗑️ Reset"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# --- KROKI FORMULARZA ---
if st.session_state.step == 1:
    st.subheader("Krok 1: Dane podstawowe")
    st.session_state.id_p = st.text_input("ID", value=st.session_state.get('id_p', ""), placeholder="ID Pacjenta")
    st.session_state.terapeuta = st.text_input("T", value=st.session_state.get('terapeuta', ""), placeholder="Terapeuta")
    
    render_label("Diagnoza", INFO["diagnoza"])
    st.session_state.diagnoza = st.text_input("d", value=st.session_state.get('diagnoza', ""))
    
    render_label("Ocena ryzyka", INFO["ryzyko"])
    st.session_state.ryzyko = st.text_area("r", value=st.session_state.get('ryzyko', ""))
    st.button("Dalej ➡️", on_click=next_step)

elif st.session_state.step == 2:
    st.subheader("Krok 2: Objawy i Myśli")
    render_label("Problemy", INFO["problemy"])
    st.session_state.problemy = st.text_area("p", value=st.session_state.get('problemy', ""))
    
    render_label("Myśli automatyczne (Cytaty)", INFO["mysli"])
    st.session_state.mysli_raw = st.text_area("m", value=st.session_state.get('mysli_raw', ""))
    
    c1, c2 = st.columns(2)
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej ➡️", on_click=next_step)

elif st.session_state.step == 3:
    st.subheader("Krok 3: Pętla CBT")
    render_label("Sytuacja", INFO["p_sytuacja"])
    st.session_state.p_sit = st.text_area("s1", value=st.session_state.get('p_sit', ""))
    render_label("Myśl", INFO["p_mysl"])
    st.session_state.p_mysl = st.text_area("s2", value=st.session_state.get('p_mysl', ""))
    render_label("Zachowanie", INFO["p_zachowanie"])
    st.session_state.p_zach = st.text_area("s3", value=st.session_state.get('p_zach', ""))
    
    c1, c2 = st.columns(2)
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej ➡️", on_click=next_step)

elif st.session_state.step == 4:
    st.subheader("Krok 4: Relacja i Hipotezy")
    st.session_state.relacja = st.text_area("Relacja", value=st.session_state.get('relacja', ""), placeholder="Relacja terapeutyczna...")
    st.session_state.historia = st.text_area("Historia", value=st.session_state.get('historia', ""), placeholder="Kontekst rodzinny...")
    render_label("Hipotezy", INFO["hipotezy"])
    st.session_state.hipotezy = st.text_area("h", value=st.session_state.get('hipotezy', ""))
    
    c1, c2 = st.columns(2)
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej ➡️", on_click=next_step)

elif st.session_state.step == 5:
    st.subheader("Krok 5: Generowanie")
    add_goals = st.checkbox("Zaproponuj cele SMART", value=True)
    add_protocol = st.checkbox("Zaproponuj protokół leczenia", value=True)
    
    if st.button("🚀 GENERUJ RAPORT"):
        if not api_key: st.error("Podaj klucz API!")
        else:
            client = genai.Client(api_key=api_key)
            prompt = f"""Jesteś superwizorem CBT. Wygeneruj raport kliniczny w czystym HTML. 
            NIE PISZ żadnych wyjaśnień przed ani po kodzie. NIE używaj backticków ```.
            
            WYMAGANE SEKCJE (Wypełnij na podstawie danych):
            1. Alert Ryzyka (jeśli dotyczy).
            2. Tabela Pętli Becka (Sytuacja, Myśl, Zachowanie).
            3. Triada Becka i Zniekształcenia Poznawcze.
            4. Tabela Padesky'ego (z Twoimi propozycjami myśli alternatywnych).
            5. Cele SMART i Protokół leczenia (etapy).
            
            DANE: ID: {st.session_state.id_p}, Diagnoza: {st.session_state.diagnoza}, 
            Problemy: {st.session_state.problemy}, Myśli: {st.session_state.mysli_raw},
            Pętla: {st.session_state.p_sit} / {st.session_state.p_mysl} / {st.session_state.p_zach},
            Historia/Hipotezy: {st.session_state.historia} / {st.session_state.hipotezy}.
            """
            
            with st.spinner('AI buduje raport...'):
                response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                clean_html = extract_html(response.text)
                st.markdown(f"<div class='report-card'>{clean_html}</div>", unsafe_allow_html=True)
