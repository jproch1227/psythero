import streamlit as st
from google import genai
import re

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="CBT Clinical Pro", layout="wide")

# --- 1. FUNKCJA CZYSZCZĄCA (NUCLEAR OPTION) ---
def clean_gemini_output(text):
    """
    Ta funkcja naprawia błąd wyświetlania kodu.
    Działa siłowo: znajduje pierwszy znak '<' i ostatni '>',
    a wszystko inne wyrzuca do kosza.
    """
    # Usuwamy znaczniki markdown, jeśli AI je dodało
    text = text.replace("```html", "").replace("```", "")
    
    # Znajdujemy początek i koniec prawdziwego HTML-a
    start_index = text.find("<")
    end_index = text.rfind(">")
    
    # Jeśli znaleziono tagi, wytnij tylko to, co jest w środku
    if start_index != -1 and end_index != -1:
        return text[start_index : end_index + 1]
    
    # Jeśli AI zwróciło sam tekst bez tagów (mało prawdopodobne), opakuj to w div
    return f"<div>{text}</div>"

# --- 2. INICJALIZACJA ZMIENNYCH (Żeby nie było błędów) ---
# Lista wszystkich pól formularza
keys = ['id_p', 'terapeuta', 'diagnoza', 'ryzyko', 'problemy', 'mysli_raw', 
        'p_sit', 'p_mysl', 'p_emocja', 'p_zach', 'p_koszt', 'relacja', 'historia', 'hipotezy', 'final_report']

for key in keys:
    if key not in st.session_state:
        st.session_state[key] = ""
if 'step' not in st.session_state:
    st.session_state.step = 1

