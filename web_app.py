import streamlit as st
from google import genai
import re

# --- KONFIGURACJA ---
st.set_page_config(page_title="CBT Clinical Pro", layout="wide")

# --- CSS (STYLIZACJA) ---
st.markdown("""
    <style>
    /* Panel boczny */
    [data-testid="stSidebar"] { background-color: #1a365d; color: white; }

    /* Ukrywanie domyślnych etykiet (dodatkowe zabezpieczenie) */
    .stTextInput label, .stTextArea label { display: none; }

    /* Własne etykiety */
    .custom-label { 
        margin-top: 20px; 
        margin-bottom: 5px; 
        display: flex; 
        align-items: center; 
    }
    .label-text { 
        font-size: 14px; 
        font-weight: 600; 
        color: #e2e8f0; /* Jasny tekst na ciemnym tle (zależnie od motywu) */
        margin-right: 8px; 
    }
    
    /* Ikonka INFO */
    .info-icon {
        background-color: #3182ce; 
        color: white; 
        border-radius: 50%; 
        width: 18px; 
        height: 18px;
        display: flex; 
        align-items: center; 
        justify-content: center; 
        font-size: 12px; 
        font-weight: bold; 
        cursor: help;
        position: relative;
    }
    
    /* Tooltip (Dymek) */
    .info-icon:hover::after {
        content: attr(data-tooltip);
        position: absolute; 
        left: 25px; 
        bottom: 0;
        background: #2d3748; 
        color: #fff; 
        padding: 10px;
        border-radius: 4px; 
        font-size: 12px; 
        width: 250px; 
        z-index: 1000; 
        font-weight: normal; 
        line-height: 1.4;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

    /* Karta Raportu */
    .report-card {
        background-color: white; 
        padding: 15mm; 
        color: black;
        font-family: 'Times New Roman', serif; 
        border: 1px solid #ccc; 
        margin-top: 20px;
    }
    .report-card h2 { color: #1a365d; border-bottom: 1px solid #ddd; margin-top: 25px; font-size: 20px; }
    .report-card table { width: 100%; border-collapse: collapse; margin: 15px 0; }
    .report-card th, .report-card td { border: 1px solid black !important; padding: 8px; text-align: left; vertical-align: top; font-size: 14px; }
    .report-card th { background-color: #f2f2f2; font-weight: bold; }
    
    /* Pola tekstowe */
    .stTextArea textarea { height: 120px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- INICJALIZACJA STANU (Zapobiega znikaniu danych) ---
# Używamy tych kluczy bezpośrednio w widgetach (parametr key=...)
default_keys = [
    'id_p', 'terapeuta', 'diagnoza', 'ryzyko', 
    'problemy', 'mysli_raw', 
    'p_sit', 'p_mysl', 'p_emocja', 'p_zach', 'p_koszt', 
    'relacja', 'historia', 'hipotezy', 
    'final_report'
]

for key in default_keys:
    if key not in st.session_state:
        st.session_state[key] = ""
if 'step' not in st.session_state:
    st.session_state.step = 1

# --- FUNKCJE POMOCNICZE ---
def render_label(text, tooltip):
    """Wyświetla Twoją własną etykietę z tooltipem."""
    st.markdown(f"""
        <div class="custom-label">
            <span class="label-text">{text}</span>
            <div class="info-icon" data-tooltip="{tooltip}">i</div>
        </div>
    """, unsafe_allow_html=True)

def extract_pure_html(text):
    """Czyści odpowiedź AI z Markdowna."""
    text = re.sub(r'```html', '', text, flags=re.IGNORECASE)
    text = re.sub(r'```', '', text)
    start = text.find('<')
    end = text.rfind('>')
    if start != -1 and end != -1:
        return text[start:end+1].strip()
    return text.strip()

# --- SŁOWNIK POMOCY ---
INFO = {
    "id": "Numer identyfikacyjny (np. 001/2024).",
    "terapeuta": "Imię i nazwisko osoby prowadzącej.",
    "diag": "Kod ICD-10 lub DSM-5.",
    "ryz": "Myśli S., plany, dostępność środków, czynniki chroniące.",
    "prob": "Lista zgłaszanych objawów i trudności.",
    "mysl": "Dosłowne cytaty pacjenta.",
    "syt": "Kto? Gdzie? Kiedy? Co wyzwoliło reakcję?",
    "auto": "Co pomyślał w tej chwili?",
    "emo": "Nazwa emocji i odczucia z ciała.",
    "zach": "Co zrobił (lub czego uniknął)?",
    "koszt": "Krótka ulga vs Długi koszt.",
    "hipo": "Mechanizm podtrzymujący problem."
}

# --- PANEL BOCZNY ---
with st.sidebar:
    st.title("🛡️ Panel")
    api_key = st.text_input("Klucz Gemini API", type="password")
    st.divider()
    st.progress(st.session_state.step / 5)
    if st.button("🗑️ Reset"):
        st.session_state.clear()
        st.rerun()

# --- KROKI FORMULARZA ---

# KROK 1
if st.session_state.step == 1:
    st.subheader("🔵 Krok 1: Dane podstawowe")
    
    render_label("ID Pacjenta", INFO["id"])
    # Używamy key="id_p" - Streamlit sam przypisze wartość do st.session_state.id_p
    # label_visibility="collapsed" ukrywa systemową etykietę
    st.text_input("Ukryta etykieta", key="id_p", label_visibility="collapsed")
    
    render_label("Terapeuta", INFO["terapeuta"])
    st.text_input("Ukryta etykieta", key="terapeuta", label_visibility="collapsed")
    
    render_label("Diagnoza (ICD/DSM)", INFO["diag"])
    st.text_input("Ukryta etykieta", key="diagnoza", label_visibility="collapsed")
    
    render_label("Ryzyko / Bezpieczeństwo", INFO["ryz"])
    st.text_area("Ukryta etykieta", key="ryzyko", label_visibility="collapsed")
    
    if st.button("Dalej ➡️"): st.session_state.step = 2; st.rerun()

# KROK 2
elif st.session_state.step == 2:
    st.subheader("🟣 Krok 2: Objawy")
    
    render_label("Objawy i problemy", INFO["prob"])
    st.text_area("Ukryta etykieta", key="problemy", label_visibility="collapsed")
    
    render_label("Myśli automatyczne (Cytaty)", INFO["mysl"])
    st.text_area("Ukryta etykieta", key="mysli_raw", label_visibility="collapsed")
    
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 1; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 3; st.rerun()

# KROK 3
elif st.session_state.step == 3:
    st.subheader("🟣 Krok 3: Pętla CBT")
    
    render_label("Sytuacja (Wyzwalacz)", INFO["syt"])
    st.text_area("Ukryta etykieta", key="p_sit", label_visibility="collapsed")
    
    render_label("Myśl Automatyczna", INFO["auto"])
    st.text_area("Ukryta etykieta", key="p_mysl", label_visibility="collapsed")
    
    render_label("Emocja / Ciało", INFO["emo"])
    st.text_area("Ukryta etykieta", key="p_emocja", label_visibility="collapsed")
    
    render_label("Zachowanie (Strategia)", INFO["zach"])
    st.text_area("Ukryta etykieta", key="p_zach", label_visibility="collapsed")
    
    render_label("Konsekwencja (Koszt)", INFO["koszt"])
    st.text_area("Ukryta etykieta", key="p_koszt", label_visibility="collapsed")
    
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 2; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 4; st.rerun()

# KROK 4
elif st.session_state.step == 4:
    st.subheader("🔵 Krok 4: Kontekst")
    
    render_label("Relacja Terapeutyczna", "Opis współpracy.")
    st.text_area("Ukryta etykieta", key="relacja", label_visibility="collapsed")
    
    render_label("Historia / Rodzina", "Tło historyczne.")
    st.text_area("Ukryta etykieta", key="historia", label_visibility="collapsed")
    
    render_label("Hipotezy kliniczne", INFO["hipo"])
    st.text_area("Ukryta etykieta", key="hipotezy", label_visibility="collapsed")
    
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 3; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 5; st.rerun()

# KROK 5
elif st.session_state.step == 5:
    st.subheader("🚀 Krok 5: Generowanie")
    
    if st.button("GENERUJ RAPORT"):
        if not api_key: st.error("Podaj klucz API!")
        else:
            try:
                client = genai.Client(api_key=api_key)
                prompt = f"""
                Jesteś superwizorem CBT. Wygeneruj raport w CZYSTYM HTML.
                WAŻNE: Nie dodawaj tekstu przed ani po kodzie HTML.
                
                STRUKTURA:
                <h2>1. Dane Pacjenta</h2>
                <h2>2. Tabela Pętli Becka</h2> (Kolumny: Sytuacja, Myśl, Emocja, Zachowanie, Konsekwencje)
                <h2>3. Triada i Zniekształcenia</h2>
                <h2>4. Tabela Padesky'ego</h2>
                <h2>5. Cele SMART</h2>

                DANE:
                ID: {st.session_state.id_p}, Diagnoza: {st.session_state.diagnoza}
                Ryzyko: {st.session_state.ryzyko}
                Problemy: {st.session_state.problemy}
                Myśli: {st.session_state.mysli_raw}
                
                PĘTLA:
                Sytuacja: {st.session_state.p_sit}
                Myśl: {st.session_state.p_mysl}
                Emocja: {st.session_state.p_emocja}
                Zachowanie: {st.session_state.p_zach}
                Konsekwencje: {st.session_state.p_koszt}
                """
                
                with st.spinner('Pisanie raportu...'):
                    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                    final_html = extract_pure_html(response.text)
                    st.session_state.final_report = final_html
                    
            except Exception as e: st.error(f"Błąd: {e}")

    if st.session_state.final_report:
        st.markdown(f"<div class='report-card'>{st.session_state.final_report}</div>", unsafe_allow_html=True)
        st.download_button("Pobierz Raport", st.session_state.final_report, file_name="raport.html")
