import streamlit as st
from google import genai
from datetime import datetime
import re

# --- KONFIGURACJA ---
st.set_page_config(page_title="CBT Pro Dashboard", layout="wide")

# CSS - Styl Kliniczny (Biała karta, czarne ramki)
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
        font-family: sans-serif;
    }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 20px; }
    td, th { border: 1px solid black !important; padding: 10px; vertical-align: top; font-size: 14px; }
    th { background-color: #f2f2f2; font-weight: bold; }
    .header-box {
        text-align: center; border: 2px solid black; padding: 10px;
        margin-bottom: 20px; font-weight: bold; text-transform: uppercase; font-size: 18px;
    }
    /* Stylizacja pól tekstowych na pełną szerokość */
    .stTextArea textarea {
        border: 1px solid #cbd5e0 !important;
    }
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
    st.subheader("Moduły Raportu")
    add_plan = st.checkbox("Plan kolejnych 5 sesji")
    add_relax = st.checkbox("Techniki relaksacyjne")
    add_distortions = st.checkbox("Analiza błędów poznawczych + Edukacja", value=True)
    st.divider()
    if st.button("🗑️ Wyczyść wszystko"):
        st.rerun()

# --- GŁÓWNA CZĘŚĆ ---
st.title("🩺 System Kliniczny CBT")
st.markdown("Wypełnij dane pacjenta, aby otrzymać kompletną tabelę pracy klinicznej.")

# JEDNA KOLUMNA - PEŁNA SZEROKOŚĆ
with st.container():
    id_p = st.text_input("ID Pacjenta", placeholder="np. 06/2026")
    terapeuta = st.text_input("Imię i nazwisko terapeuty")
    
    st.markdown("---") # Oddzielenie danych podstawowych od wywiadu
    
    bio = st.text_area("1. Dane biograficzne", height=150)
    zasoby = st.text_input("Zasoby pacjenta")
    problemy = st.text_area("2. Problemy i objawy", height=200)
    mysli = st.text_area("Kluczowe myśli / Przekonania", height=200)
    rodzina = st.text_area("Historia rodzinna", height=200)
    cele = st.text_area("Cele terapii", height=100)

st.divider()

# Pole na dodatkowe życzenia
st.subheader("✍️ Uwagi końcowe do wersji ostatecznej")
custom_notes = st.text_area("Co jeszcze powinniśmy uwzględnić w tym konkretnym raporcie?", 
                            placeholder="Np. Chcę poradę dotyczącą tego w jaki sposób pracować z arachnofobią.",
                            height=100)

generate_btn = st.button("🚀 GENERUJ KOMPLETNĄ DOKUMENTACJĘ")

# --- LOGIKA ---
if generate_btn:
    if not api_key: st.error("Brak klucza API!")
    elif not id_p: st.error("Podaj ID pacjenta!")
    else:
        try:
            client = genai.Client(api_key=api_key)
            
            extras = ""
            if add_plan: extras += "- DODATEK: Plan 5 sesji.\n"
            if add_relax: extras += "- DODATEK: 3 techniki relaksacyjne.\n"
            if add_distortions: 
                extras += "- SEKCJA: Zidentyfikuj błędy poznawcze w myślach pacjenta i dodaj TABELĘ EDUKACYJNĄ 'Jak pracować z tymi błędami' (pytania sokratejskie, techniki).\n"

            prompt = f"""Jesteś certyfikowanym superwizorem i terapeutą CBT. Przygotuj profesjonalną dokumentację.
            
            STRUKTURA DOKUMENTU:
            1. ALERT RYZYKA (na samym początku, tylko jeśli są sygnały zagrożenia).
            2. TABELA PRACY KLINICZNEJ (14 punktów: Dane bio, Zasoby, Problemy, Aktywacja, Błędna interpretacja, Zagrożenie, Zabezpieczenia, Skupienie uwagi, Czynniki podtrzymujące, Przeszłość, Przekonania, Cele, Techniki, Trudności, Wynik).
            3. MODUŁ SUPERWIZYJNY (Czego się wystrzegać, język, narzędzia).
            4. {extras}
            
            UWAGI SPECJALNE OD TERAPEUTY DO UWZGLĘDNIENIA: {custom_notes}
            
            WYMAGANIA TECHNICZNE:
            - Wyłącznie czysty kod HTML (tabele <table>).
            - Styl surowy, kliniczny, bez wstępów.
            
            DANE PACJENTA: ID: {id_p}, Bio: {bio}, Problemy: {problemy}, Myśli: {mysli}, Zasoby {zasoby}, Rodzina: {rodzina}, Cele: {cele}."""

            with st.spinner('Analizowanie przypadku klinicznego...'):
                response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                wynik = wyczysc_html(response.text)
                
                if "Stabilny" not in wynik and ("RYZYKO" in wynik.upper() or "ALERT" in wynik.upper()):
                    st.markdown("<div class='risk-alert'>⚠️ UWAGA: WYKRYTO SYGNAŁY WYMAGAJĄCE SZCZEGÓLNEJ CZUJNOŚCI (RYZYKO/AUTOAGRESJA)</div>", unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown(f"""
                    <div class="report-card">
                        <div class="header-box">DOKUMENTACJA PRACY KLINICZNEJ I KONCEPTUALIZACJA</div>
                        <p><b>DATA:</b> {datetime.now().strftime('%d.%m.%Y')} &nbsp;&nbsp; <b>PACJENT NR:</b> {id_p}<br>
                        <b>TERAPEUTA PROWADZĄCY:</b> {terapeuta}</p>
                        {wynik}
                        <br><br>
                        <div style="border-top: 1px solid black; width: 250px; text-align: center; font-size: 11px;">
                            Podpis Terapeuty
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.download_button("Pobierz wersję tekstową", wynik, file_name=f"Raport_CBT_{id_p}.txt")
                
        except Exception as e:
            st.error(f"Błąd systemu: {e}")
