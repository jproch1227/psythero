import streamlit as st
import streamlit.components.v1 as components
from google import genai
import re

# --- KONFIGURACJA ---
st.set_page_config(page_title="CBT Clinical Pro", layout="wide", initial_sidebar_state="expanded")

# --- INICJALIZACJA STANU ---
keys = ['id_p', 'terapeuta', 'diagnoza', 'ryzyko', 'problemy', 'mysli_raw', 
        'p_sit', 'p_mysl', 'p_emocja', 'p_zach', 'p_koszt', 'relacja', 'historia', 'hipotezy', 'final_report']
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = ""
if 'step' not in st.session_state:
    st.session_state.step = 1

# --- DESIGN SYSTEM (CSS - NOWOCZESNY DARK MODE) ---
st.markdown("""
    <style>
    /* 1. GŁÓWNE TŁO APLIKACJI */
    .stApp {
        background-color: #0f1116; /* Bardzo ciemny granat/czern */
        color: #e2e8f0;
    }

    /* 2. PANEL BOCZNY (SIDEBAR) - GRADIENT */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e3a8a 100%);
        border-right: 1px solid #334155;
    }
    
    /* 3. UKRYWANIE SYSTEMOWYCH ETYKIET */
    div[data-testid="stWidgetLabel"] { display: none; }

    /* 4. POLA TEKSTOWE (INPUTS) */
    .stTextInput input, .stTextArea textarea {
        background-color: #1e293b !important; /* Ciemnoszare tło */
        color: #f8fafc !important; /* Biały tekst */
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #6366f1 !important; /* Fioletowe podświetlenie */
        box-shadow: 0 0 0 1px #6366f1 !important;
    }
    
    /* 5. PRZYCISKI (BUTTONS) - GRADIENT I GLOW */
    .stButton > button {
        background: linear-gradient(90deg, #4f46e5, #7c3aed); /* Fioletowo-niebieski gradient */
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .stButton > button:hover {
        opacity: 0.9;
        box-shadow: 0 0 15px rgba(124, 58, 237, 0.5); /* Świecenie po najechaniu */
        transform: translateY(-1px);
    }
    /* Przycisk Wstecz - inny styl (bardziej stonowany) */
    div.row-widget.stButton > button[kind="secondary"] {
        background: transparent;
        border: 1px solid #475569;
    }

    /* 6. PASEK POSTĘPU */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #ef4444, #a855f7); /* Czerwono-fioletowy jak na screenie */
    }

    /* 7. WŁASNE ETYKIETY Z IKONKAMI */
    .custom-label {
        margin-top: 15px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        font-family: 'Inter', sans-serif;
    }
    .label-text {
        font-size: 14px;
        font-weight: 500;
        color: #94a3b8; /* Jasnoszary tekst etykiet */
        margin-right: 8px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .info-icon {
        background-color: #3b82f6;
        color: white;
        border-radius: 50%;
        width: 16px;
        height: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        font-weight: bold;
        cursor: help;
        position: relative;
    }
    .info-icon:hover::after {
        content: attr(data-tooltip);
        position: absolute;
        left: 24px;
        bottom: -5px;
        background: #0f172a;
        color: #e2e8f0;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        width: 250px;
        z-index: 1000;
        border: 1px solid #334155;
        line-height: 1.4;
    }
    
    /* 8. NAGŁÓWKI */
    h1, h2, h3 {
        color: #f8fafc !important;
        font-family: 'Inter', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCJE POMOCNICZE ---
def render_label(text, tooltip):
    st.markdown(f"""
        <div class="custom-label">
            <span class="label-text">{text}</span>
            <div class="info-icon" data-tooltip="{tooltip}">i</div>
        </div>
    """, unsafe_allow_html=True)

def extract_pure_html(text):
    text = re.sub(r'```html', '', text, flags=re.IGNORECASE)
    text = re.sub(r'```', '', text)
    start = text.find('<')
    end = text.rfind('>')
    if start != -1 and end != -1:
        return text[start:end+1].strip()
    return text.strip()

# --- SŁOWNIK POMOCY ---
INFO = {
    "diag": "Kod ICD-10/DSM-5.",
    "ryz": "Myśli S., plany, czynniki chroniące.",
    "prob": "Główne objawy i problemy.",
    "mysl": "Cytaty myśli automatycznych.",
    "syt": "Kto? Gdzie? Kiedy?",
    "auto": "Co pomyślał w tej chwili?",
    "emo": "Uczucia i reakcje ciała.",
    "zach": "Co zrobił / Czego uniknął?",
    "koszt": "Skutek: Krótka ulga vs Długi koszt.",
    "hipo": "Mechanizmy podtrzymujące."
}

# --- PANEL BOCZNY ---
with st.sidebar:
    st.markdown("### 🛡️ Panel Sterowania")
    api_key = st.text_input("Klucz Gemini API", type="password")
    
    st.write("") # Odstęp
    st.markdown(f"**Postęp:** Krok {st.session_state.step} z 5")
    st.progress(st.session_state.step / 5)
    
    st.write("") # Odstęp
    if st.button("🗑️ Resetuj sesję"):
        st.session_state.clear()
        st.rerun()

# --- LOGIKA KROKÓW ---

# KROK 1
if st.session_state.step == 1:
    st.markdown("### 🔵 Krok 1: Dane podstawowe")
    
    col1, col2 = st.columns(2)
    with col1:
        render_label("ID Pacjenta", "Unikalny numer.")
        st.text_input("lbl", key="id_p", label_visibility="collapsed")
        
        render_label("Diagnoza", INFO["diag"])
        st.text_input("lbl", key="diagnoza", label_visibility="collapsed")
        
    with col2:
        render_label("Terapeuta", "Imię i nazwisko.")
        st.text_input("lbl", key="terapeuta", label_visibility="collapsed")
    
    render_label("Ryzyko / Bezpieczeństwo", INFO["ryz"])
    st.text_area("lbl", key="ryzyko", label_visibility="collapsed")
    
    if st.button("Dalej ➡️"): st.session_state.step = 2; st.rerun()

# KROK 2
elif st.session_state.step == 2:
    st.markdown("### 🟣 Krok 2: Objawy")
    
    render_label("Objawy i problemy", INFO["prob"])
    st.text_area("lbl", key="problemy", label_visibility="collapsed")
    
    render_label("Myśli automatyczne", INFO["mysl"])
    st.text_area("lbl", key="mysli_raw", label_visibility="collapsed")
    
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 1; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 3; st.rerun()

# KROK 3
elif st.session_state.step == 3:
    st.markdown("### 🟣 Krok 3: Pętla CBT")
    
    render_label("Sytuacja", INFO["syt"])
    st.text_area("lbl", key="p_sit", label_visibility="collapsed")
    
    render_label("Myśl Automatyczna", INFO["auto"])
    st.text_area("lbl", key="p_mysl", label_visibility="collapsed")
    
    render_label("Emocja", INFO["emo"])
    st.text_area("lbl", key="p_emocja", label_visibility="collapsed")
    
    render_label("Zachowanie", INFO["zach"])
    st.text_area("lbl", key="p_zach", label_visibility="collapsed")
    
    render_label("Konsekwencja", INFO["koszt"])
    st.text_area("lbl", key="p_koszt", label_visibility="collapsed")
    
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 2; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 4; st.rerun()

# KROK 4
elif st.session_state.step == 4:
    st.markdown("### 🔵 Krok 4: Kontekst")
    
    render_label("Relacja Terapeutyczna", "Opis współpracy.")
    st.text_area("lbl", key="relacja", label_visibility="collapsed")
    
    render_label("Historia / Rodzina", "Tło historyczne.")
    st.text_area("lbl", key="historia", label_visibility="collapsed")
    
    render_label("Hipotezy kliniczne", INFO["hipo"])
    st.text_area("lbl", key="hipotezy", label_visibility="collapsed")
    
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 3; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 5; st.rerun()

# KROK 5
elif st.session_state.step == 5:
    st.markdown("### 🚀 Krok 5: Generowanie")
    
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
                Pętla: {st.session_state.p_sit} -> {st.session_state.p_mysl} -> {st.session_state.p_emocja} -> {st.session_state.p_zach} -> {st.session_state.p_koszt}
                """
                
                with st.spinner('Przetwarzanie danych klinicznych...'):
                    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                    st.session_state.final_report = extract_pure_html(response.text)
                    
            except Exception as e: st.error(f"Błąd: {e}")

    # --- PODGLĄD DOKUMENTU W STYLU "DARK MODE" ---
    if st.session_state.final_report:
        st.write("---")
        st.markdown("### 📄 Podgląd dokumentu:")
        
        # Stylizacja HTML dla podglądu (żeby pasował do ciemnego motywu aplikacji)
        dark_preview_css = """
        <style>
            body { background-color: #1e293b; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; padding: 20px; }
            h2 { color: #a5b4fc; border-bottom: 1px solid #475569; padding-bottom: 5px; margin-top: 25px; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; background-color: #0f172a; }
            th, td { border: 1px solid #334155; padding: 10px; text-align: left; vertical-align: top; }
            th { background-color: #1e3a8a; color: white; }
            strong { color: #818cf8; }
        </style>
        """
        
        # Łączymy style ciemne z treścią raportu TYLKO dla podglądu
        preview_html = f"{dark_preview_css}{st.session_state.final_report}"
        
        # Wyświetlamy podgląd
        components.html(preview_html, height=800, scrolling=True)
        
        # --- DO POBRANIA: CZYSTY BIAŁY RAPORT (DO DRUKU) ---
        clean_print_css = """
        <style>
            body { font-family: 'Times New Roman', serif; padding: 40px; color: black; line-height: 1.6; }
            h2 { color: #003366; border-bottom: 1px solid #ccc; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid black; padding: 8px; }
            th { background-color: #f0f0f0; }
        </style>
        """
        full_html_download = f"<html><head>{clean_print_css}</head><body>{st.session_state.final_report}</body></html>"
            
        st.download_button("💾 Pobierz Raport (HTML)", full_html_download, file_name=f"raport_{st.session_state.id_p}.html")
