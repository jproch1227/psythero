import streamlit as st
from google import genai
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Asystent CBT Premium", layout="wide")

# Ukrywamy klucz API w boczny panelu dla bezpieczeństwa
with st.sidebar:
    st.title("Ustawienia")
    api_key = st.text_input("Wklej swój Gemini API Key", type="password")
    st.info("Klucz nie jest nigdzie zapisywany.")

st.title("🩺 Kliniczny Asystent CBT")
st.markdown("---")

# --- FORMULARZ WYWIADU ---
col1, col2 = st.columns(2)

with col1:
    id_p = st.text_input("ID Pacjenta")
    bio = st.text_area("Dane Bio/Medyczne", placeholder="Wiek, diagnozy, stan zdrowia...")
    problemy = st.text_area("Główne trudności", placeholder="Co się dzieje?")

with col2:
    mysli = st.text_area("Kluczowe myśli", placeholder="Cytaty pacjenta...")
    rodzina = st.text_area("Kontekst rodzinny", placeholder="Relacje, presja...")

if st.button("🚀 GENERUJ DOKUMENTACJĘ"):
    if not api_key:
        st.error("Proszę podać klucz API!")
    else:
        try:
            client = genai.Client(api_key=api_key)
            
            with st.spinner('Gemini analizuje przypadek kliniczny...'):
                # PROMPTY (Te same, które dopracowaliśmy wcześniej)
                p1 = f"Zacznij bezpośrednio od treści. Wszystkie zestawienia danych (np. Padesky) twórz wyłącznie w formie tabeli HTML (<table>). Przygotuj EKSPERTYZĘ KLINICZNĄ dla pacjenta {id_p}. Dane: {bio}, {problemy}, {mysli}, {rodzina}."
                
                response = client.models.generate_content(model='gemini-2.0-flash', contents=p1)
                
                # WYŚWIETLANIE NA STRONIE
                st.success("Raport wygenerowany!")
                st.markdown(response.text, unsafe_allow_html=True)
                
                # OPCJA POBRANIA (Prosty tekst)
                st.download_button("Pobierz jako tekst", response.text, file_name=f"Raport_{id_p}.txt")
        except Exception as e:
            st.error(f"Błąd: {e}")