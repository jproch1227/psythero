import streamlit as st
import streamlit.components.v1 as components  # <--- NOWY IMPORT DO WYŚWIETLANIA HTML
from google import genai
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

# --- CSS (WYGLĄD APLIKACJI) ---
st.markdown("""
    <style>
    /* Ukrywanie etykiet systemowych */
    div[data-testid="stWidgetLabel"] { display: none; }
    [data-testid="stSidebar"] { background-color: #1a365d; color: white; }

    /* Etykiety z ikonkami */
    .custom-label { margin-top: 15px; margin-bottom: 5px; display: flex; align-items: center; }
    .label-text { font-size: 14px; font-weight: 600; color: #f0f2f6; margin-right: 8px; }
    .info-icon {
        background-color: #2b6cb0; color: white; border-radius: 50%; width: 18px; height: 18px;
        display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; cursor: help;
        position: relative;
    }
    
    /* Tooltip */
    .info-icon:hover::after {
        content: attr(data-tooltip);
        position: absolute; left: 25px; background: #2d3748; color: #fff; padding: 8px;
        border-radius: 4px; font-size: 12px; width: 260px; z-index: 1000; font-weight: normal; line-height: 1.4;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    .stTextArea textarea { border: 1px solid #4a5568 !important; height: 130px !important; }
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
    """Czyści odpowiedź AI."""
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
    
    render_label("ID Pacjenta", "Unikalny numer.")
    st.text_input("lbl", key="id_p")
    
    render_label("Terapeuta", "Imię i nazwisko.")
    st.text_input("lbl", key="terapeuta")
    
    render_label("Diagnoza", INFO["diag"])
    st.text_input("lbl", key="diagnoza")
    
    render_label("Ryzyko / Bezpieczeństwo", INFO["ryz"])
    st.text_area("lbl", key="ryzyko")
    
    if st.button("Dalej ➡️"): st.session_state.step = 2; st.rerun()

# KROK 2
elif st.session_state.step == 2:
    st.subheader("🟣 Krok 2: Objawy")
    render_label("Objawy i problemy", INFO["prob"])
    st.text_area("lbl", key="problemy")
    
    render_label("Myśli automatyczne", INFO["mysl"])
    st.text_area("lbl", key="mysli_raw")
    
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 1; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 3; st.rerun()

# KROK 3
elif st.session_state.step == 3:
    st.subheader("🟣 Krok 3: Pętla CBT")
    
    render_label("Sytuacja", INFO["syt"])
    st.text_area("lbl", key="p_sit")
    
    render_label("Myśl Automatyczna", INFO["auto"])
    st.text_area("lbl", key="p_mysl")
    
    render_label("Emocja", INFO["emo"])
    st.text_area("lbl", key="p_emocja")
    
    render_label("Zachowanie", INFO["zach"])
    st.text_area("lbl", key="p_zach")
    
    render_label("Konsekwencja", INFO["koszt"])
    st.text_area("lbl", key="p_koszt")
    
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 2; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 4; st.rerun()

# KROK 4
elif st.session_state.step == 4:
    st.subheader("🔵 Krok 4: Kontekst")
    
    render_label("Relacja Terapeutyczna", "Opis współpracy.")
    st.text_area("lbl", key="relacja")
    
    render_label("Historia / Rodzina", "Tło historyczne.")
    st.text_area("lbl", key="historia")
    
    render_label("Hipotezy kliniczne", INFO["hipo"])
    st.text_area("lbl", key="hipotezy")
    
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
                Pętla: {st.session_state.p_sit} -> {st.session_state.p_mysl} -> {st.session_state.p_emocja} -> {st.session_state.p_zach} -> {st.session_state.p_koszt}
                """
                
                with st.spinner('Generowanie...'):
                    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                    st.session_state.final_report = extract_pure_html(response.text)
                    
            except Exception as e: st.error(f"Błąd: {e}")

    # --- TUTAJ JEST ZMIANA: UŻYWAMY KOMPONENTU HTML ZAMIAST MARKDOWN ---
    if st.session_state.final_report:
        st.write("---")
        st.subheader("📄 Podgląd dokumentu:")
        
        # Wstrzykujemy style CSS bezpośrednio do HTML-a dla podglądu
        preview_html = f"""
        <style>
            body {{ font-family: 'Times New Roman', serif; padding: 20px; }}
            h2 {{ color: #1a365d; border-bottom: 1px solid #ccc; margin-top: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ border: 1px solid black; padding: 8px; text-align: left; vertical-align: top; }}
            th {{ background-color: #f2f2f2; }}
        </style>
        {st.session_state.final_report}
        """
        
        # Wyświetlamy jako prawdziwą stronę HTML (iframe)
        components.html(preview_html, height=800, scrolling=True)
        
        # Przycisk pobierania (czysty HTML bez styli podglądu, bo przeglądarka je doda)
        full_html_download = f"""<html><body>
            <style>body {{ font-family: sans-serif; max-width: 800px; margin: auto; padding: 20px; }} 
            table {{ width: 100%; border-collapse: collapse; }} 
            td, th {{ border: 1px solid black; padding: 8px; }}</style>
            {st.session_state.final_report}
            </body></html>"""
            
        st.download_button("💾 Pobierz Raport (HTML)", full_html_download, file_name="raport.html")
