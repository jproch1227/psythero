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

# --- CSS (Design System Aplikacji) ---
st.markdown("""
    <style>
    .stApp { background-color: #0f1116; color: #e2e8f0; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e3a8a 100%); border-right: 1px solid #334155; }
    div[data-testid="stWidgetLabel"] { display: none; }

    /* Pola tekstowe */
    .stTextInput input, .stTextArea textarea {
        background-color: #1e293b !important; color: #f8fafc !important;
        border: 1px solid #334155 !important; border-radius: 8px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus { border-color: #6366f1 !important; box-shadow: 0 0 0 1px #6366f1 !important; }
    
    /* Przyciski */
    .stButton > button {
        background: linear-gradient(90deg, #4f46e5, #7c3aed); color: white; border: none;
        border-radius: 8px; padding: 10px 24px; font-weight: 600;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stButton > button:hover { opacity: 0.9; box-shadow: 0 0 15px rgba(124, 58, 237, 0.5); }
    
    /* Etykiety */
    .custom-label { margin-top: 15px; margin-bottom: 8px; display: flex; align-items: center; }
    .label-text { font-size: 14px; font-weight: 500; color: #94a3b8; margin-right: 8px; text-transform: uppercase; }
    .info-icon {
        background-color: #3b82f6; color: white; border-radius: 50%; width: 16px; height: 16px;
        display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; cursor: help;
    }
    .info-icon:hover::after {
        content: attr(data-tooltip); position: absolute; left: 24px; bottom: -5px;
        background: #0f172a; color: #e2e8f0; padding: 8px 12px; border-radius: 6px;
        font-size: 12px; width: 250px; z-index: 1000; border: 1px solid #334155;
    }
    h1, h2, h3 { color: #f8fafc !important; }
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
    st.write("")
    st.markdown(f"**Postęp:** Krok {st.session_state.step} z 5")
    st.progress(st.session_state.step / 5)
    st.write("")
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
        st.session_state.id_p = st.text_input("lbl", value=st.session_state.id_p, key="widget_id_p", label_visibility="collapsed")
        
        render_label("Diagnoza", INFO["diag"])
        st.session_state.diagnoza = st.text_input("lbl", value=st.session_state.diagnoza, key="widget_diag", label_visibility="collapsed")
    with col2:
        render_label("Terapeuta", "Imię i nazwisko.")
        st.session_state.terapeuta = st.text_input("lbl", value=st.session_state.terapeuta, key="widget_terapeuta", label_visibility="collapsed")
    
    render_label("Ryzyko / Bezpieczeństwo", INFO["ryz"])
    st.session_state.ryzyko = st.text_area("lbl", value=st.session_state.ryzyko, key="widget_ryzyko", label_visibility="collapsed")
    
    if st.button("Dalej ➡️"): st.session_state.step = 2; st.rerun()

# KROK 2
elif st.session_state.step == 2:
    st.markdown("### 🟣 Krok 2: Objawy")
    render_label("Objawy i problemy", INFO["prob"])
    st.session_state.problemy = st.text_area("lbl", value=st.session_state.problemy, key="widget_problemy", label_visibility="collapsed")
    render_label("Myśli automatyczne", INFO["mysl"])
    st.session_state.mysli_raw = st.text_area("lbl", value=st.session_state.mysli_raw, key="widget_mysli", label_visibility="collapsed")
    
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 1; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 3; st.rerun()

# KROK 3
elif st.session_state.step == 3:
    st.markdown("### 🟣 Krok 3: Pętla CBT")
    
    

    render_label("Sytuacja", INFO["syt"])
    st.session_state.p_sit = st.text_area("lbl", value=st.session_state.p_sit, key="widget_sit", label_visibility="collapsed")
    
    render_label("Myśl Automatyczna", INFO["auto"])
    st.session_state.p_mysl = st.text_area("lbl", value=st.session_state.p_mysl, key="widget_pmysl", label_visibility="collapsed")
    
    render_label("Emocja", INFO["emo"])
    st.session_state.p_emocja = st.text_area("lbl", value=st.session_state.p_emocja, key="widget_emo", label_visibility="collapsed")
    
    render_label("Zachowanie", INFO["zach"])
    st.session_state.p_zach = st.text_area("lbl", value=st.session_state.p_zach, key="widget_zach", label_visibility="collapsed")
    
    render_label("Konsekwencja", INFO["koszt"])
    st.session_state.p_koszt = st.text_area("lbl", value=st.session_state.p_koszt, key="widget_koszt", label_visibility="collapsed")
    
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 2; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 4; st.rerun()

# KROK 4
elif st.session_state.step == 4:
    st.markdown("### 🔵 Krok 4: Kontekst")
    render_label("Relacja Terapeutyczna", "Opis współpracy.")
    st.session_state.relacja = st.text_area("lbl", value=st.session_state.relacja, key="widget_relacja", label_visibility="collapsed")
    render_label("Historia / Rodzina", "Tło historyczne.")
    st.session_state.historia = st.text_area("lbl", value=st.session_state.historia, key="widget_historia", label_visibility="collapsed")
    render_label("Hipotezy kliniczne", INFO["hipo"])
    st.session_state.hipotezy = st.text_area("lbl", value=st.session_state.hipotezy, key="widget_hipotezy", label_visibility="collapsed")
    
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

    # --- PODGLĄD DOKUMENTU ---
    if st.session_state.final_report:
        st.write("---")
        st.markdown("### 📄 Podgląd dokumentu:")
        
        # ZMODYFIKOWANY CSS PODGLĄDU ZGODNIE Z PROŚBĄ
        dark_preview_css = """
        <style>
            body { 
                background-color: #1e293b; 
                color: #e2e8f0; 
                font-family: 'Segoe UI', sans-serif; 
                padding: 20px; 
            }
            
            /* NAGŁÓWKI NA BIAŁO */
            h1, h2, h3, h4 { 
                color: #ffffff !important; 
                border-bottom: 1px solid #475569; 
                padding-bottom: 5px; 
                margin-top: 25px; 
            }
            
            /* TABELA - JASNE TŁO, CZARNY TEKST */
            table { 
                width: 100%; 
                border-collapse: collapse; 
                margin-top: 10px; 
                background-color: #f1f5f9; /* Bardzo jasny szary (prawie biały) */
            }
            
            th, td { 
                border: 1px solid #334155; 
                padding: 10px; 
                text-align: left; 
                vertical-align: top; 
                color: #000000 !important; /* CZARNY TEKST */
            }
            
            th { 
                background-color: #cbd5e1; /* Szary nagłówek tabeli */
                font-weight: bold;
            }
            
            strong { color: #818cf8; }
        </style>
        """
        
        # Renderowanie podglądu
        components.html(dark_preview_css + st.session_state.final_report, height=800, scrolling=True)
        
        # Do pobrania (Klasyczny biały do druku)
        clean_print_css = """
        <style>
            body { font-family: 'Times New Roman', serif; padding: 40px; color: black; line-height: 1.6; }
            h2 { color: #000000; border-bottom: 1px solid #ccc; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid black; padding: 8px; color: black; }
            th { background-color: #f0f0f0; }
        </style>
        """
        full_html_download = f"<html><head>{clean_print_css}</head><body>{st.session_state.final_report}</body></html>"
            
        st.download_button("💾 Pobierz Raport (HTML)", full_html_download, file_name=f"raport_{st.session_state.id_p}.html")
