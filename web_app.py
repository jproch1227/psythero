import streamlit as st
from google import genai
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Asystent CBT Premium", page_icon="🩺", layout="wide")

# Zaawansowany CSS dla profesjonalnego wyglądu raportu
st.markdown("""
    <style>
    .report-font { font-family: 'Inter', sans-serif; line-height: 1.6; color: #1a202c; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f1f5f9; border-radius: 4px 4px 0 0; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #1a365d ! Catholicism; color: white !important; }
    section[data-testid="stSidebar"] { background-color: #f8fafc; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Konfiguracja")
    api_key = st.text_input("Gemini API Key", type="password")
    st.divider()
    st.subheader("Tryb Interaktywny")
    add_plan = st.checkbox("Dodaj Plan 15 sesji")
    add_relax = st.checkbox("Dodaj Techniki Relaksacyjne")
    st.info("Zaznacz opcje powyżej, aby rozszerzyć raport.")

st.title("🩺 Kliniczny Asystent CBT")
st.caption("Profesjonalny generator dokumentacji klinicznej i arkuszy terapeutycznych")

# --- FORMULARZ ---
col1, col2 = st.columns(2)
with col1:
    id_p = st.text_input("ID Pacjenta", placeholder="np. 017")
    bio = st.text_area("Dane Bio/Medyczne", height=150)
    problemy = st.text_area("Główne trudności", height=150)
with col2:
    mysli = st.text_area("Kluczowe myśli/przekonania", height=150)
    rodzina = st.text_area("Kontekst rodzinny", height=150)

# --- PROCES GENEROWANIA ---
if st.button("🚀 GENERUJ KOMPLET DOKUMENTÓW"):
    if not api_key:
        st.error("Wklej klucz API w panelu bocznym!")
    elif not id_p:
        st.error("Podaj ID Pacjenta!")
    else:
        try:
            client = genai.Client(api_key=api_key)
            
            # Budowanie dynamicznego promptu
            extra_sections = ""
            if add_plan: extra_sections += "- Szczegółowy plan 15 sesji terapeutycznych.\n"
            if add_relax: extra_sections += "- Zestaw 3 spersonalizowanych technik relaksacyjnych.\n"

            p1 = f"""Jesteś certyfikowanym superwizorem CBT. Przygotuj profesjonalną EKSPERTYZĘ KLINICZNĄ dla pacjenta {id_p}. 
            ZASADY: 1. Zacznij bezpośrednio od nagłówka #. 2. Nie pisz wstępów typu 'Oto raport'. 3. Używaj czytelnych tabel Markdown.
            TREŚĆ:
            - Tabela Padesky'ego (5 obszarów).
            - Analiza Bio-Psycho-Społeczna (uwzględnij: {bio}).
            - Konceptualizacja (mechanizmy podtrzymujące).
            - Analiza Superwizyjna (Przeniesienie/Przeciwprzeniesienie).
            {extra_sections}
            DANE: {bio}, {problemy}, {mysli}, {rodzina}."""

            p2 = f"""Przygotuj ARKUSZ PRACY WŁASNEJ DLA PACJENTA {id_p}. 
            ZASADY: Zacznij od nagłówka # ARKUSZ PRACY WŁASNEJ. Nie pisz komentarzy bocznych.
            TREŚĆ: Stwórz tabelę 'Zapis myśli' wypełnioną przykładami bazującymi na: {mysli}. Pisz językiem wspierającym."""

            with st.spinner('Trwa generowanie dokumentacji wysokiej jakości...'):
                r1 = client.models.generate_content(model='gemini-2.0-flash', contents=p1)
                r2 = client.models.generate_content(model='gemini-2.0-flash', contents=p2)

                st.markdown("---")
                tab1, tab2 = st.tabs(["📋 RAPORT KLINICZNY", "🏠 ZADANIE DOMOWE"])
                
                with tab1:
                    st.markdown(f"<div class='report-font'>{r1.text}</div>", unsafe_allow_html=True)
                with tab2:
                    st.markdown(f"<div class='report-font'>{r2.text}</div>", unsafe_allow_html=True)
                    
        except Exception as e:
            st.error(f"Błąd komunikacji z modelem: {e}")

st.divider()
st.caption("Pamiętaj o anonimizacji danych przed wysłaniem do AI.")
