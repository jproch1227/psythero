import streamlit as st
from google import genai
from datetime import datetime
import re

# --- KONFIGURACJA I STYL ---
st.set_page_config(page_title="CBT Clinical Professional", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1a365d; color: white; }
    .stProgress > div > div > div > div { background-color: #1a365d; }
    
    /* Strefy odpowiedzialności */
    .clinician-zone { border-left: 5px solid #2b6cb0; padding-left: 15px; margin-bottom: 20px; background-color: #f7fafc; padding: 10px; }
    .ai-zone { border-left: 5px solid #805ad5; padding-left: 15px; margin-bottom: 20px; background-color: #f3e8ff; padding: 10px; }
    
    /* RAPORT FINALNY - Stylizacja dokumentu */
    .report-card {
        background-color: white; padding: 20mm; color: black;
        font-family: 'Times New Roman', serif; border: 1px solid #ccc;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    h1 { font-size: 26px; text-align: center; color: #000; margin-bottom: 30px; text-transform: uppercase; border-bottom: 2px solid #000; padding-bottom: 10px; }
    h2 { font-size: 18px; border-bottom: 1px solid #666; padding-bottom: 5px; margin-top: 30px; color: #1a365d; font-weight: bold; }
    h3 { font-size: 16px; margin-top: 20px; font-weight: bold; color: #333; }
    p, li, td { font-size: 14px; line-height: 1.6; }
    ul { margin-bottom: 15px; }
    
    /* Sekcje specjalne */
    .alert { background-color: #fff5f5; border: 2px solid #c53030; color: #c53030; padding: 15px; font-weight: bold; margin-bottom: 20px; }
    .goals-section { background-color: #f0fff4; border: 1px solid #2f855a; padding: 15px; margin-top: 20px; }
    .protocol-section { background-color: #ebf8ff; border: 1px solid #2b6cb0; padding: 15px; margin-top: 20px; }
    
    /* Tabele */
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    td, th { border: 1px solid black !important; padding: 10px; vertical-align: top; }
    th { background-color: #e2e8f0; font-weight: bold; text-align: left; }
    
    /* Pola tekstowe */
    .stTextArea textarea { border: 1px solid #cbd5e0 !important; height: 130px !important; }
    </style>
    """, unsafe_allow_html=True)

def wyczysc_html(tekst):
    tekst = re.sub(r'```html', '', tekst, flags=re.IGNORECASE)
    tekst = re.sub(r'```', '', tekst)
    return tekst.strip()

# --- LOGIKA SESJI ---
if 'step' not in st.session_state: st.session_state.step = 1

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1

# --- PANEL BOCZNY ---
with st.sidebar:
    st.title("🛡️ Panel Kontrolny")
    api_key = st.text_input("Klucz Gemini API", type="password")
    st.divider()
    st.info(f"Krok {st.session_state.step} / 5")
    st.progress(st.session_state.step / 5)

# --- KROK 1: FAKTY KLINICZNE ---
if st.session_state.step == 1:
    st.markdown("<div class='clinician-zone'><h3>🔵 Krok 1: Fakty Kliniczne</h3><p>Wprowadź twarde dane. AI nie może ich wymyślić.</p></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.id_p = st.text_input("ID Pacjenta", value=st.session_state.get('id_p', ""))
        st.session_state.diagnoza = st.text_input("Diagnoza (ICD-10/DSM-5)", value=st.session_state.get('diagnoza', ""))
    with c2:
        st.session_state.terapeuta = st.text_input("Terapeuta", value=st.session_state.get('terapeuta', ""))
        st.session_state.leki = st.text_input("Leczenie / Psychiatra", value=st.session_state.get('leki', ""))
    
    st.markdown("---")
    st.subheader("⚠️ Ocena Ryzyka")
    st.session_state.ryzyko_poziom = st.selectbox("Poziom ryzyka", ["Brak / Niskie", "Umiarkowane (plan bezp.)", "Wysokie (interwencja)"], index=0)
    st.session_state.ryzyko_opis = st.text_area("Opis ryzyka / Plan bezpieczeństwa", value=st.session_state.get('ryzyko_opis', ""), placeholder="Czy pacjent ma myśli S? Czy ma plan?")
    st.button("Dalej ➡️", on_click=next_step)

# --- KROK 2: OBJAWY ---
elif st.session_state.step == 2:
    st.markdown("<div class='clinician-zone'><h3>🟣 Krok 2: Objawy i Myśli</h3><p>Wpisz surowe dane. AI je uporządkuje.</p></div>", unsafe_allow_html=True)
    st.session_state.problemy = st.text_area("Objawy i problemy", value=st.session_state.get('problemy', ""))
    st.session_state.mysli_raw = st.text_area("Myśli automatyczne (Cytaty)", value=st.session_state.get('mysli_raw', ""))
    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej ➡️", on_click=next_step)

# --- KROK 3: PĘTLA BECKA ---
elif st.session_state.step == 3:
    st.markdown("<div class='clinician-zone'><h3>🟣 Krok 3: Pętla Podtrzymująca</h3><p>Opisz jedną sytuację modelową.</p></div>", unsafe_allow_html=True)
    st.session_state.p_sytuacja = st.text_area("Sytuacja", value=st.session_state.get('p_sytuacja', ""))
    st.session_state.p_mysl = st.text_area("Myśl", value=st.session_state.get('p_mysl', ""))
    st.session_state.p_emocja = st.text_area("Emocja / Ciało", value=st.session_state.get('p_emocja', ""))
    st.session_state.p_zachowanie = st.text_area("Zachowanie", value=st.session_state.get('p_zachowanie', ""))
    st.session_state.p_konsekwencja = st.text_area("Konsekwencja", value=st.session_state.get('p_konsekwencja', ""))
    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej ➡️", on_click=next_step)

# --- KROK 4: DANE JAKOŚCIOWE ---
elif st.session_state.step == 4:
    st.markdown("<div class='clinician-zone'><h3>🔵 Krok 4: Relacja i Hipotezy</h3><p>AI przepisze te dane 1:1.</p></div>", unsafe_allow_html=True)
    st.session_state.relacja = st.text_area("Relacja terapeutyczna", value=st.session_state.get('relacja', ""))
    st.session_state.historia = st.text_area("Kontekst historyczny", value=st.session_state.get('historia', ""))
    st.session_state.hipotezy = st.text_area("Hipotezy kliniczne", value=st.session_state.get('hipotezy', ""))
    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej ➡️", on_click=next_step)

# --- KROK 5: GENEROWANIE ---
elif st.session_state.step == 5:
    st.header("Krok 5: Finalizacja")
    
    st.info("Zaznacz, co AI ma dodać do raportu:")
    add_goals = st.checkbox("✅ Zaproponuj Cele Terapeutyczne (SMART)", value=True)
    add_protocol = st.checkbox("✅ Zaproponuj Protokół Leczenia (Plan Terapii)", value=True)
    
    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    
    if c2.button("🚀 GENERUJ PEŁNĄ DOKUMENTACJĘ"):
        if not api_key:
            st.error("Brak klucza API!")
        else:
            try:
                client = genai.Client(api_key=api_key)
                
                # Dynamiczne budowanie instrukcji, aby AI nie pominęło sekcji
                goals_instruction = ""
                if add_goals:
                    goals_instruction = """
                    6. CELE TERAPEUTYCZNE (Musi być wygenerowane):
                       - Zaproponuj 3 konkretne cele SMART na podstawie problemów pacjenta.
                       - Podziel na cele krótkoterminowe i długoterminowe.
                       - Umieść w sekcji <div class="goals-section">.
                    """
                
                protocol_instruction = ""
                if add_protocol:
                    protocol_instruction = f"""
                    7. PROTOKÓŁ LECZENIA (Musi być wygenerowane):
                       - Zaproponuj ramowy plan terapii dla diagnozy {st.session_state.diagnoza}.
                       - Wypisz etapy (Początek, Środek, Koniec).
                       - Wymień techniki (np. dialog sokratejski, ekspozycja).
                       - Umieść w sekcji <div class="protocol-section">.
                    """

                prompt = f"""Jesteś profesjonalnym superwizorem CBT. Twoim zadaniem jest stworzenie SZCZEGÓŁOWEGO i WYCZERPUJĄCEGO raportu klinicznego. Nie skracaj opisów. Raport ma wyglądać jak dokumentacja medyczna.

                INSTRUKCJA FORMATOWANIA:
                - Zwróć kod HTML. Używaj tagów <h1>, <h2>, <table>, <ul>, <li>.
                - Nie używaj znaczników markdown (```html).
                
                SEKCJE RAPORTU:
                1. DANE I RYZYKO: Jeśli ryzyko ({st.session_state.ryzyko_poziom}) > 'Niskie', stwórz wyraźny ALERT na górze (<div class="alert">). Wypisz dane pacjenta.
                2. OBJAWY I ZNIEKSZTAŁCENIA: Wypisz problemy. Myśli automatyczne ({st.session_state.mysli_raw}) nazwij pod kątem zniekształceń poznawczych.
                3. MODEL KONCEPTUALIZACJI: Stwórz Tabelę Pętli Becka z danych sytuacyjnych.
                4. TRIADA DEPRESYJNA: Opisz postrzeganie JA, ŚWIATA i PRZYSZŁOŚCI przez pacjenta.
                5. RELACJA I HISTORIA: Przepisz dokładnie dane od klinicysty.
                {goals_instruction}
                {protocol_instruction}

                DANE WEJŚCIOWE OD KLINICYSTY:
                ID: {st.session_state.id_p}, Diagnoza: {st.session_state.diagnoza}, Terapeuta: {st.session_state.terapeuta}
                Leczenie: {st.session_state.leki}, Ryzyko Opis: {st.session_state.ryzyko_opis}
                Problemy: {st.session_state.problemy}
                Sytuacja Pętli: {st.session_state.p_sytuacja}, Myśl: {st.session_state.p_mysl}, Emocja: {st.session_state.p_emocja}, Zachowanie: {st.session_state.p_zachowanie}, Konsekwencja: {st.session_state.p_konsekwencja}
                Relacja: {st.session_state.relacja}, Historia: {st.session_state.historia}, Hipotezy: {st.session_state.hipotezy}
                """

                with st.spinner('Generowanie szczegółowego raportu z celami i planem leczenia...'):
                    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                    wynik = wyczysc_html(response.text)
                    
                    st.markdown("---")
                    st.markdown(f"<div class='report-card'>{wynik}</div>", unsafe_allow_html=True)
                    st.download_button("Pobierz Raport (HTML)", wynik, file_name=f"Karta_CBT_{st.session_state.id_p}.html")
                    
            except Exception as e:
                st.error(f"Błąd: {e}")
