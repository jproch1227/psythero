import streamlit as st
from google import genai
from datetime import datetime
import re

# --- KONFIGURACJA ---
st.set_page_config(page_title="CBT Clinical Dashboard", layout="wide")

# CSS - Styl Kliniczny 3.0
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1a365d; color: white; }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: white !important; }
    
    .report-card {
        background-color: white;
        padding: 15mm;
        color: black;
        font-family: 'Times New Roman', serif;
        border: 1px solid #000;
    }
    .risk-alert {
        background-color: #fff5f5;
        border: 2px solid #c53030;
        padding: 15px;
        color: #c53030;
        font-weight: bold;
        margin-bottom: 20px;
        border-radius: 5px;
    }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 20px; }
    td, th { border: 1px solid black !important; padding: 10px; vertical-align: top; font-size: 14px; }
    .col-label { width: 30%; font-weight: bold; background-color: #f2f2f2; }
    .header-box {
        text-align: center; border: 2px solid black; padding: 10px;
        margin-bottom: 20px; font-weight: bold; text-transform: uppercase; font-size: 18px;
    }
    .section-title { background-color: #e0e0e0; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

def wyczysc_html(tekst):
    tekst = re.sub(r'```html', '', tekst)
    tekst = re.sub(r'```', '', tekst)
    return tekst.strip()

# --- PANEL BOCZNY ---
with st.sidebar:
    st.title("⚙️ Konfiguracja")
    api_key = st.text_input("Klucz Gemini API", type="password")
    st.divider()
    st.subheader("Moduły Dodatkowe")
    add_plan = st.checkbox("Plan kolejnych 5 sesji")
    add_relax = st.checkbox("Techniki relaksacyjne")
    add_distortions = st.checkbox("Analiza zniekształceń poznawczych", value=True)
    st.divider()
    if st.button("🗑️ Wyczyść formularz"):
        st.rerun()

# --- GŁÓWNA CZĘŚĆ ---
st.title("🩺 System Wspomagania Pracy Klinicznej CBT")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        id_p = st.text_input("Numer pacjenta / Inicjały", placeholder="np. 06/2024")
        terapeuta = st.text_input("Terapeuta prowadzący")
        bio = st.text_area("1. Dane biograficzne i tło", height=120)
        problemy = st.text_area("2. Prezentacja problemów i objawów", height=150)
    with col2:
        mysli = st.text_area("Myśli automatyczne (cytaty)", height=120)
        rodzina = st.text_area("Historia rozwojowa i rodzinna", height=150)
        cele = st.text_area("Cele terapeutyczne", height=68)

if st.button("🚀 GENERUJ PEŁNĄ KONCEPTUALIZACJĘ"):
    if not api_key: st.error("Brak klucza API!")
    elif not id_p: st.error("Podaj dane pacjenta!")
    else:
        try:
            client = genai.Client(api_key=api_key)
            
            # Budowanie rozszerzeń
            extras = ""
            if add_plan: extras += "- Plan 5 kolejnych sesji (cele i techniki).\n"
            if add_relax: extras += "- 3 spersonalizowane techniki relaksacyjne.\n"
            if add_distortions: extras += "- Nazwij konkretne zniekształcenia poznawcze w myślach pacjenta.\n"

            prompt = f"""Jesteś doświadczonym superwizorem CBT. Na podstawie danych przygotuj:
            
            1. TABELĘ PRACY KLINICZNEJ (14 punktów): Dane biograficzne, Prezentacja problemów, Aktywacja poznawcza, Błędna interpretacja, Przesadna ocena zagrożenia, Zachowania zabezpieczające, Skupienie uwagi, Czynniki podtrzymujące, Doświadczenia z przeszłości, Przekonania kluczowe, Cele, Techniki, Trudności, Wynik.
            
            2. MODUŁ SUPERWIZYJNY: Czego się wystrzegać, jakiego języka używać, sugerowane kwestionariusze.
            
            3. ALERT RYZYKA: Jeśli w danych występują sygnały o zagrożeniu życia/zdrowia, wypisz je krótko na początku. Jeśli nie - napisz 'RYZYKO: Stabilny'.
            
            {extras}
            
            FORMATOWANIE: Używaj wyłącznie tabel HTML. Zacznij od razu od treści.
            DANE: Terapeuta: {terapeuta}, ID: {id_p}, Bio: {bio}, Problemy: {problemy}, Myśli: {mysli}, Rodzina: {rodzina}, Cele: {cele}."""

            with st.spinner('AI analizuje proces terapeutyczny...'):
                response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                wynik = wyczysc_html(response.text)
                
                # Prosta detekcja alertu ryzyka dla stylu
                if "RYZYKO: Stabilny" not in wynik:
                    st.markdown("<div class='risk-alert'>⚠️ WYKRYTO POTENCJALNE MARKERY RYZYKA - WYMAGANA CZUJNOŚĆ KLINICZNA</div>", unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="report-card">
                        <div class="header-box">TABELA PRACY KLINICZNEJ I KONCEPTUALIZACJA</div>
                        <p><b>DATA:</b> {datetime.now().strftime('%d.%m.%Y')} &nbsp;&nbsp; <b>TERAPEUTA:</b> {terapeuta} &nbsp;&nbsp; <b>PACJENT:</b> {id_p}</p>
                        {wynik}
                        <br><br>
                        <div style="border-top: 1px solid black; width: 200px; text-align: center;">
                            <p style="font-size: 10px;">Podpis i pieczęć terapeuty</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.download_button("Pobierz Dokument (TXT)", wynik, file_name=f"Konceptualizacja_{id_p}.txt")
                
        except Exception as e:
            st.error(f"Błąd: {e}")
