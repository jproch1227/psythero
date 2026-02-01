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
    
    /* Strefy odpowiedzialności (paski boczne) */
    .clinician-zone { border-left: 5px solid #2b6cb0; padding-left: 15px; margin-bottom: 20px; background-color: #f7fafc; padding: 10px; }
    .ai-zone { border-left: 5px solid #805ad5; padding-left: 15px; margin-bottom: 20px; background-color: #f3e8ff; padding: 10px; }
    
    /* GŁÓWNA KARTA RAPORTU */
    .report-card {
        background-color: white; padding: 20mm; color: black;
        font-family: 'Times New Roman', serif; border: 1px solid #ccc;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Style elementów wewnątrz raportu */
    h1 { font-size: 24px; text-align: center; color: #333; margin-bottom: 20px; }
    h2 { font-size: 18px; border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-top: 25px; color: #1a365d; }
    p, li, td { font-size: 14px; line-height: 1.6; }
    
    /* Alerty i Ryzyko */
    .alert {
        background-color: #fff5f5; border: 1px solid #c53030; color: #c53030;
        padding: 15px; border-radius: 4px; margin-bottom: 20px;
    }
    
    /* Sugestie AI */
    .propozycja { color: #555; font-style: italic; }
    
    /* Tabele */
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    td, th { border: 1px solid black !important; padding: 8px; vertical-align: top; }
    th { background-color: #f0f0f0; font-weight: bold; text-align: left; }
    
    /* Pola tekstowe w formularzu */
    .stTextArea textarea { border: 1px solid #cbd5e0 !important; height: 130px !important; }
    </style>
    """, unsafe_allow_html=True)

def wyczysc_html(tekst):
    # Usuwa znaczniki markdown ```html oraz ``` na początku i końcu
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
    
    st.markdown("### Legenda:")
    st.markdown("🔵 **Ty (Klinicysta):** Fakty, ryzyko, relacja.")
    st.markdown("🟣 **AI (Asystent):** Struktura, plany, cele.")

# --- KROK 1: FAKTY KLINICZNE ---
if st.session_state.step == 1:
    st.markdown("<div class='clinician-zone'><h3>🔵 Krok 1: Fakty Kliniczne i Odpowiedzialność Prawna</h3><p>Te dane musisz wprowadzić Ty. AI nie może ich zgadywać.</p></div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.id_p = st.text_input("ID Pacjenta", value=st.session_state.get('id_p', ""))
        st.session_state.diagnoza = st.text_input("Rozpoznanie ICD/DSM (np. F32.1)", value=st.session_state.get('diagnoza', ""))
    with c2:
        st.session_state.terapeuta = st.text_input("Terapeuta", value=st.session_state.get('terapeuta', ""))
        st.session_state.leki = st.text_input("Farmakoterapia / Psychiatra", value=st.session_state.get('leki', ""))

    st.markdown("---")
    st.subheader("⚠️ Ocena Ryzyka (Safety Assessment)")
    st.session_state.ryzyko_poziom = st.selectbox("Poziom ryzyka samobójczego", ["Brak / Niskie", "Umiarkowane (wymaga planu)", "Wysokie (interwencja)"], index=0)
    st.session_state.ryzyko_opis = st.text_area("Opis ryzyka i Plan Bezpieczeństwa", value=st.session_state.get('ryzyko_opis', ""), placeholder="Wpisz fakty: charakter myśli S, czy zawarto kontrakt, telefon zaufania...")

    st.button("Dalej: Objawy i Myśli ➡️", on_click=next_step)

# --- KROK 2: DANE DO ROZBUDOWY ---
elif st.session_state.step == 2:
    st.markdown("<div class='clinician-zone'><h3>🟣 Krok 2: Objawy i Myśli Automatyczne</h3><p>Wpisz 'surowe' dane. AI pogrupuje je i nazwie zniekształcenia.</p></div>", unsafe_allow_html=True)
    
    st.session_state.problemy = st.text_area("Faktyczne objawy i problemy", value=st.session_state.get('problemy', ""))
    st.session_state.mysli_raw = st.text_area("Przykłady myśli automatycznych (Cytaty)", value=st.session_state.get('mysli_raw', ""))
    
    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej: Pętla CBT ➡️", on_click=next_step)

# --- KROK 3: PĘTLA BECKA ---
elif st.session_state.step == 3:
    st.markdown("<div class='clinician-zone'><h3>🟣 Krok 3: Pętla Podtrzymująca (Mechanizm)</h3><p>Opisz jedną sytuację wyzwalającą. AI zbuduje z tego tabelę.</p></div>", unsafe_allow_html=True)
    
    st.session_state.p_sytuacja = st.text_area("Sytuacja (Wyzwalacz)", value=st.session_state.get('p_sytuacja', ""))
    st.session_state.p_mysl = st.text_area("Kluczowa Myśl", value=st.session_state.get('p_mysl', ""))
    st.session_state.p_emocja = st.text_area("Emocja", value=st.session_state.get('p_emocja', ""))
    st.session_state.p_zachowanie = st.text_area("Zachowanie (Strategia)", value=st.session_state.get('p_zachowanie', ""))
    st.session_state.p_konsekwencja = st.text_area("Konsekwencja", value=st.session_state.get('p_konsekwencja', ""))

    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej: Relacja i Hipotezy ➡️", on_click=next_step)

# --- KROK 4: OBSERWACJE KLINICZNE ---
elif st.session_state.step == 4:
    st.markdown("<div class='clinician-zone'><h3>🔵 Krok 4: Relacja i Sens (Dane Jakościowe)</h3><p>To są Twoje oceny. AI je przepisze, nie ma prawa ich wymyślać.</p></div>", unsafe_allow_html=True)
    
    st.session_state.relacja = st.text_area("Obserwacja relacji i współpracy", value=st.session_state.get('relacja', ""))
    st.session_state.historia = st.text_area("Kontekst historyczny / Rodzinny", value=st.session_state.get('historia', ""))
    st.session_state.hipotezy = st.text_area("Twoje hipotezy kliniczne", value=st.session_state.get('hipotezy', ""))

    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej: Generowanie ➡️", on_click=next_step)

# --- KROK 5: GENEROWANIE ---
elif st.session_state.step == 5:
    st.header("Krok 5: Finalizacja Dokumentacji")
    add_goals = st.checkbox("Zaproponuj cele terapeutyczne (SMART)", value=True)
    add_protocol = st.checkbox("Zaproponuj protokół leczenia", value=True)
    
    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    
    if c2.button("🚀 GENERUJ PROFESJONALNĄ DOKUMENTACJĘ"):
        if not api_key:
            st.error("Brak klucza API!")
        else:
            try:
                client = genai.Client(api_key=api_key)
                
                prompt = f"""Jesteś asystentem klinicysty CBT.
                ZASADY FORMATOWANIA:
                1. Wygeneruj kod HTML, ale NIE umieszczaj go w blokach ```html. Zwróć czysty tekst zaczynający się od tagów HTML.
                2. Używaj klas CSS: <div class="alert"> dla ryzyka, <li class="propozycja"> dla celów/interwencji.
                
                ZADANIA:
                1. Jeśli ryzyko ({st.session_state.ryzyko_poziom}) jest wyższe niż 'Brak', stwórz sekcję ALERT na górze.
                2. Przepisz dokładnie dane od klinicysty: ID, Diagnoza, Relacja, Hipotezy.
                3. Zbuduj Tabelę Pętli Becka z danych: {st.session_state.p_sytuacja} itd.
                4. Nazwij zniekształcenia poznawcze w myślach: {st.session_state.mysli_raw}.
                5. Zbuduj triadę depresyjną (JA/ŚWIAT/PRZYSZŁOŚĆ).
                
                DANE:
                ID: {st.session_state.id_p}, Terapeuta: {st.session_state.terapeuta}, Diagnoza: {st.session_state.diagnoza}
                Leki: {st.session_state.leki}, Ryzyko opis: {st.session_state.ryzyko_opis}
                Problemy: {st.session_state.problemy}
                Relacja: {st.session_state.relacja}, Historia: {st.session_state.historia}, Hipotezy: {st.session_state.hipotezy}
                """

                with st.spinner('Przetwarzanie danych klinicznych...'):
                    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                    wynik = wyczysc_html(response.text)
                    
                    st.markdown("---")
                    # RENDEROWANIE HTML - To naprawia problem widocznego kodu
                    st.markdown(f"<div class='report-card'>{wynik}</div>", unsafe_allow_html=True)
                    
                    st.download_button("Pobierz Raport (TXT)", wynik, file_name=f"Karta_CBT_{st.session_state.id_p}.html")
                    
            except Exception as e:
                st.error(f"Błąd: {e}")
