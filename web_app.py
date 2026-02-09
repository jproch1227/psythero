import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
import re

# --- KONFIGURACJA ---
st.set_page_config(page_title="CBT Clinical Architect", layout="wide", initial_sidebar_state="expanded")

# --- DANE SŁOWNIKOWE ---
ICD_10_LIST = [
    "F32 - Epizod depresyjny", "F33 - Zaburzenia depresyjne nawracające", "F31 - ChAD",
    "F41.1 - Lęk uogólniony (GAD)", "F40.1 - Fobia społeczna", "F41.0 - Lęk paniczny",
    "F42 - OCD", "F43.1 - PTSD", "F43.2 - Zaburzenia adaptacyjne",
    "F60.3 - Osobowość borderline", "F60.6 - Osobowość unikająca", "F90 - ADHD",
    "Inne / Nieokreślone"
]

FIZJOLOGIA_LIST = [
    "Bezsenność / Problemy ze snem", "Nadmierna senność", "Utrata apetytu", "Objadanie się",
    "Pobudzenie psychoruchowe", "Spowolnienie", "Zmęczenie / Brak energii",
    "Napięcie mięśniowe", "Bóle somatyczne", "Używki (Alkohol/Narkotyki)"
]

EMOCJE_LIST = [
    "Lęk / Niepokój", "Smutek / Przygnębienie", "Złość / Gniew", "Wstyd", "Poczucie winy",
    "Wstręt", "Obojętność / Pustka", "Bezradność", "Zazdrość"
]

# --- INICJALIZACJA STANU ---
keys = [
    'id_p', 'wiek', 'plec', 'terapeuta', 'diagnoza', 'leki', 'fizjologia', 'ryzyko_skala', 'ryzyko_opis',
    'problemy', 'wyzwalacze', 'zach_zabezp', 'coping', 
    'p_sit', 'p_mysl', 'p_emocje_tagi', 'p_zach', 'p_koszt',
    'historia', 'krytyczne', 'przekonania', 'zasady', 'zasoby', 'cele',
    'final_report', 'patient_homework', 'step'
]

for key in keys:
    if key not in st.session_state:
        if key in ['diagnoza', 'fizjologia', 'p_emocje_tagi']: st.session_state[key] = []
        elif key == 'ryzyko_skala': st.session_state[key] = 0
        elif key == 'step': st.session_state[key] = 1
        else: st.session_state[key] = ""

