import streamlit as st
from google import genai
from datetime import datetime
import re

# --- KONFIGURACJA ---
st.set_page_config(page_title="Asystent CBT", page_icon="🩺", layout="wide")

# CSS - Poprawione style dla tabel, aby zawsze miały widoczne ramki
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1a365d; color: white; }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: white !important; }
    
    .report-card {
        background-color: white;
        padding: 40px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        color: #1a202c;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Stylizacja tabel - wymuszenie ramek */
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th { 
        background-color: #f1f5f9; 
        color: #1a365d; 
        border: 1px solid #cbd5e0 !important; 
        padding: 12px; 
        text-align: left; 
    }
    td { 
        border: 1px solid #cbd5e0 !important; 
        padding: 12px; 
        vertical-align: top; 
        line-height: 1.5; 
    }
    tr:nth-child(even) { background-color: #f8fafc; }
    </style>
    """, unsafe_allow_html=True)

# Funkcja czyszcząca odpowiedź AI z tagów typu ```html
def wyczysc_html(tekst):
    # Usuwa bloki kodu markdown: ```html ... ``` lub ``` ... ```
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
    add_relax = st.checkbox("Dodaj techniki relaksacyjne dla pacjenta")

# --- GŁÓWNA CZĘŚĆ ---
st.title("🩺 Kliniczny Asystent CBT")
st.markdown("Wypełnij poniższy wywiad, aby wygenerować konceptualizację.")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        id_p = st.text_input("ID Pacjenta", placeholder="np. 123")
        bio = st.text_area("Bio / Dane medyczne", height=150)
        problemy = st.text_area("Trudności / Objawy", height=150)
    with col2:
        mysli = st.text_area("Myśli automatyczne", height=150, placeholder="Np. 'Nie poradzę sobie'")
        rodzina = st.text_area("Kontekst rodzinny", height=150)
        cele = st.text_area("Cele terapii", height=68)

if st.button("🚀 GENERUJ KOMPLET DOKUMENTÓW"):
    if not api_key:
        st.error("Wklej klucz API!")
    elif not id_p:
        st.error("Podaj ID!")
    else:
        try:
            client = genai.Client(api_key=api_key)
            extra = ""
            if add_plan: extra += "- Plan 5 kolejnych sesji.\n"
            if add_relax: extra += "- 3 techniki relaksacyjne.\n"

            prompt = f"""Jesteś certyfikowanym superwizorem CBT. Przygotuj profesjonalną EKSPERTYZĘ KLINICZNĄ dla pacjenta {id_p}. 
            ZASADY: 
            1. Zacznij bezpośrednio od nagłówka #. 
            2. Nie używaj żadnych wstępów. 
            3. Tabelę Padesky'ego (5 obszarów) wygeneruj w czystym HTML (użyj tagów <table>, <tr>, <td>).
            TREŚĆ: Tabela Padesky'ego, Analiza Bio-Psycho-Społeczna, Konceptualizacja, Superwizja.
            {extra}
            DANE: Bio: {bio}, Problemy: {problemy}, Myśli: {mysli}, Rodzina: {rodzina}, Cele: {cele}"""

            with st.spinner('Trwa generowanie...'):
                response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                
                # Używamy funkcji czyszczącej
                wynik_html = wyczysc_html(response.text)
                
                st.markdown("---")
                # Wyświetlanie raportu z włączonym renderowaniem HTML
                st.markdown(f"<div class='report-card'>{wynik_html}</div>", unsafe_allow_html=True)
                
                st.download_button("Pobierz raport (TXT)", wynik_html, file_name=f"Raport_{id_p}.txt")
                
        except Exception as e:
            st.error(f"Błąd: {e}")
