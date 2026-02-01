import streamlit as st
from google import genai
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Asystent CBT", page_icon="🩺", layout="wide")

# Zaawansowany CSS dla poprawy widoczności liter i kolorystyki
st.markdown("""
    <style>
    /* Stylowanie panelu bocznego (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #1a365d;
        color: white;
    }
    /* Naprawa koloru tekstów w panelu bocznym */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: white !important;
    }
    /* Białe pola wprowadzania w ciemnym panelu */
    [data-testid="stSidebar"] .stTextArea textarea, [data-testid="stSidebar"] .stTextInput input {
        background-color: #ffffff;
        color: #1a202c;
    }
    /* Styl raportu po prawej stronie */
    .report-container {
        background-color: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- PANEL BOCZNY (CAŁY FORMULARZ) ---
with st.sidebar:
    st.title("🩺 Panel Sterowania")
    api_key = st.text_input("Klucz Gemini API", type="password")
    st.divider()
    
    st.subheader("Wywiad Kliniczny")
    id_p = st.text_input("ID Pacjenta", placeholder="np. 017")
    bio = st.text_area("Bio / Dane medyczne", height=100)
    problemy = st.text_area("Trudności / Objawy", height=100)
    mysli = st.text_area("Myśli / Przekonania", height=100)
    rodzina = st.text_area("Kontekst rodzinny", height=100)
    
    st.divider()
    st.subheader("Tryb Interaktywny")
    add_plan = st.checkbox("Dodaj Plan 15 sesji")
    add_relax = st.checkbox("Dodaj Relaksacje")
    
    generate_btn = st.button("🚀 GENERUJ RAPORT")

# --- GŁÓWNA CZĘŚĆ (WYŚWIETLANIE) ---
st.header("📄 Wynik Analizy Klinicznej")

if generate_btn:
    if not api_key:
        st.error("Wklej klucz API w lewym panelu!")
    elif not id_p:
        st.error("Podaj ID Pacjenta!")
    else:
        try:
            client = genai.Client(api_key=api_key)
            
            extra = ""
            if add_plan: extra += "- Plan 15 sesji terapeutycznych.\n"
            if add_relax: extra += "- 3 techniki relaksacyjne.\n"

            prompt = f"""Jesteś superwizorem CBT. Przygotuj profesjonalną EKSPERTYZĘ KLINICZNĄ (Tabela Padesky'ego, Analiza Bio-Psycho-Społeczna, Konceptualizacja, Superwizja) oraz ARKUSZ DLA PACJENTA.
            ZASADY: Zacznij bezpośrednio od treści. Używaj tabel HTML. Nie pisz wstępów.
            DODATKI: {extra}
            DANE: Bio: {bio}, Problemy: {problemy}, Myśli: {mysli}, Rodzina: {rodzina}, ID: {id_p}"""

            with st.spinner('Gemini przetwarza dane...'):
                response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                
                st.markdown("---")
                # Wyświetlamy raport w ładnym kontenerze
                st.markdown(f"<div class='report-container'>{response.text}</div>", unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Błąd: {e}")
else:
    st.info("Wypełnij dane w panelu po lewej stronie i kliknij przycisk, aby wygenerować analizę.")
