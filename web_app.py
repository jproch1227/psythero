import streamlit as st
from google import genai
import re

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="CBT Clinical Pro", layout="wide")

# --- INICJALIZACJA STANU (Zapobieganie błędom) ---
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
    /* Panel boczny */
    [data-testid="stSidebar"] { background-color: #1a365d; color: white; }

    /* Etykiety z ikonkami */
    .custom-label { 
        margin-top: 15px; 
        margin-bottom: 5px; 
        display: flex; 
        align-items: center; 
    }
    .label-text { 
        font-size: 14px; 
        font-weight: 600; 
        color: #f0f2f6; 
        margin-right: 8px; 
    }
    
    /* Ikonka INFO */
    .info-icon {
        background-color: #2b6cb0; 
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
        background: #2d3748; 
        color: #fff; 
        padding: 8px;
        border-radius: 4px; 
        font-size: 12px; 
        width: 260px; 
        z-index: 1000; 
        font-weight: normal; 
        line-height: 1.4;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

    /* Karta Raportu - Wygląd dokumentu */
    .report-card {
        background-color: white; 
        padding: 15mm; 
        color: black;
        font-family: 'Times New Roman', serif; 
        border: 1px solid #ccc; 
        margin-top: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .report-card h2 { 
        color: #1a365d; 
        border-bottom: 1px solid #ddd; 
        margin-top: 25px; 
        font-size: 20px; 
    }
    .report-card table { 
        width: 100%; 
        border-collapse: collapse; 
        margin: 15px 0; 
    }
    .report-card th, .report-card td { 
        border: 1px solid black !important; 
        padding: 8px; 
        text-align: left; 
        vertical-align: top; 
        font-size: 14px; 
    }
    .report-card th { 
        background-color: #f2f2f2; 
        font-weight: bold; 
    }
    
    /* Pola tekstowe - Stylizacja */
    .stTextArea textarea { 
        border: 1px solid #4a5568 !important; 
        height: 130px !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCJE POMOCNICZE ---
def render_label(text, tooltip):
    """Wyświetla etykietę z ikonką [i] i dymkiem."""
    st.markdown(f"""
        <div class="custom-label">
            <span class="label-text">{text}</span>
            <div class="info-icon" data-tooltip="{tooltip}">i</div>
        </div>
    """, unsafe_allow_html=True)

def extract_pure_html(text):
    """Czyści odpowiedź AI, zostawiając tylko czysty HTML."""
    text = re.sub(r'```html', '', text, flags=re.IGNORECASE)
    text = re.sub(r'```', '', text)
    
    start = text.find('<')
    end = text.rfind('>')
    
    if start != -1 and end != -1:
        return text[start:end+1].strip()
    return text.strip()

# --- SŁOWNIK TOOLTIPÓW ---
INFO = {
    "id": "Unikalny numer identyfikacyjny w Twojej dokumentacji.",
    "terapeuta": "Imię i nazwisko klinicysty prowadzącego.",
    "diag": "Kod ICD-10/DSM-5 (np. F42.1).",
    "ryz": "Myśli S., plany, dostępność środków, czynniki chroniące.",
    "prob": "Opis objawów, czasu trwania i wpływu na funkcjonowanie.",
    "mysl": "Dosłowne cytaty pacjenta ('Coś jest ze mną nie tak').",
    "syt": "Kontekst: Kto? Gdzie? Kiedy? Co było wyzwalaczem?",
    "auto": "Co przemknęło przez głowę w ułamku sekundy?",
    "emo": "Nazwij emocje (lęk, złość) i odczucia z ciała.",
    "zach": "Co pacjent zrobił (uniknął, sprawdził, uciekł)?",
    "koszt": "Krótkoterminowa ulga vs Długoterminowe podtrzymanie problemu.",
    "hipo": "Mechanizm: Dlaczego problem trwa? (np. błędne koło unikania)."
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
    
    #
