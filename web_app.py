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
    div[data-testid="stTextInput"] { max-width: 200px !important; }
    .report-card {
        background-color: white; padding: 15mm; color: black;
        font-family: 'Times New Roman', serif; border: 1px solid #000;
    }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    td, th { border: 1px solid black !important; padding: 10px; vertical-align: top; font-size: 14px; }
    th { background-color: #f2f2f2; }
    .header-box { text-align: center; border: 2px solid black; padding: 10px; margin-bottom: 20px; font-weight: bold; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

def wyczysc_html(tekst):
    tekst = re.sub(r'```html', '', tekst)
    tekst = re.sub(r'```', '', tekst)
    return tekst.strip()

# --- LOGIKA SESJI ---
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
    st.progress(st.session_state.step / 4)
    
    add_plan = st.checkbox("Plan kolejnych 5 sesji", value=True)
    add_relax = st.checkbox("Techniki relaksacyjne")
    
    if st.button("🗑️ Resetuj formularz"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.session_state.step = 1
        st.rerun()

# --- KROK 1: KONTEKST ---
if st.session_state.step == 1:
    st.header("Krok 1: Kontekst kliniczny")
    st.session_state.id_p = st.text_input("ID Pacjenta", value=st.session_state.get('id_p', ""))
    st.session_state.terapeuta = st.text_input("Terapeuta", value=st.session_state.get('terapeuta', ""))
    st.session_state.bio = st.text_area("1. Dane biograficzne", value=st.session_state.get('bio', ""), placeholder="Wiek, sytuacja życiowa...")
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

# --- KROK 3: PĘTLA CBT ---
elif st.session_state.step == 3:
    st.header("Krok 3: Pętla podtrzymująca (Model 5 obszarów)")
    st.session_state.p_sytuacja = st.text_area("Sytuacja", value=st.session_state.get('p_sytuacja', ""), placeholder="Co dokładnie się wydarzyło?")
    st.session_state.p_mysl = st.text_area("Myśl", value=st.session_state.get('p_mysl', ""), placeholder="Co przemknęło przez głowę?")
    st.session_state.p_reakcja = st.text_area("Emocje i ciało", value=st.session_state.get('p_reakcja', ""), placeholder="Co poczuł?")
    st.session_state.p_zachowanie = st.text_area("Zachowanie", value=st.session_state.get('p_zachowanie', ""), placeholder="Co zrobił?")
    st.session_state.p_koszt = st.text_area("Konsekwencja", value=st.session_state.get('p_koszt', ""), placeholder="Krótka ulga / Długi koszt?")

    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej (Konceptualizacja) ➡️", on_click=next_step)

# --- KROK 4: GENEROWANIE ---
elif st.session_state.step == 4:
    st.header("Krok 4: Finalizacja")
    st.session_state.rodzina = st.text_area("Historia rodzinna", value=st.session_state.get('rodzina', ""))
    st.session_state.cele = st.text_area("Cele terapii", value=st.session_state.get('cele', ""))
    st.session_state.custom_notes = st.text_area("Uwagi dodatkowe", value=st.session_state.get('custom_notes', ""))

    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    
    if c2.button("🚀 GENERUJ KOMPLETNĄ DOKUMENTACJĘ"):
        if not api_key:
            st.error("Wklej klucz API w panelu bocznym!")
        else:
            try:
                client = genai.Client(api_key=api_key)
                
                # Zbieranie dodatków
                extras = ""
                if add_plan: extras += "- Plan 5 sesji.\n"
                if add_relax: extras += "- 3 techniki relaksacyjne.\n"

                # Główny prompt kliniczny wykorzystujący strukturę lejka
                prompt = f"""Jesteś certyfikowanym superwizorem CBT. Przygotuj profesjonalną EKSPERTYZĘ KLINICZNĄ.
                
                STRUKTURA:
                1. ALERT RYZYKA (jeśli dotyczy).
                2. TABELA PRACY KLINICZNEJ (14 punktów wg wzoru DOCX, uwzględnij nasilenie objawów: Lęk {st.session_state.s_lek}/3, Nastrój {st.session_state.s_nastroj}/3, Sen {st.session_state.s_sen}/3, Relacje {st.session_state.s_relacje}/3).
                3. MODEL 5 OBSZARÓW (Na podstawie pętli: Syt: {st.session_state.p_sytuacja}, Myśl: {st.session_state.p_mysl}, Reakcja: {st.session_state.p_reakcja}, Zachowanie: {st.session_state.p_zachowanie}, Koszt: {st.session_state.p_koszt}).
                4. MODUŁ SUPERWIZYJNY I EDUKACJA O BŁĘDACH.
                5. {extras}
                
                UWAGI TERAPEUTY: {st.session_state.custom_notes}
                DANE: ID: {st.session_state.id_p}, Bio: {st.session_state.bio}, Problemy: {st.session_state.problemy}, Zasoby: {st.session_state.zasoby}, Rodzina: {st.session_state.rodzina}, Cele: {st.session_state.cele}.
                
                WYMAGANIA: Czysty HTML <table>, profesjonalny język, brak wstępów."""

                with st.spinner('Trwa generowanie raportu klinicznego...'):
                    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                    wynik = wyczysc_html(response.text)
                    
                    st.markdown("---")
                    st.markdown(f"""
                        <div class="report-card">
                            <div class="header-box">DOKUMENTACJA KLINICZNA I KONCEPTUALIZACJA</div>
                            <p><b>PACJENT:</b> {st.session_state.id_p} &nbsp;&nbsp; <b>TERAPEUTA:</b> {st.session_state.terapeuta}</p>
                            {wynik}
                        </div>
                    """, unsafe_allow_html=True)
                    st.download_button("Pobierz TXT", wynik, file_name=f"Raport_{st.session_state.id_p}.txt")
                    
            except Exception as e:
                st.error(f"Błąd Gemini: {e}")
