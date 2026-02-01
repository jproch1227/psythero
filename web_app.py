import streamlit as st
from google import genai
from datetime import datetime

# --- KONFIGURACJA ---
st.set_page_config(page_title="Asystent CBT", page_icon="🩺", layout="wide")

# CSS dla poprawy kontrastu i wyglądu
st.markdown("""
    <style>
    /* Stylowanie paska bocznego na ciemno */
    [data-testid="stSidebar"] {
        background-color: #1a365d;
        color: white;
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: white !important;
    }
    /* Styl raportu na środku */
    .report-card {
        background-color: white;
        padding: 30px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PANEL BOCZNY (Sidebar) - Tylko konfiguracja ---
with st.sidebar:
    st.title("⚙️ Konfiguracja")
    api_key = st.text_input("Klucz Gemini API", type="password")
    
    st.divider()
    st.subheader("Tryb Interaktywny")
    add_plan = st.checkbox("Dodaj Plan 15 sesji")
    add_relax = st.checkbox("Dodaj Relaksacje")
    
    st.info("Klucz API znajdziesz w Google AI Studio.")

# --- GŁÓWNA CZĘŚĆ (Środek strony) ---
st.title("🩺 Kliniczny Asystent CBT")
st.markdown("Wypełnij poniższy wywiad, aby wygenerować profesjonalną dokumentację.")

# Formularz na środku w dwóch kolumnach
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        id_p = st.text_input("ID Pacjenta", placeholder="np. 123")
        bio = st.text_area("Bio / Dane medyczne", height=150, placeholder="Wiek, stan zdrowia...")
        problemy = st.text_area("Trudności / Objawy", height=150, placeholder="Co się dzieje?")
    
    with col2:
        mysli = st.text_area("Kluczowe myśli", height=150, placeholder="Co pacjent o sobie myśli?")
        rodzina = st.text_area("Kontekst rodzinny", height=150, placeholder="Relacje z bliskimi...")
        cele = st.text_area("Cele terapii", height=68, placeholder="Co chcemy osiągnąć?")

generate_btn = st.button("🚀 GENERUJ KOMPLET DOKUMENTÓW")

# --- LOGIKA GENEROWANIA ---
if generate_btn:
    if not api_key:
        st.error("Wklej klucz API w lewym panelu!")
    elif not id_p:
        st.error("Podaj ID Pacjenta!")
    else:
        try:
            client = genai.Client(api_key=api_key)
            
            extra = ""
            if add_plan: extra += "- Szczegółowy plan 15 sesji terapeutycznych.\n"
            if add_relax: extra += "- 3 spersonalizowane techniki relaksacyjne.\n"

            # Bardzo surowy prompt, by uniknąć wstępów AI
            prompt = f"""Jesteś certyfikowanym superwizorem CBT. Przygotuj profesjonalną EKSPERTYZĘ KLINICZNĄ dla pacjenta {id_p}. 
            ZASADY: 
            1. Zacznij bezpośrednio od nagłówka # EKSPERTYZA. 
            2. Nie używaj żadnych wstępów. 
            3. Padesky'ego przedstaw w tabeli HTML (<table>).
            TREŚĆ: Tabela Padesky'ego, Analiza Bio-Psycho-Społeczna, Konceptualizacja, Superwizja.
            {extra}
            DANE: Bio: {bio}, Problemy: {problemy}, Myśli: {mysli}, Rodzina: {rodzina}, Cele: {cele}"""

            with st.spinner('Analizowanie przypadku klinicznego...'):
                response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                
                st.markdown("---")
                st.markdown(f"<div class='report-card'>{response.text}</div>", unsafe_allow_html=True)
                
                # Dodatkowa opcja kopiowania
                st.download_button("Pobierz raport (TXT)", response.text, file_name=f"Raport_{id_p}.txt")
                
        except Exception as e:
            st.error(f"Błąd: {e}")
