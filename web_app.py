import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types # Import typów do konfiguracji temperatury
import re

# --- KONFIGURACJA ---
st.set_page_config(page_title="CBT Clinical Pro", layout="wide", initial_sidebar_state="expanded")

# --- INICJALIZACJA STANU ---
keys = ['id_p', 'terapeuta', 'diagnoza', 'ryzyko', 'problemy', 'mysli_raw', 
        'p_sit', 'p_mysl', 'p_emocja', 'p_zach', 'p_koszt', 'relacja', 'historia', 'hipotezy', 'final_report', 'patient_homework']

for key in keys:
    if key not in st.session_state:
        st.session_state[key] = ""

if 'step' not in st.session_state:
    st.session_state.step = 1

# --- CSS (Design System) ---
st.markdown("""
    <style>
    /* Ogólne */
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
        transition: all 0.3s ease;
    }
    .stButton > button:hover { opacity: 0.9; box-shadow: 0 0 15px rgba(124, 58, 237, 0.5); transform: translateY(-1px); }
    
    /* Etykiety */
    .custom-label { margin-top: 15px; margin-bottom: 8px; display: flex; align-items: center; }
    .label-text { font-size: 14px; font-weight: 500; color: #94a3b8; margin-right: 8px; text-transform: uppercase; letter-spacing: 0.05em; }
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
    
    # UKŁAD WERTYKALNY (Jeden pod drugim)
    
    render_label("ID Pacjenta", "Unikalny numer.")
    st.session_state.id_p = st.text_input("lbl", value=st.session_state.id_p, key="widget_id_p", label_visibility="collapsed")
    
    render_label("Terapeuta", "Imię i nazwisko.")
    st.session_state.terapeuta = st.text_input("lbl", value=st.session_state.terapeuta, key="widget_terapeuta", label_visibility="collapsed")
    
    render_label("Diagnoza", INFO["diag"])
    st.session_state.diagnoza = st.text_input("lbl", value=st.session_state.diagnoza, key="widget_diag", label_visibility="collapsed")
    
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
    
    # --- SEKCJA 1: RAPORT KLINICZNY ---
    st.subheader("1. Dokumentacja Kliniczna (Dla Specjalisty)")
    
    if st.button("GENERUJ RAPORT SUPERWIZYJNY", key="btn_clinical"):
        if not api_key: st.error("Podaj klucz API!")
        else:
            try:
                client = genai.Client(api_key=api_key)
                prompt_clinical = f"""
                Jesteś superwizorem CBT. Wygeneruj raport w CZYSTYM HTML. Bez markdown. Bez instrukcji.
                
                DANE:
                ID: {st.session_state.id_p}, Diagnoza: {st.session_state.diagnoza}, Ryzyko: {st.session_state.ryzyko}
                Historia: {st.session_state.historia}, Problemy: {st.session_state.problemy}
                PĘTLA: Syt: {st.session_state.p_sit}, Myśl: {st.session_state.p_mysl}, Emo: {st.session_state.p_emocja}, Zach: {st.session_state.p_zach}, Koszt: {st.session_state.p_koszt}
                
                STRUKTURA HTML:
                <h2>1. Dane Kliniczne</h2>
                <h2>2. Konceptualizacja 5P (Tabela HTML)</h2>
                <h2>3. Analiza Funkcjonalna (Tabela Pętli Becka)</h2>
                <h2>4. Triada i Zniekształcenia</h2>
                <h2>5. Tabela Padesky'ego (Restrukturyzacja)</h2>
                <h2>6. Plan Bezpieczeństwa</h2>
                <h2>7. Cele SMART</h2>
                """
                
                with st.spinner('Tworzenie dokumentacji medycznej...'):
                    config = types.GenerateContentConfig(temperature=0.0)
                    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt_clinical, config=config)
                    st.session_state.final_report = extract_pure_html(response.text)
            except Exception as e: st.error(f"Błąd: {e}")

    # Wyświetlanie Raportu Klinicznego
    if st.session_state.final_report:
        with st.expander("📄 Podgląd Raportu Klinicznego", expanded=True):
            dark_css = """<style>
                body { background-color: #1e293b; color: #e2e8f0; font-family: sans-serif; padding: 20px; }
                h1, h2, h3 { color: #ffffff !important; border-bottom: 1px solid #475569; margin-top: 30px; }
                table { width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #f8fafc; }
                th, td { border: 1px solid #cbd5e1; padding: 12px; color: #0f172a !important; }
                th { background-color: #e2e8f0; font-weight: bold; }
            </style>"""
            components.html(dark_css + st.session_state.final_report, height=600, scrolling=True)
            
            # Pobieranie Raportu
            print_css = """<style>body{font-family:'Times New Roman',serif;padding:40px;color:black}table{width:100%;border-collapse:collapse}th,td{border:1px solid black;padding:8px}th{background:#f0f0f0}</style>"""
            st.download_button("💾 Pobierz Raport Kliniczny (HTML)", f"<html><head>{print_css}</head><body>{st.session_state.final_report}</body></html>", file_name=f"raport_{st.session_state.id_p}.html")

    st.markdown("---")
    
    # --- SEKCJA 2: MATERIAŁY DLA PACJENTA (NOWOŚĆ) ---
    st.subheader("2. Materiały dla Pacjenta (Zadanie Domowe)")
    
    if st.button("GENERUJ KARTĘ PRACY DLA PACJENTA", key="btn_patient"):
        if not api_key: st.error("Podaj klucz API!")
        elif not st.session_state.final_report: st.warning("Najpierw wygeneruj raport kliniczny, aby AI miało kontekst!")
        else:
            try:
                client = genai.Client(api_key=api_key)
                prompt_patient = f"""
                Jesteś empatycznym terapeutą CBT. Stwórz "Kartę Pracy" dla pacjenta w formacie CZYSTEGO HTML.
                Używaj języka prostego, motywującego i zrozumiałego dla osoby w kryzysie. Żadnego żargonu lekarskiego.
                
                DANE:
                Diagnoza: {st.session_state.diagnoza}
                Sytuacja trudna: {st.session_state.p_sit}
                Myśl automatyczna: {st.session_state.p_mysl}
                
                STRUKTURA DOKUMENTU DLA PACJENTA:
                <div class="header" style="text-align:center; padding:20px; background:#e0f2fe; border-radius:10px;">
                    <h1 style="color:#0369a1; margin:0;">Moja Karta Pracy CBT</h1>
                    <p style="color:#0c4a6e;">Materiały wspierające do sesji</p>
                </div>
                
                <h2>1. Co się dzisiaj działo? (Psychoedukacja)</h2>
                (Wyjaśnij pacjentowi w 3 zdaniach, jak jego myśl "{st.session_state.p_mysl}" wpłynęła na to, że poczuł "{st.session_state.p_emocja}". Użyj metafory "okularów przez które patrzymy na świat".)
                
                <h2>2. Twoje Zadanie na ten tydzień</h2>
                (Zaproponuj 1 konkretne, małe zadanie behawioralne oparte na przełamaniu unikania. Np. "Spróbuj raz dziennie...". Ma to być eksperyment.)
                
                <h2>3. Karta Przypominajka (Do wycięcia)</h2>
                (Stwórz ramkę z krótkim tekstem, który pacjent może przeczytać w trudnej chwili. Np. "Pamiętaj, że myśl to nie fakt..." + myśl alternatywna).
                """
                
                with st.spinner('Przygotowywanie materiałów edukacyjnych...'):
                    config = types.GenerateContentConfig(temperature=0.7)
                    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt_patient, config=config)
                    st.session_state.patient_homework = extract_pure_html(response.text)
            except Exception as e: st.error(f"Błąd: {e}")

    # Wyświetlanie Karty Pacjenta
    if st.session_state.patient_homework:
        with st.expander("🎓 Podgląd Karty Pacjenta", expanded=True):
            patient_css = """<style>
                body { background-color: #ffffff; color: #334155; font-family: 'Segoe UI', sans-serif; padding: 20px; }
                h1, h2 { color: #0284c7; border-bottom: 2px solid #e0f2fe; padding-bottom: 10px; margin-top: 20px; }
                p { font-size: 16px; line-height: 1.6; }
                .card { border: 2px dashed #94a3b8; padding: 20px; margin: 20px 0; background-color: #f8fafc; text-align: center; font-style: italic; }
            </style>"""
            components.html(patient_css + st.session_state.patient_homework, height=600, scrolling=True)
            
            st.download_button("💾 Pobierz Zadanie Domowe (HTML)", f"<html><head>{patient_css}</head><body>{st.session_state.patient_homework}</body></html>", file_name=f"zadanie_domowe_{st.session_state.id_p}.html")
