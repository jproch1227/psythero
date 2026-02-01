import streamlit as st
from google import genai
from datetime import datetime
import re

# --- KONFIGURACJA I STYL ---
st.set_page_config(page_title="CBT Clinical Wizard", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1a365d; color: white; }
    .stProgress > div > div > div > div { background-color: #1a365d; }
    .stTextArea textarea { border: 1px solid #cbd5e0 !important; height: 120px !important; }
    /* Stylizacja pól ID i Terapeuty */
    div[data-testid="stTextInput"] { max-width: 200px !important; }
    .loop-box { background-color: #f8fafc; padding: 15px; border-radius: 10px; border-left: 5px solid #1a365d; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIKA SESJI (NAWIGACJA) ---
if 'step' not in st.session_state:
    st.session_state.step = 1

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1

# --- PANEL BOCZNY ---
with st.sidebar:
    st.title("⚙️ Nawigacja")
    api_key = st.text_input("Klucz Gemini API", type="password")
    st.divider()
    st.write(f"Krok {st.session_state.step} z 4")
    progress = (st.session_state.step / 4)
    st.progress(progress)
    if st.button("🗑️ Resetuj formularz"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.session_state.step = 1
        st.rerun()

# --- KROK 1: KONTEKST ---
if st.session_state.step == 1:
    st.header("Krok 1: Kontekst kliniczny")
    st.session_state.id_p = st.text_input("ID Pacjenta", value=st.session_state.get('id_p', ""))
    st.session_state.terapeuta = st.text_input("Terapeuta", value=st.session_state.get('terapeuta', ""))
    st.session_state.bio = st.text_area("1. Dane biograficzne", value=st.session_state.get('bio', ""), placeholder="Wiek, sytuacja życiowa, istotne wydarzenia...")
    st.button("Dalej (Objawy) ➡️", on_click=next_step)

# --- KROK 2: OBJAWY ---
elif st.session_state.step == 2:
    st.header("Krok 2: Problemy i nasilenie")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.s_lek = st.select_slider("Lęk", options=[0, 1, 2, 3], value=st.session_state.get('s_lek', 0))
        st.session_state.s_nastroj = st.select_slider("Nastrój", options=[0, 1, 2, 3], value=st.session_state.get('s_nastroj', 0))
    with col2:
        st.session_state.s_sen = st.select_slider("Sen", options=[0, 1, 2, 3], value=st.session_state.get('s_sen', 0))
        st.session_state.s_relacje = st.select_slider("Relacje", options=[0, 1, 2, 3], value=st.session_state.get('s_relacje', 0))
    
    st.session_state.problemy = st.text_area("Opis objawów", value=st.session_state.get('problemy', ""))
    st.session_state.zasoby = st.text_area("Zasoby pacjenta", value=st.session_state.get('zasoby', ""))
    
    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej (Pętla CBT) ➡️", on_click=next_step)

# --- KROK 3: PĘTLA CBT (SERCE APLIKACJI) ---
elif st.session_state.step == 3:
    st.header("Krok 3: Pętla podtrzymująca (Model 5 obszarów)")
    st.caption("Uchwyć mechanizm, który sprawia, że pacjent tkwi w problemie.")
    
    st.session_state.p_sytuacja = st.text_area("Sytuacja (Wyzwalacz)", value=st.session_state.get('p_sytuacja', ""), placeholder="Co dokładnie się wydarzyło? (Kto, co, gdzie?)", height=100)
    st.session_state.p_mysl = st.text_area("Myśl automatyczna", value=st.session_state.get('p_mysl', ""), placeholder="Co przemknęło pacjentowi przez głowę?", height=100)
    st.session_state.p_reakcja = st.text_area("Emocje i ciało", value=st.session_state.get('p_reakcja', ""), placeholder="Co poczuł w sercu i w ciele?", height=100)
    st.session_state.p_zachowanie = st.text_area("Zachowanie (Co pacjent zrobił?)", value=st.session_state.get('p_zachowanie', ""), placeholder="Unikanie, zabezpieczanie, walka?", height=100)
    st.session_state.p_koszt = st.text_area("Konsekwencja (Krótka ulga / Długi koszt)", value=st.session_state.get('p_koszt', ""), placeholder="Co pomogło na chwilę, a co pogorszyło sytuację później?", height=100)

    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej (Konceptualizacja) ➡️", on_click=next_step)

# --- KROK 4: PRZEKONANIA I RAPORT ---
elif st.session_state.step == 4:
    st.header("Krok 4: Przekonania i Cele")
    st.session_state.rodzina = st.text_area("Historia i wpływ rodziny", value=st.session_state.get('rodzina', ""))
    st.session_state.cele = st.text_area("Cele terapii", value=st.session_state.get('cele', ""))
    st.session_state.custom_notes = st.text_area("Dodatkowe uwagi do raportu", value=st.session_state.get('custom_notes', ""))

    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    
    if c2.button("🚀 GENERUJ KOMPLETNĄ DOKUMENTACJĘ"):
        # Tutaj wstawiamy logikę generowania Gemini z poprzednich wersji...
        st.success("Raport jest gotowy do wygenerowania (Logika Gemini zostanie uruchomiona po wpisaniu API Key)")