# --- CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0f1116; color: #e2e8f0; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e3a8a 100%); border-right: 1px solid #334155; }
    div[data-testid="stWidgetLabel"] { display: none; }
    
    .stTextInput input, .stTextArea textarea, .stSelectbox div, .stMultiSelect div {
        background-color: #1e293b !important; color: white !important;
        border: 1px solid #334155 !important; border-radius: 6px !important;
    }
    .stSlider div { color: #e2e8f0; }
    
    /* Etykiety */
    .custom-label { margin-top: 15px; margin-bottom: 5px; display: flex; align-items: center; }
    .label-text { font-size: 13px; font-weight: 600; color: #94a3b8; margin-right: 8px; text-transform: uppercase; letter-spacing: 0.05em; }
    .info-icon {
        background-color: #3b82f6; color: white; border-radius: 50%; width: 16px; height: 16px;
        display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; cursor: help;
    }
    .info-icon:hover::after {
        content: attr(data-tooltip); position: absolute; left: 24px; bottom: 0;
        background: #0f172a; color: #fff; padding: 8px; border-radius: 4px; font-size: 12px; width: 250px; z-index: 1000; border: 1px solid #334155;
    }
    h1, h2, h3 { color: #f8fafc !important; }
    </style>
""", unsafe_allow_html=True)

# --- FUNKCJE ---
def render_label(text, tooltip=""):
    st.markdown(f'<div class="custom-label"><span class="label-text">{text}</span>' + 
                (f'<div class="info-icon" data-tooltip="{tooltip}">i</div>' if tooltip else '') + 
                '</div>', unsafe_allow_html=True)

def extract_pure_html(text):
    text = re.sub(r'```html', '', text, flags=re.IGNORECASE)
    text = re.sub(r'```', '', text)
    start = text.find('<')
    end = text.rfind('>')
    if start != -1 and end != -1: return text[start:end+1].strip()
    return text.strip()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🧠 CBT Architect v5.0")
    api_key = st.text_input("Klucz Gemini API", type="password")
    st.divider()
    st.write(f"Krok {st.session_state.step} / 5")
    st.progress(st.session_state.step / 5)
    if st.button("🗑️ Resetuj"): st.session_state.clear(); st.rerun()

# --- KROKI ---

# KROK 1: METRYCZKA I BIOLOGIA
if st.session_state.step == 1:
    st.markdown("### 🧬 Krok 1: Biologia i Ryzyko")
    
    c1, c2 = st.columns(2)
    with c1:
        render_label("ID Pacjenta")
        st.session_state.id_p = st.text_input("l", value=st.session_state.id_p, key="w_id", label_visibility="collapsed")
        render_label("Wiek", "Lata")
        st.session_state.wiek = st.text_input("l", value=st.session_state.wiek, key="w_wiek", label_visibility="collapsed")
    with c2:
        render_label("Terapeuta")
        st.session_state.terapeuta = st.text_input("l", value=st.session_state.terapeuta, key="w_ter", label_visibility="collapsed")
        render_label("Płeć")
        st.session_state.plec = st.selectbox("l", ["Kobieta", "Mężczyzna", "Inna"], index=0, key="w_plec", label_visibility="collapsed")

    render_label("Diagnoza (ICD-10)")
    st.session_state.diagnoza = st.multiselect("l", ICD_10_LIST, default=st.session_state.diagnoza, key="w_diag", label_visibility="collapsed")
    
    c1, c2 = st.columns(2)
    with c1:
        render_label("Leczenie Farmakologiczne", "Nazwy leków i dawki")
        st.session_state.leki = st.text_input("l", value=st.session_state.leki, key="w_leki", label_visibility="collapsed")
    with c2:
        render_label("Funkcjonowanie Fizjologiczne", "Sen, apetyt, energia")
        st.session_state.fizjologia = st.multiselect("l", FIZJOLOGIA_LIST, default=st.session_state.fizjologia, key="w_fizjo", label_visibility="collapsed")

    render_label("Ocena Ryzyka (0-10)", "0 - brak, 10 - bezpośrednie zagrożenie życia")
    st.session_state.ryzyko_skala = st.slider("l", 0, 10, st.session_state.ryzyko_skala, key="w_ryz_s", label_visibility="collapsed")
    render_label("Opis Ryzyka / Czynniki Chroniące")
    st.session_state.ryzyko_opis = st.text_area("l", value=st.session_state.ryzyko_opis, key="w_ryz_o", label_visibility="collapsed")
    
    if st.button("Dalej ➡️"): st.session_state.step = 2; st.rerun()

# KROK 2: OBRAZ KLINICZNY
elif st.session_state.step == 2:
    st.markdown("### 🌩️ Krok 2: Mechanizmy Podtrzymujące")
    
    render_label("Główne Problemy i Objawy", "Co pacjent zgłasza jako problem?")
    st.session_state.problemy = st.text_area("l", value=st.session_state.problemy, key="w_prob", label_visibility="collapsed")
    
    render_label("Wyzwalacze (Triggers)", "Co uruchamia objawy? (Sytuacje, myśli, doznania)")
    st.session_state.wyzwalacze = st.text_area("l", value=st.session_state.wyzwalacze, key="w_trig", label_visibility="collapsed")
    
    c1, c2 = st.columns(2)
    with c1:
        render_label("Zachowania Zabezpieczające", "Co robi, żeby 'nie stało się nic złego'? (np. unikanie wzroku)")
        st.session_state.zach_zabezp = st.text_area("l", value=st.session_state.zach_zabezp, key="w_safe", label_visibility="collapsed")
    with c2:
        render_label("Strategie Radzenia Sobie (Coping)", "Jak próbuje sobie radzić? (np. alkohol, sen, sport)")
        st.session_state.coping = st.text_area("l", value=st.session_state.coping, key="w_cope", label_visibility="collapsed")

    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 1; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 3; st.rerun()

# KROK 3: PĘTLA (TU I TERAZ)
elif st.session_state.step == 3:
    st.markdown("### 🔄 Krok 3: Analiza Funkcjonalna (Pętla)")
    
    render_label("Sytuacja (Konkretne zdarzenie)", "Kto? Gdzie? Kiedy?")
    st.session_state.p_sit = st.text_area("l", value=st.session_state.p_sit, key="w_sit", label_visibility="collapsed")
    
    render_label("Myśl Automatyczna / Obraz", "Co przeszło przez głowę?")
    st.session_state.p_mysl = st.text_area("l", value=st.session_state.p_mysl, key="w_mysl", label_visibility="collapsed")
    
    render_label("Emocje (Wybierz)", "Główne stany emocjonalne")
    st.session_state.p_emocje_tagi = st.multiselect("l", EMOCJE_LIST, default=st.session_state.p_emocje_tagi, key="w_emo", label_visibility="collapsed")
    
    render_label("Zachowanie (Reakcja)", "Co pacjent zrobił?")
    st.session_state.p_zach = st.text_area("l", value=st.session_state.p_zach, key="w_zach", label_visibility="collapsed")
    
    render_label("Konsekwencje (Krótko- i Długoterminowe)", "Jaki był skutek?")
    st.session_state.p_koszt = st.text_area("l", value=st.session_state.p_koszt, key="w_koszt", label_visibility="collapsed")

    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 2; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 4; st.rerun()

# KROK 4: WARSTWA GŁĘBOKA
elif st.session_state.step == 4:
    st.markdown("### 🌳 Krok 4: Geneza i Kontekst")
    
    render_label("Historia Życia / Rodzina", "Tło, dzieciństwo, ważne relacje.")
    st.session_state.historia = st.text_area("l", value=st.session_state.historia, key="w_hist", label_visibility="collapsed")
    
    # --- NOWOŚĆ: WYDARZENIE KRYTYCZNE ---
    render_label("Wydarzenie Krytyczne (Początek problemu)", "Co się stało, że objawy wystąpiły TERAZ? (Zapalnik)")
    st.session_state.krytyczne = st.text_area("l", value=st.session_state.krytyczne, key="w_kryt", label_visibility="collapsed")
    
    c1, c2 = st.columns(2)
    with c1:
        render_label("Hipoteza: Przekonania Kluczowe", "O sobie, o świecie, o innych.")
        st.session_state.przekonania = st.text_area("l", value=st.session_state.przekonania, key="w_core", label_visibility="collapsed")
    with c2:
        render_label("Hipoteza: Zasady i Założenia", "'Jeśli..., to...'. Strategie kompensacyjne.")
        st.session_state.zasady = st.text_area("l", value=st.session_state.zasady, key="w_rules", label_visibility="collapsed")
    
    render_label("Zasoby (Poznawcze i Społeczne)", "Co działa dobrze? Na czym budować?")
    st.session_state.zasoby = st.text_area("l", value=st.session_state.zasoby, key="w_res", label_visibility="collapsed")
    
    render_label("Cele Pacjenta", "Co chce osiągnąć w terapii?")
    st.session_state.cele = st.text_area("l", value=st.session_state.cele, key="w_cele", label_visibility="collapsed")

    c1, c2 = st.columns(2)
    if c1.button("⬅️ Wstecz"): st.session_state.step = 3; st.rerun()
    if c2.button("Dalej ➡️"): st.session_state.step = 5; st.rerun()

# KROK 5: RAPORT
elif st.session_state.step == 5:
    st.markdown("### 🚀 Krok 5: Synteza Kliniczna")
    
    # Przygotowanie danych do promptu
    diagnoza_str = ", ".join(st.session_state.diagnoza)
    fizjo_str = ", ".join(st.session_state.fizjologia)
    emocje_str = ", ".join(st.session_state.p_emocje_tagi)
    
    st.subheader("1. Konceptualizacja (Dla Terapeuty)")
    
    if st.button("GENERUJ PEŁNĄ KONCEPTUALIZACJĘ", key="btn_gen"):
        if not api_key: st.error("Podaj klucz API!")
        else:
            try:
                client = genai.Client(api_key=api_key)
                prompt = f"""
                Jesteś superwizorem CBT. Stwórz zaawansowaną konceptualizację przypadku (Case Formulation) w CZYSTYM HTML.
                
                DANE PACJENTA:
                ID: {st.session_state.id_p}, Wiek: {st.session_state.wiek}, Płeć: {st.session_state.plec}
                Diagnoza: {diagnoza_str}
                Leki: {st.session_state.leki}, Fizjologia: {fizjo_str}
                Ryzyko (0-10): {st.session_state.ryzyko_skala}/10. Opis: {st.session_state.ryzyko_opis}
                
                OBRAZ KLINICZNY:
                Problemy: {st.session_state.problemy}
                Wyzwalacze: {st.session_state.wyzwalacze}
                Zach. Zabezpieczające: {st.session_state.zach_zabezp}
                Coping: {st.session_state.coping}
                
                GŁĘBOKA STRUKTURA POZNAWCZA:
                Historia: {st.session_state.historia}
                Wydarzenie Krytyczne (Początek): {st.session_state.krytyczne}
                Hipoteza Przekonań Kluczowych: {st.session_state.przekonania}
                Zasady/Założenia: {st.session_state.zasady}
                Zasoby: {st.session_state.zasoby}
                
                PĘTLA (TU I TERAZ):
                Syt: {st.session_state.p_sit}, Myśl: {st.session_state.p_mysl}, Emo: {emocje_str}, Zach: {st.session_state.p_zach}
                
                STRUKTURA RAPORTU HTML:
                
                <h2>1. Podsumowanie Kliniczne (Executive Summary)</h2>
                (Narracyjny opis przypadku łączący dane demograficzne, diagnozę, ryzyko i główne objawy w jeden spójny obraz.)
                
                <h2>2. Konceptualizacja Poznawcza (Model 5P)</h2>
                (Tabela HTML:
                 - Predyspozycje (Geneza, Historia)
                 - Czynniki Wyzwalające (Wydarzenie Krytyczne / Triggers)
                 - Problem Aktualny (Objawy)
                 - Czynniki Podtrzymujące (Mechanizmy CBT - nazwij je!)
                 - Czynniki Chroniące (Zasoby))
                 
                <h2>3. Model Aktywacji Schematów</h2>
                (Opisz mechanizm: Wyzwalacz -> Aktywacja Przekonania Kluczowego -> Strategia Kompensacyjna/Zabezpieczająca -> Objaw.)
                
                <h2>4. Analiza Funkcjonalna Zachowań</h2>
                (Wyjaśnij funkcję zachowań zabezpieczających. Dlaczego pacjent to robi? Co mu to daje na krótko (ulga), a co zabiera na długo?)
                
                <h2>5. Plan Terapii i Hierarchia Problemów</h2>
                (Ustal priorytety. Co leczymy najpierw? Zaproponuj techniki CBT do konkretnych problemów.)
                
                <h2>6. Ryzyka Procesowe i Trudności</h2>
                (Opisz możliwe przeszkody w terapii wynikające z osobowości, fizjologii lub strategii radzenia sobie.)
                
                <h2>7. Psychoedukacja ("Zdanie Klucz")</h2>
                (Jedno zdanie, metafora do powiedzenia pacjentowi, tłumacząca jego błędne koło.)
                """
                
                with st.spinner('Analiza danych klinicznych...'):
                    config = types.GenerateContentConfig(temperature=0.0)
                    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt, config=config)
                    st.session_state.final_report = extract_pure_html(response.text)
            except Exception as e: st.error(f"Błąd: {e}")

    if st.session_state.final_report:
        with st.expander("📄 Podgląd Dokumentacji", expanded=True):
            css = """<style>body{background:#1e293b;color:#e2e8f0;font-family:sans-serif;padding:20px}h2{color:#fff;border-bottom:1px solid #475569;margin-top:25px}table{width:100%;border-collapse:collapse;margin-top:10px;background:#f8fafc}td,th{border:1px solid #cbd5e1;padding:10px;color:#0f172a}th{background:#e2e8f0;font-weight:bold}</style>"""
            components.html(css + st.session_state.final_report, height=800, scrolling=True)
            
            dl_css = """<style>body{font-family:'Times New Roman',serif;padding:40px;color:black;max-width:900px}h2{border-bottom:2px solid #333}table{width:100%;border-collapse:collapse;margin:15px 0}th,td{border:1px solid black;padding:10px}th{background:#f0f0f0}</style>"""
            st.download_button("💾 Pobierz Raport (HTML)", f"<html><head>{dl_css}</head><body>{st.session_state.final_report}</body></html>", file_name="konceptualizacja.html")

    st.markdown("---")
    st.subheader("2. Materiały dla Pacjenta")
    if st.button("GENERUJ KARTĘ PRACY"):
        # (Kod generowania karty pracy - taki sam jak wcześniej, korzystający z nowych zmiennych)
        pass
