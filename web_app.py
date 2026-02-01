import streamlit as st
from google import genai
from datetime import datetime
import re

# --- KONFIGURACJA ---
st.set_page_config(page_title="Asystent CBT - Tabela Kliniczna", layout="wide")

# Nowy CSS - Surowy, profesjonalny styl tabeli klinicznej
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1a365d; color: white; }
    .report-card {
        background-color: white;
        padding: 20mm;
        color: black;
        font-family: 'Times New Roman', serif;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
    }
    td {
        border: 1px solid black !important;
        padding: 10px;
        vertical-align: top;
        font-size: 14px;
    }
    .col-label {
        width: 30%;
        font-weight: bold;
        background-color: #f2f2f2;
    }
    .header-box {
        text-align: center;
        border: 1px solid black;
        padding: 10px;
        margin-bottom: 20px;
        font-weight: bold;
        text-transform: uppercase;
    }
    @media print {
        .no-print { display: none; }
        body { background: white; }
    }
    </style>
    """, unsafe_allow_html=True)

# Funkcja czyszcząca
def wyczysc_html(tekst):
    tekst = re.sub(r'```html', '', tekst)
    tekst = re.sub(r'```', '', tekst)
    return tekst.strip()

# --- PANEL BOCZNY ---
with st.sidebar:
    st.title("⚙️ Konfiguracja")
    api_key = st.text_input("Klucz Gemini API", type="password")
    st.divider()
    st.subheader("Opcje dodatkowe")
    add_suicide_risk = st.checkbox("Dodaj ocenę ryzyka (SADS)")

# --- GŁÓWNA CZĘŚĆ ---
st.title("📄 Generator Tabeli Pracy Klinicznej")

col1, col2 = st.columns(2)
with col1:
    id_p = st.text_input("Numer pacjenta", placeholder="np. 6")
    terapeuta = st.text_input("Imię i nazwisko terapeuty")
    bio = st.text_area("1. Dane biograficzne", height=100)
    problemy = st.text_area("2. Prezentacja problemów", height=150)
with col2:
    mysli = st.text_area("Interpretacje/Myśli automatyczne", height=100)
    rodzina = st.text_area("Historia/Rodzina", height=150)

if st.button("🚀 GENERUJ TABELĘ KLINICZNĄ"):
    if not api_key: st.error("Brak klucza API!")
    else:
        client = genai.Client(api_key=api_key)
        
        # PROMPT wymuszający format 14 punktów z Twojego pliku .docx
        prompt = f"""Jesteś certyfikowanym terapeutą CBT. Przygotuj 'TABELĘ PRACY KLINICZNEJ' dokładnie według schematu:
        1. Dane biograficzne
        2. Prezentacja problemów
        3. Aktywacja poznawcza (bodźce)
        4. Błędna interpretacja doznań (myśli)
        5. Przesadna ocena zagrożenia
        6. Zachowania zabezpieczające i unikanie
        7. Skupienie uwagi na ciele/problemie
        8. Czynniki podtrzymujące (błędne koła)
        9. Doświadczenia z przeszłości (mechanizm powstawania)
        10. Przekonania kluczowe i warunkowe
        11. Cele terapeutyczne
        12. Planowane techniki i interwencje
        13. Potencjalne trudności w planie leczenia
        14. Przewidywany wynik i zapobieganie nawrotom.
        
        ZASADY:
        - Zwróć wyłącznie tabelę HTML o dwóch kolumnach.
        - W lewej kolumnie numer i nazwa sekcji (np. 1. Dane biograficzne), w prawej treść.
        - Styl: profesjonalny, kliniczny, bez wstępów.
        
        DANE: Terapeuta: {terapeuta}, Pacjent ID: {id_p}, Bio: {bio}, Problemy: {problemy}, Myśli: {mysli}, Rodzina: {rodzina}."""

        with st.spinner('Trwa generowanie tabeli...'):
            response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
            wynik = wyczysc_html(response.text)
            
            st.markdown(f"""
                <div class="report-card">
                    <div class="header-box">TABELA PRACY KLINICZNEJ</div>
                    <p><b>IMIĘ I NAZWISKO TERAPEUTY:</b> {terapeuta}<br>
                    <b>PACJENT (NUMER):</b> {id_p}</p>
                    {wynik}
                    <div style="font-size: 10px; margin-top: 20px;">Copyright © System Wspomagania Terapii Poznawczo-Behawioralnej</div>
                </div>
            """, unsafe_allow_html=True)
