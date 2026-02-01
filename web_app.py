import streamlit as st
from google import genai
from datetime import datetime
import re

# --- KONFIGURACJA I STYL ---
st.set_page_config(page_title="CBT Clinical Professional", layout="wide")

# CSS dla wyglądu raportu i pól
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1a365d; color: white; }
    .report-card {
        background-color: white; padding: 20mm; color: black;
        font-family: 'Times New Roman', serif; border: 1px solid #ccc;
    }
    .stTextArea textarea { border: 1px solid #cbd5e0 !important; height: 130px !important; }
    
    /* Stylizacja etykiet, aby były blisko pól */
    .stMarkdown p { margin-bottom: -10px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- SŁOWNIK TOOLTIPÓW ---
# Tutaj możesz edytować teksty, które pojawią się po najechaniu na ikonkę [i]
INFO = {
    "diagnoza": "Wprowadź kod ICD-10 lub DSM-5. Jest to kluczowe dla doboru odpowiedniego protokołu leczenia przez AI.",
    "ryzyko": "Opisz charakter myśli S., ich częstotliwość oraz czy pacjent posiada plan. AI wygeneruje na tej podstawie alert bezpieczeństwa.",
    "problemy": "Wymień główne dolegliwości (np. brak energii, lęk społeczny). AI pogrupuje je w kategorie kliniczne.",
    "mysli": "Wpisz dosłowne cytaty pacjenta. AI zidentyfikuje w nich błędy poznawcze (np. katastrofizację).",
    "p_sytuacja": "Opisz konkretne zdarzenie, które wywołało zmianę nastroju (Kto? Co? Gdzie? Kiedy?).",
    "p_mysl": "Co dokładnie przemknęło pacjentowi przez głowę w tej konkretnej chwili?",
    "p_emocja": "Określ emocje (np. smutek, złość) oraz reakcje z ciała (np. ucisk w klatce).",
    "p_zachowanie": "Co pacjent zrobił w odpowiedzi na te myśli i emocje? (np. wyszedł z pokoju, zaczął pić alkohol).",
    "p_konsekwencja": "Jaki był skutek tego zachowania? Skup się na tym, jak to zachowanie podtrzymuje problem w dłuższym czasie.",
    "hipotezy": "Twoja profesjonalna interpretacja mechanizmu (np. uwewnętrzniona krytyka rodzicielska)."
}

def wyczysc_html(tekst):
    tekst = re.sub(r'```html', '', tekst, flags=re.IGNORECASE)
    tekst = re.sub(r'```', '', tekst)
    return tekst.strip()

# --- LOGIKA NAWIGACJI ---
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
    st.subheader("🔵 Krok 1: Fakty Kliniczne")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.id_p = st.text_input("ID Pacjenta", value=st.session_state.get('id_p', ""))
        # Użycie parametru 'help' - tworzy ikonkę [i] z dymkiem obok etykiety
        st.session_state.diagnoza = st.text_input("Diagnoza (ICD/DSM)", value=st.session_state.get('diagnoza', ""), help=INFO["diagnoza"])
        
    with c2:
        st.session_state.terapeuta = st.text_input("Terapeuta", value=st.session_state.get('terapeuta', ""))
        st.session_state.leki = st.text_input("Farmakoterapia", value=st.session_state.get('leki', ""))
    
    st.markdown("---")
    st.session_state.ryzyko_poziom = st.selectbox("Poziom ryzyka", ["Brak / Niskie", "Umiarkowane", "Wysokie"], index=0)
    st.session_state.ryzyko_opis = st.text_area("Opis ryzyka / Plan bezpieczeństwa", value=st.session_state.get('ryzyko_opis', ""), help=INFO["ryzyko"])
    
    st.button("Dalej ➡️", on_click=next_step)

# --- KROK 2: OBJAWY ---
elif st.session_state.step == 2:
    st.subheader("🟣 Krok 2: Objawy i Myśli")
    
    st.session_state.problemy = st.text_area("Objawy i problemy", value=st.session_state.get('problemy', ""), help=INFO["problemy"])
    st.session_state.mysli_raw = st.text_area("Myśli automatyczne (Cytaty)", value=st.session_state.get('mysli_raw', ""), help=INFO["mysli"])
    
    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej ➡️", on_click=next_step)

# --- KROK 3: PĘTLA BECKA ---
elif st.session_state.step == 3:
    st.subheader("🟣 Krok 3: Pętla Podtrzymująca")
    
    st.session_state.p_sytuacja = st.text_area("Sytuacja (Wyzwalacz)", value=st.session_state.get('p_sytuacja', ""), help=INFO["p_sytuacja"])
    st.session_state.p_mysl = st.text_area("Kluczowa Myśl", value=st.session_state.get('p_mysl', ""), help=INFO["p_mysl"])
    st.session_state.p_emocja = st.text_area("Emocja / Ciało", value=st.session_state.get('p_emocja', ""), help=INFO["p_emocja"])
    st.session_state.p_zachowanie = st.text_area("Zachowanie (Strategia)", value=st.session_state.get('p_zachowanie', ""), help=INFO["p_zachowanie"])
    st.session_state.p_konsekwencja = st.text_area("Konsekwencja", value=st.session_state.get('p_konsekwencja', ""), help=INFO["p_konsekwencja"])
    
    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej ➡️", on_click=next_step)

# --- KROK 4: RELACJA I HIPOTEZY ---
elif st.session_state.step == 4:
    st.subheader("🔵 Krok 4: Relacja i Hipotezy")
    
    st.session_state.relacja = st.text_area("Relacja terapeutyczna", value=st.session_state.get('relacja', ""))
    st.session_state.historia = st.text_area("Kontekst historyczny", value=st.session_state.get('historia', ""))
    st.session_state.hipotezy = st.text_area("Hipotezy kliniczne", value=st.session_state.get('hipotezy', ""), help=INFO["hipotezy"])
    
    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej ➡️", on_click=next_step)

# --- KROK 5: GENEROWANIE ---
elif st.session_state.step == 5:
    st.header("Krok 5: Finalizacja")
    
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
                prompt = f"""Jesteś superwizorem CBT. Stwórz szczegółowy raport HTML na podstawie danych:
                ID: {st.session_state.id_p}, Diagnoza: {st.session_state.diagnoza}, Ryzyko: {st.session_state.ryzyko_opis},
                Problemy: {st.session_state.problemy}, Myśli: {st.session_state.mysli_raw}, 
                Pętla: {st.session_state.p_sytuacja} / {st.session_state.p_mysl} / {st.session_state.p_zachowanie}.
                Cele i Protokół: {add_goals}, {add_protocol}.
                Pamiętaj o Tabeli Padesky'ego, Triadzie Becka i zidentyfikowaniu zniekształceń poznawczych."""

                with st.spinner('Generowanie raportu...'):
                    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                    wynik = wyczysc_html(response.text)
                    st.markdown(f"<div class='report-card'>{wynik}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Błąd: {e}")
