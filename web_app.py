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
        color: #1a202c;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PANEL BOCZNY (Sidebar) ---
with st.sidebar:
    st.title("⚙️ Konfiguracja")
    api_key = st.text_input("Klucz Gemini API", type="password")
    
    st.divider()
    st.subheader("Tryb Interaktywny")
    add_plan = st.checkbox("Dodaj plan kolejnych 5 sesji")
    add_relax = st.checkbox("Dodaj techniki relaksacyjne dla pacjenta")
    
    st.info("Klucz API znajdziesz w Google AI Studio.")

# --- GŁÓWNA CZĘŚĆ (Środek strony) ---
st.title("🩺 Kliniczny Asystent CBT")
st.markdown("Wypełnij poniższy wywiad, aby wygenerować konceptualizację pacjenta.")
st.caption("Pamiętaj, aby nie podawać wrażliwych danych personalnych (nazwisk, adresów).")

# Formularz na środku w dwóch kolumnach
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        id_p = st.text_input("ID Pacjenta", placeholder="np. 123")
        bio = st.text_area("Bio / Dane medyczne", height=150, placeholder="Wiek, stan zdrowia, historia leczenia...")
        problemy = st.text_area("Trudności / Objawy", height=150, placeholder="Opisz obecne symptomy...")
    
    with col2:
        # Poprawione cudzysłowy w placeholderach
        mysli = st.text_area("Myśli automatyczne", height=150, placeholder="Np. 'Coś jest ze mną nie tak' lub 'Nie poradzę sobie'")
        rodzina = st.text_area("Kontekst rodzinny", height=150, placeholder="Relacje z bliskimi, historia rodzinna, wsparcie...")
        cele = st.text_area("Cele terapii", height=68, placeholder="Co pacjent chce osiągnąć w procesie?")

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
            if add_plan: extra += "- Szczegółowy plan 5 kolejnych sesji terapeutycznych (techniki i cele).\n"
            if add_relax: extra += "- 3 spersonalizowane techniki relaksacyjne dopasowane do profilu pacjenta.\n"

            prompt = f"""Jesteś certyfikowanym superwizorem CBT. Przygotuj profesjonalną EKSPERTYZĘ KLINICZNĄ dla pacjenta {id_p}. 
            ZASADY: 
            1. Zacznij bezpośrednio od nagłówka # EKSPERTYZA KLINICZNA. 
            2. Nie używaj żadnych wstępów ani komentarzy. 
            3. Tabelę Padesky'ego (5 obszarów) przygotuj jako czytelną tabelę HTML.
            TREŚĆ: Tabela Padesky'ego, Analiza Bio-Psycho-Społeczna, Konceptualizacja, Superwizja (przeniesienie/przeciwprzeniesienie).
            {extra}
            DANE PACJENTA: Bio: {bio}, Problemy: {problemy}, Myśli: {mysli}, Rodzina: {rodzina}, Cele: {cele}"""

            with st.spinner('Analizowanie przypadku... proszę czekać.'):
                response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                
                st.markdown("---")
                # Wyświetlenie raportu w stylowej karcie
                st.markdown(f"<div class='report-card'>{response.text}</div>", unsafe_allow_html=True)
                
                st.download_button(
                    label="Pobierz raport (TXT)",
                    data=response.text,
                    file_name=f"Ekspertyza_{id_p}_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
                
        except Exception as e:
            st.error(f"Wystąpił błąd: {e}")
