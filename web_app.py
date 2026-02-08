import streamlit as st
import streamlit.components.v1 as components
from google import genai
import re

# --- KONFIGURACJA ---
st.set_page_config(page_title="CBT Clinical Pro", layout="wide", initial_sidebar_state="expanded")

# --- INICJALIZACJA STANU (Trwałość danych) ---
keys = ['id_p', 'terapeuta', 'diagnoza', 'ryzyko', 'problemy', 'mysli_raw', 
        'p_sit', 'p_mysl', 'p_emocja', 'p_zach', 'p_koszt', 'relacja', 'historia', 'hipotezy', 'final_report']

for key in keys:
    if key not in st.session_state:
        st.session_state[key] = ""

if 'step' not in st.session_state:
    st.session_state.step = 1

# --- CSS (Design System - Dark Mode UI) ---
st.markdown("""
    <style>
    /* Ogólny wygląd aplikacji */
    .stApp { background-color: #0f1116; color: #e2e8f0; }
    
    /* Panel boczny */
    section[data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #0f172a 0%, #1e3a8a 100%); 
        border-right: 1px solid #334155; 
    }
    
    /* Ukrywanie systemowych etykiet */
    div[data-testid="stWidgetLabel"] { display: none; }

    /* Pola tekstowe (Inputy) */
    .stTextInput input, .stTextArea textarea {
        background-color: #1e293b !important; 
        color: #f8fafc !important;
        border: 1px solid #334155 !important; 
        border-radius: 8px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus { 
        border-color: #6366f1 !important; 
        box-shadow: 0 0 0 1px #6366f1 !important; 
    }
    
    /* Przyciski */
    .stButton > button {
        background: linear-gradient(90deg, #4f46e5, #7c3aed); 
        color: white; 
        border: none;
        border-radius: 8px; 
        padding: 10px 24px; 
        font-weight: 600;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .stButton > button:hover { 
        opacity: 0.9; 
        box-shadow: 0 0 15px rgba(124, 58, 237, 0.5); 
        transform: translateY(-1px);
    }
    
    /* Własne etykiety */
    .custom-label { 
        margin-top: 15px; 
        margin-bottom: 8px; 
        display: flex; 
        align-items: center; 
    }
    .label-text { 
        font-size: 14px; 
        font-weight: 500; 
        color: #94a3b8; 
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
    }
    
    /* Nagłówki Streamlit */
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
    """
    Brutalna funkcja czyszcząca. Usuwa Markdown i wszystko poza tagami HTML.
    """
    text = re.sub(r'```html', '', text, flags=re.IGNORECASE)
    text = re.sub(r'```', '', text)
    start = text.find('<')
    end = text.rfind('>')
    if start != -1 and end != -1:
        return text[start:end+1].strip()
    return text.strip()

# --- SŁOWNIK POMOCY ---
INFO = {
    "diag": "Kod ICD-10/DSM-5 (np. F42.1).",
    "ryz": "Myśli S., plany, czynniki chroniące.",
    "prob": "Główne objawy, czas trwania, wpływ na życie.",
    "mysl": "Dosłowne cytaty pacjenta ('Jestem beznadziejna').",
    "syt": "Kto? Gdzie? Kiedy? Co wyzwoliło reakcję?",
    "auto": "Co pomyślał w ułamku sekundy?",
    "emo": "Emocje (lęk, złość) i odczucia z ciała.",
    "zach": "Co zrobił lub czego uniknął?",
    "koszt": "Krótka ulga vs Długi koszt.",
    "hipo": "Dlaczego problem trwa? Jakie schematy działają?"
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
    st.markdown("### 🚀 Krok 5: Generowanie (Wersja Rozszerzona)")
    
    if st.button("GENERUJ RAPORT EKSPERCKI"):
        if not api_key: st.error("Podaj klucz API!")
        else:
            try:
                client = genai.Client(api_key=api_key)
                
                # --- ZAAWANSOWANY PROMPT (Zapobiega "leakage" i dodaje nowe sekcje) ---
                prompt = f"""
                Jesteś ekspertem i superwizorem CBT. Twoim zadaniem jest wygenerowanie kompletnego Raportu Klinicznego w formacie HTML.
                
                ZASADY KRYTYCZNE:
                1. Generuj WYŁĄCZNIE kod HTML (od tagu <h2>). Żadnych wstępów, żadnych markdownów ```.
                2. ZAKAZ UŻYWANIA INSTRUKCJI W NAWIASACH typu "(Należy uzupełnić...)" lub "(Tutaj wpisz...)".
                3. Wszystkie sekcje mają być wypełnione ANALIZĄ KLINICZNĄ na podstawie dostarczonych danych. Jeśli brakuje danych, stawiaj hipotezy oznaczone jako "Hipoteza:".
                4. Używaj profesjonalnego języka klinicznego.
                
                DANE PACJENTA:
                ID: {st.session_state.id_p}, Diagnoza: {st.session_state.diagnoza}
                Ryzyko: {st.session_state.ryzyko}
                Problemy: {st.session_state.problemy}
                Historia: {st.session_state.historia}
                
                PĘTLA KLINICZNA (TU I TERAZ):
                Sytuacja: {st.session_state.p_sit} -> Myśl: {st.session_state.p_mysl} -> Emocja: {st.session_state.p_emocja} -> Zachowanie: {st.session_state.p_zach} -> Konsekwencje: {st.session_state.p_koszt}
                
                WYMAGANA STRUKTURA RAPORTU HTML:
                
                <h2>1. Dane Kliniczne</h2>
                (Krótkie podsumowanie ID, Diagnozy i Oceny Ryzyka)
                
                <h2>2. Konceptualizacja 5P (Case Formulation)</h2>
                (Stwórz tabelę HTML z wierszami: 
                - Problem Aktualny (Presenting Problem)
                - Czynniki Predysponujące (Predisposing) - wyciągnij z Historii/Dzieciństwa
                - Czynniki Wyzwalające (Precipitating) - co nasiliło problem teraz?
                - Czynniki Podtrzymujące (Perpetuating) - np. unikanie, ruminacje
                - Czynniki Chroniące (Protective) - zasoby pacjenta)
                
                <h2>3. Analiza Funkcjonalna (Pętla Becka)</h2>
                (Tabela 5 kolumn: Sytuacja, Myśl, Emocja, Zachowanie, Konsekwencje. Wypełnij danymi z pętli.)
                
                <h2>4. Triada i Zniekształcenia Poznawcze</h2>
                (Wypunktuj zidentyfikowane zniekształcenia np. Katastrofizacja, Czytanie w myślach. 
                Opisz Triadę Becka: Ja, Świat, Przyszłość na podstawie myśli pacjenta.)
                
                <h2>5. Tabela Padesky'ego (Restrukturyzacja)</h2>
                (Tabela: Myśl Automatyczna | Dowody ZA | Dowody PRZECIW | Myśl Alternatywna. 
                SAMODZIELNIE wymyśl racjonalne dowody przeciw i zdrową myśl alternatywną pasującą do kontekstu.)
                
                <h2>6. Hierarchia Lęku / Ekspozycji</h2>
                (Zaproponuj listę 3-4 sytuacji w formie listy punktowanej, uszeregowanych od najmniejszego do największego lęku, które pacjent może ćwiczyć. Np. 1. Uśmiech, 2. Pytanie, 3. Wystąpienie.)
                
                <h2>7. Plan Bezpieczeństwa (Crisis Plan)</h2>
                (Tabela: Sygnały Ostrzegawcze | Strategie Własne | Wsparcie Społeczne | Profesjonalna Pomoc. Wypełnij na podstawie pola Ryzyko. Jeśli ryzyko niskie, skup się na zapobieganiu nawrotom.)
                
                <h2>8. Cele Terapeutyczne (SMART)</h2>
                (Zaproponuj 2 konkretne cele w formacie listy.)
                """
                
                with st.spinner('Analiza kliniczna i generowanie raportu...'):
                    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                    st.session_state.final_report = extract_pure_html(response.text)
                    
            except Exception as e: st.error(f"Błąd: {e}")

    # --- PODGLĄD DOKUMENTU ---
    if st.session_state.final_report:
        st.write("---")
        st.markdown("### 📄 Podgląd dokumentu:")
        
        # CSS DLA PODGLĄDU (ZGODNIE Z PROŚBĄ: Białe nagłówki, czarne teksty w tabelach)
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
                margin-top: 30px; 
            }
            
            /* TABELA - JASNE TŁO, CZARNY TEKST DLA CZYTELNOŚCI */
            table { 
                width: 100%; 
                border-collapse: collapse; 
                margin-top: 15px; 
                background-color: #f8fafc; /* Prawie biały */
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                border-radius: 4px;
                overflow: hidden;
            }
            
            th, td { 
                border: 1px solid #cbd5e1; 
                padding: 12px; 
                text-align: left; 
                vertical-align: top; 
                color: #0f172a !important; /* GŁĘBOKA CZERŃ TEKSTU */
                font-size: 14px;
            }
            
            th { 
                background-color: #e2e8f0; /* Szary nagłówek */
                font-weight: 700;
                text-transform: uppercase;
                font-size: 12px;
                letter-spacing: 0.05em;
            }
            
            /* Listy w podglądzie */
            li { margin-bottom: 8px; color: #e2e8f0; }
            strong { color: #818cf8; }
        </style>
        """
        
        # Renderowanie podglądu (Iframe)
        components.html(dark_preview_css + st.session_state.final_report, height=1000, scrolling=True)
        
        # Do pobrania (Klasyczny biały do druku/PDF)
        clean_print_css = """
        <style>
            body { font-family: 'Times New Roman', serif; padding: 40px; color: black; line-height: 1.6; max-width: 900px; margin: auto; }
            h2 { color: #000000; border-bottom: 2px solid #333; padding-bottom: 10px; margin-top: 30px; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; page-break-inside: avoid; }
            th, td { border: 1px solid black; padding: 10px; color: black; }
            th { background-color: #f0f0f0; font-weight: bold; }
            ul { margin-top: 0; }
        </style>
        """
        full_html_download = f"<html><head>{clean_print_css}</head><body>{st.session_state.final_report}</body></html>"
            
        st.download_button("💾 Pobierz Raport (HTML)", full_html_download, file_name=f"raport_{st.session_state.id_p}.html")