# --- 3. STYLE CSS (WYGLĄD) ---
st.markdown("""
    <style>
    /* Ukryj systemowe etykiety Streamlit */
    div[data-testid="stWidgetLabel"] { display: none; }
    
    /* Kolory panelu */
    [data-testid="stSidebar"] { background-color: #1a365d; color: white; }

    /* Własne etykiety z dymkami */
    .custom-label { 
        margin-top: 15px; margin-bottom: 5px; 
        display: flex; align-items: center; 
    }
    .label-text { 
        font-size: 14px; font-weight: 600; 
        color: #f0f2f6; margin-right: 8px; 
    }
    .info-icon {
        background-color: #2b6cb0; color: white; 
        border-radius: 50%; width: 18px; height: 18px;
        display: flex; align-items: center; justify-content: center; 
        font-size: 12px; font-weight: bold; cursor: help;
    }
    
    /* Prosty, systemowy dymek po najechaniu (niezawodny) */
    .info-icon:hover::after {
        content: attr(data-tooltip);
        position: absolute; left: 25px; 
        background: #2d3748; color: #fff; padding: 8px;
        border-radius: 4px; font-size: 12px; width: 280px; 
        z-index: 1000; font-weight: normal; line-height: 1.4;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

    /* Wygląd Raportu (Dokument) */
    .report-card {
        background-color: white; padding: 15mm; color: black;
        font-family: 'Times New Roman', serif; border: 1px solid #ccc; 
        margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .report-card h2 { 
        color: #1a365d; border-bottom: 1px solid #ddd; 
        margin-top: 25px; font-size: 20px; 
    }
    .report-card table { 
        width: 100%; border-collapse: collapse; margin: 15px 0; 
    }
    .report-card th, .report-card td { 
        border: 1px solid black !important; padding: 8px; 
        text-align: left; vertical-align: top; font-size: 14px; 
    }
    .report-card th { background-color: #f2f2f2; font-weight: bold; }
    
    .stTextArea textarea { border: 1px solid #4a5568 !important; height: 130px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKCJA RENDERUJĄCA ETYKIETY ---
def render_label(text, tooltip):
    st.markdown(f"""
        <div class="custom-label">
            <span class="label-text">{text}</span>
            <div class="info-icon" data-tooltip="{tooltip}">i</div>
        </div>
    """, unsafe_allow_html=True)

# --- 5. TREŚCI TOOLTIPÓW ---
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

# --- 6. PANEL BOCZNY ---
with st.sidebar:
    st.title("🛡️ Panel")
    api_key = st.text_input("Klucz Gemini API", type="password")
    st.divider()
    st.progress(st.session_state.step / 5)
    if st.button("🗑️ Reset"):
        st.session_state.clear()
        st.rerun()

# --- 7. LOGIKA KROKÓW (FORMULARZ) ---

# KROK 1
if st.session_state.step == 1:
    st.subheader("🔵 Krok 1: Dane podstawowe")
    st.text_input("ID", key="id_inp", value=st.session_state.id_p)
    st.session_state.id_p = st.session_state.id_inp
    
    st.text_input("Terapeuta", key="ter_inp", value=st.session_state.terapeuta)
    st.session_state.terapeuta = st.session_state.ter_inp
    
    render_label("Diagnoza", INFO["diag"])
    st.session_state.diagnoza = st.text_input("d_inp", value=st.session_state.diagnoza)
    
    render_label("Ryzyko / Bezpieczeństwo", INFO["ryz"])
    st.session_state.ryzyko = st.text_area("r_inp", value=st.session_state.ryzyko)
    
    if st.button("Dalej ➡️"): st.session_state.step = 2; st.rerun()

# KROK 2
elif st.session_state.step == 2:
    st.subheader("🟣 Krok 2: Objawy")
    render_label("Problemy", INFO["prob"])
    st.session_state.problemy = st.text_area("p_inp", value=st.session_state.problemy)
    
    render_label("Myśli automatyczne", INFO["mysl"])
    st.session_state.mysli_raw = st.text_area("m_inp", value=st.session_state.mysli_raw)
    
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 1; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 3; st.rerun()

# KROK 3
elif st.session_state.step == 3:
    st.subheader("🟣 Krok 3: Pętla CBT")
    
    

    render_label("Sytuacja", INFO["syt"])
    st.session_state.p_sit = st.text_area("s_inp", value=st.session_state.p_sit)
    render_label("Myśl Automatyczna", INFO["auto"])
    st.session_state.p_mysl = st.text_area("my_inp", value=st.session_state.p_mysl)
    render_label("Emocja", INFO["emo"])
    st.session_state.p_emocja = st.text_area("e_inp", value=st.session_state.p_emocja)
    render_label("Zachowanie", INFO["zach"])
    st.session_state.p_zach = st.text_area("z_inp", value=st.session_state.p_zach)
    render_label("Konsekwencja (Koszt)", INFO["koszt"])
    st.session_state.p_koszt = st.text_area("k_inp", value=st.session_state.p_koszt)
    
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 2; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 4; st.rerun()

# KROK 4
elif st.session_state.step == 4:
    st.subheader("🔵 Krok 4: Kontekst")
    st.text_area("Relacja", key="rel_inp", value=st.session_state.relacja)
    st.session_state.relacja = st.session_state.rel_inp
    st.text_area("Historia", key="hist_inp", value=st.session_state.historia)
    st.session_state.historia = st.session_state.hist_inp
    render_label("Hipotezy", INFO["hipo"])
    st.session_state.hipotezy = st.text_area("h_inp", value=st.session_state.hipotezy)
    
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 3; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 5; st.rerun()

# KROK 5 (GENEROWANIE)
elif st.session_state.step == 5:
    st.subheader("🚀 Krok 5: Generowanie")
    if st.button("GENERUJ RAPORT"):
        if not api_key: st.error("Podaj klucz API!")
        else:
            try:
                client = genai.Client(api_key=api_key)
                
                # Prompt dla AI
                prompt = f"""
                Jesteś superwizorem CBT. Wygeneruj raport w formacie HTML.
                
                DANE:
                ID: {st.session_state.id_p}, Diagnoza: {st.session_state.diagnoza}
                Ryzyko: {st.session_state.ryzyko}
                Pętla: Sytuacja: {st.session_state.p_sit}, Myśl: {st.session_state.p_mysl}, 
                Emocja: {st.session_state.p_emocja}, Zachowanie: {st.session_state.p_zach}, 
                Konsekwencje: {st.session_state.p_koszt}
                
                STRUKTURA HTML:
                <div class="header">RAPORT SUPERWIZYJNY</div>
                <h2>1. Dane i Ryzyko</h2>
                <h2>2. Konceptualizacja (Tabela Pętli Becka)</h2> (5 kolumn: Sytuacja, Myśl, Emocja, Zachowanie, Konsekwencja)
                <h2>3. Triada i Zniekształcenia</h2>
                <h2>4. Tabela Padesky'ego</h2>
                <h2>5. Cele SMART</h2>
                """
                
                with st.spinner('Pisanie raportu...'):
                    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                    # TUTAJ UŻYWAMY FUNKCJI CZYSZCZĄCEJ
                    final_html = clean_gemini_output(response.text)
                    st.session_state.final_report = final_html
                    
            except Exception as e: st.error(f"Błąd: {e}")

    # Wyświetlanie (Renderowanie)
    if st.session_state.final_report:
        st.markdown(f"<div class='report-card'>{st.session_state.final_report}</div>", unsafe_allow_html=True)
        st.download_button("Pobierz Raport", st.session_state.final_report, file_name="raport.html")
