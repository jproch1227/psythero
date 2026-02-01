import streamlit as st
from google import genai
import re

# --- KONFIGURACJA I STYL ---
st.set_page_config(page_title="CBT Clinical Wizard", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1a365d; color: white; }
    .stProgress > div > div > div > div { background-color: #1a365d; }
    /* Stylizacja ramek wg Twoich wytycznych */
    .stTextArea textarea { border: 1px solid #cbd5e0 !important; height: 150px !important; }
    div[data-testid="stTextInput"] { max-width: 150px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIKA SESJI (NAWIGACJA) ---
if 'step' not in st.session_state:
    st.session_state.step = 1

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1

# --- PANEL BOCZNY ---
with st.sidebar:
    st.title("⚙️ Ustawienia")
    api_key = st.text_input("Klucz Gemini API", type="password")
    st.divider()
    st.write(f"Jesteś w kroku: {st.session_state.step} z 2")
    if st.button("🗑️ Resetuj wszystko"):
        st.session_state.step = 1
        st.rerun()

# --- KROK 1: KONTEKST ---
if st.session_state.step == 1:
    st.header("Krok 1: Kontekst kliniczny")
    st.caption("Zacznij od osadzenia problemu w czasie i przestrzeni.")
    
    st.session_state.id_p = st.text_input("ID Pacjenta", value=st.session_state.get('id_p', ""), placeholder="np. 06")
    st.session_state.terapeuta = st.text_input("Imię i nazwisko terapeuty", value=st.session_state.get('terapeuta', ""))
    
    st.divider()
    st.session_state.bio = st.text_area("1. Dane biograficzne", value=st.session_state.get('bio', ""), height=150)
    
    st.button("Dalej (Objawy) ➡️", on_click=next_step)

# --- KROK 2: OBJAWY I NASILENIE ---
elif st.session_state.step == 2:
    st.header("Krok 2: Problemy i objawy")
    st.caption("Określ nasilenie kluczowych obszarów (0 - brak, 3 - bardzo silne).")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.s_lek = st.select_slider("Lęk / Niepokój", options=[0, 1, 2, 3], value=st.session_state.get('s_lek', 0))
        st.session_state.s_nastroj = st.select_slider("Obniżony nastrój", options=[0, 1, 2, 3], value=st.session_state.get('s_nastroj', 0))
    with col2:
        st.session_state.s_sen = st.select_slider("Problemy ze snem", options=[0, 1, 2, 3], value=st.session_state.get('s_sen', 0))
        st.session_state.s_relacje = st.select_slider("Trudności w relacjach", options=[0, 1, 2, 3], value=st.session_state.get('s_relacje', 0))

    st.divider()
    st.session_state.problemy = st.text_area("2. Problemy i objawy (opisowe)", value=st.session_state.get('problemy', ""), height=150)
    st.session_state.zasoby = st.text_area("Zasoby pacjenta", value=st.session_state.get('zasoby', ""), height=150)

    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1:
        st.button("⬅️ Wstecz", on_click=prev_step)
    with col_nav2:
        st.button("Generuj wstępny raport 🚀")
        st.info("W pełnej wersji tutaj przejdziemy do Kroku 3: Pętla CBT.")
