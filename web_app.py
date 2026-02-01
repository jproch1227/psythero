import streamlit as st
from google import genai
from datetime import datetime
import re

# --- KONFIGURACJA ---
st.set_page_config(page_title="Asystent CBT - Tabela Kliniczna", layout="wide")

# CSS - Stylizacja na wzór dokumentu klinicznego (DOCX)
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1a365d; color: white; }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: white !important; }
    
    .report-card {
        background-color: white;
        padding: 15mm;
        color: black;
        font-family: 'Times New Roman', serif;
        border: 1px solid #ccc;
    }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 20px; }
    td, th { border: 1px solid black !important; padding: 10px; vertical-align: top; font-size: 14px; }
    .col-label { width: 30%; font-weight: bold; background-color: #f2f2f2; }
    .header-box {
        text-align: center; border: 2px solid black; padding: 10px;
        margin-bottom: 20px; font-weight: bold; text-transform: uppercase;
    }
    .sub-header { background-color: #e0e0e0; font-weight: bold; text-align: center; }
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
    st.subheader("Tryb Interaktywny")
    add_plan = st.checkbox("Dodaj plan kolejnych 5 sesji")
    add_relax = st.checkbox("Dodaj techniki relaksacyjne")
    st.info("Zaznacz opcje, aby rozszerzyć raport o dodatkowe moduły.")

# --- GŁÓWNA CZĘŚĆ ---
st.title("📄 Generator Tabeli Pracy Klinicznej")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        id_p = st.text_input("Numer pacjenta", placeholder="np. 6")
        terapeuta = st.text_input("Imię i nazwisko terapeuty")
        bio = st.text_area("1. Dane biograficzne", height=100)
        problemy = st.text_area("2. Prezentacja problemów", height=150)
    with col2:
        mysli = st.text_area("Interpretacje / Myśli automatyczne", height=100)
        rodzina = st.text_area("Historia / Rodzina", height=150)
        cele = st.text_area("Cele i oczekiwania", height=68)

if st.button("🚀 GENERUJ KOMPLETNĄ DOKUMENTACJĘ"):
    if not api_key: st.error("Brak klucza API!")
    elif not id_p: st.error("Podaj numer pacjenta!")
    else:
        try:
            client = genai.Client(api_key=api_key)
            
            # Budowanie sekcji dodatkowych
            extra_instructions = ""
            if add_plan: extra_instructions += "- DODATEK: Przygotuj plan 5 kolejnych sesji.\n"
            if add_relax: extra_instructions += "- DODATEK: Przygotuj 3 techniki relaksacyjne.\n"

            prompt = f"""Jesteś certyfikowanym superwizorem CBT. Przygotuj dokumentację dla pacjenta {id_p}.
            
            DOKUMENT MA SIĘ SKŁADAĆ Z TRZECH CZĘŚCI:
            1. TABELA PRACY KLINICZNEJ (14 punktów wg wzoru: Dane biograficzne, Prezentacja problemów, Aktywacja poznawcza, Błędna interpretacja, Przesadna ocena zagrożenia, Zachowania zabezpieczające, Skupienie uwagi, Czynniki podtrzymujące, Doświadczenia z przeszłości, Przekonania kluczowe, Cele, Techniki, Trudności, Wynik).
            
            2. MODUŁ SUPERWIZYJNY (Tabela):
               - Czego się wystrzegać w prowadzeniu tego przypadku?
               - Jakiego języka używać w kontakcie z tym pacjentem?
               - Jakie konkretne narzędzia/kwestionariusze warto zastosować?
            
            3. DODATKI (Tylko jeśli wskazano): {extra_instructions}
            
            ZASADY: 
            - Wszystko w czystym HTML (<table>).
            - Styl profesjonalny, bez komentarzy typu 'Oto Twój raport'.
            
            DANE: Terapeuta: {terapeuta}, Bio: {bio}, Problemy: {problemy}, Myśli: {mysli}, Rodzina: {rodzina}, Cele: {cele}."""

            with st.spinner('Trwa generowanie dokumentacji...'):
                response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                wynik = wyczysc_html(response.text)
                
                st.markdown(f"""
                    <div class="report-card">
                        <div class="header-box">TABELA PRACY KLINICZNEJ</div>
                        <p><b>TERAPEUTA:</b> {terapeuta} &nbsp;&nbsp;&nbsp; <b>PACJENT NR:</b> {id_p}</p>
                        {wynik}
                    </div>
                """, unsafe_allow_html=True)
                
                st.download_button("Pobierz raport (TXT)", wynik, file_name=f"Tabela_Kliniczna_{id_p}.txt")
                
        except Exception as e:
            st.error(f"Błąd: {e}")
