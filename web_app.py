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
    
    /* Stylizacja sekcji odpowiedzialności */
    .clinician-zone { border-left: 5px solid #2b6cb0; padding-left: 15px; margin-bottom: 20px; }
    .ai-zone { border-left: 5px solid #805ad5; padding-left: 15px; margin-bottom: 20px; }
    
    .report-card {
        background-color: white; padding: 15mm; color: black;
        font-family: 'Times New Roman', serif; border: 1px solid #000;
    }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    td, th { border: 1px solid black !important; padding: 10px; vertical-align: top; font-size: 14px; }
    th { background-color: #f2f2f2; }
    .header-box { text-align: center; border: 2px solid black; padding: 10px; margin-bottom: 20px; font-weight: bold; font-size: 18px; }
    
    /* Wymuszona wysokość pól tekstowych */
    .stTextArea textarea { border: 1px solid #cbd5e0 !important; height: 130px !important; }
    </style>
    """, unsafe_allow_html=True)

def wyczysc_html(tekst):
    tekst = re.sub(r'```html', '', tekst)
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

# --- KROK 1: FAKTY KLINICZNE (TYLKO KLINICYSTA) ---
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
    st.session_state.ryzyko_opis = st.text_area("Opis ryzyka i podjęte działania (Plan Bezpieczeństwa)", value=st.session_state.get('ryzyko_opis', ""), placeholder="Wpisz fakty: czy są myśli S? Jaki charakter? Czy zawarto kontrakt?")

    st.button("Dalej: Objawy i Myśli ➡️", on_click=next_step)

# --- KROK 2: DANE DO ROZBUDOWY (HYBRYDA) ---
elif st.session_state.step == 2:
    st.markdown("<div class='clinician-zone'><h3>🟣 Krok 2: Objawy i Myśli Automatyczne</h3><p>Wpisz 'surowe' dane. AI pogrupuje je, nazwie zniekształcenia i zaproponuje strukturę.</p></div>", unsafe_allow_html=True)
    
    st.session_state.problemy = st.text_area("Faktyczne objawy i problemy", value=st.session_state.get('problemy', ""), placeholder="Opisz objawy behawioralne, fizjologiczne, emocjonalne.")
    st.session_state.mysli_raw = st.text_area("Przykłady myśli automatycznych (Cytaty)", value=st.session_state.get('mysli_raw', ""), placeholder="Np. 'Nic mi nie wyjdzie', 'Wszyscy mnie oceniają'.")
    
    st.info("💡 AI w raporcie automatycznie przypisze do tych myśli kategorie (np. Katastrofizacja, Czytanie w myślach).")
    
    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej: Pętla CBT ➡️", on_click=next_step)

# --- KROK 3: PĘTLA BECKA (MODELOWANIE) ---
elif st.session_state.step == 3:
    st.markdown("<div class='clinician-zone'><h3>🟣 Krok 3: Pętla Podtrzymująca (Mechanizm)</h3><p>Opisz jedną, konkretną sytuację wyzwalającą. AI użyje tego do zbudowania modelu konceptualizacji.</p></div>", unsafe_allow_html=True)
    
    st.session_state.p_sytuacja = st.text_area("Sytuacja (Wyzwalacz)", value=st.session_state.get('p_sytuacja', ""))
    st.session_state.p_mysl = st.text_area("Kluczowa Myśl w tej sytuacji", value=st.session_state.get('p_mysl', ""))
    st.session_state.p_emocja = st.text_area("Emocja / Reakcja ciała", value=st.session_state.get('p_emocja', ""))
    st.session_state.p_zachowanie = st.text_area("Zachowanie (Strategia radzenia sobie)", value=st.session_state.get('p_zachowanie', ""))
    st.session_state.p_konsekwencja = st.text_area("Konsekwencja (Krótko/Długoterminowa)", value=st.session_state.get('p_konsekwencja', ""))

    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej: Relacja i Hipotezy ➡️", on_click=next_step)

# --- KROK 4: OBSERWACJE KLINICZNE (TYLKO KLINICYSTA) ---
elif st.session_state.step == 4:
    st.markdown("<div class='clinician-zone'><h3>🔵 Krok 4: Relacja i Sens (Dane Jakościowe)</h3><p>To są Twoje subiektywne oceny. AI przepisze je 1:1, ewentualnie uporządkuje stylistycznie. Nie ma prawa ich wymyślać.</p></div>", unsafe_allow_html=True)
    
    st.session_state.relacja = st.text_area("Obserwacja relacji i współpracy", value=st.session_state.get('relacja', ""), placeholder="Motywacja pacjenta, przymierze terapeutyczne, trudności w kontakcie...")
    st.session_state.historia = st.text_area("Kontekst historyczny / Rodzinny", value=st.session_state.get('historia', ""), placeholder="Fakty z przeszłości wpływające na obecne schematy.")
    st.session_state.hipotezy = st.text_area("Twoje hipotezy kliniczne (Interpretacja)", value=st.session_state.get('hipotezy', ""), placeholder="Np. 'Możliwe uwewnętrznienie presji sukcesu'.")

    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    c2.button("Dalej: Generowanie ➡️", on_click=next_step)

# --- KROK 5: GENEROWANIE I EDYCJA ---
elif st.session_state.step == 5:
    st.header("Krok 5: Finalizacja Dokumentacji")
    st.markdown("AI teraz połączy Twoje dane z modelami teoretycznymi CBT.")
    
    add_goals = st.checkbox("Niech AI zaproponuje cele terapeutyczne (na podstawie problemów)", value=True)
    add_protocol = st.checkbox("Niech AI zaproponuje standardowy protokół leczenia (dla podanej diagnozy)", value=True)
    
    c1, c2 = st.columns([1, 5])
    c1.button("⬅️ Wstecz", on_click=prev_step)
    
    if c2.button("🚀 GENERUJ PROFESJONALNĄ DOKUMENTACJĘ"):
        if not api_key:
            st.error("Brak klucza API!")
        else:
            try:
                client = genai.Client(api_key=api_key)
                
                # Instrukcje dla AI - Rygorystyczny podział ról
                prompt = f"""Jesteś asystentem klinicysty CBT. Twoim zadaniem jest uporządkowanie danych, a nie ich tworzenie.
                
                ZASADA 0 (BEZPIECZEŃSTWO): Jeśli w sekcji RYZYKO wpisano 'Wysokie' lub opisano myśli samobójcze, wygeneruj na początku dokumentu wyraźny ALERT z planem bezpieczeństwa.
                
                ZASADA 1 (FAKTY): Sekcje 'Diagnoza', 'Ryzyko', 'Relacja', 'Hipotezy' przepisz DOKŁADNIE tak, jak podał użytkownik. Nie dodawaj własnych przymiotników o relacji ("ciepła", "dobra"), jeśli nie ma ich w danych.
                
                ZASADA 2 (STRUKTURYZACJA - TU DZIAŁAJ):
                - Myśli automatyczne: Pogrupuj je i nazwij zniekształcenia poznawcze (np. Katastrofizacja).
                - Pętla Becka: Z danych (Sytuacja, Myśl...) stwórz czytelną tabelę modelu 5 obszarów.
                - Triada Depresyjna: Na podstawie myśli pacjenta, sformułuj jego widzenie JA, ŚWIATA i PRZYSZŁOŚCI.
                
                ZASADA 3 (PROPOZYCJE):
                - Jeśli zaznaczono opcję celów: Zaproponuj cele SMART pasujące do problemów. Oznacz jako "Propozycja".
                - Jeśli zaznaczono opcję protokołu: Zaproponuj standardowe interwencje CBT dla diagnozy {st.session_state.diagnoza}.
                
                DANE OD KLINICYSTY:
                ID: {st.session_state.id_p}, Diagnoza: {st.session_state.diagnoza}, Terapeuta: {st.session_state.terapeuta}
                Leczenie: {st.session_state.leki}
                RYZYKO: Poziom: {st.session_state.ryzyko_poziom}, Opis: {st.session_state.ryzyko_opis}
                
                PROBLEMY: {st.session_state.problemy}
                MYŚLI (CYTATY): {st.session_state.mysli_raw}
                
                PĘTLA SYTUACYJNA: Syt: {st.session_state.p_sytuacja}, Myśl: {st.session_state.p_mysl}, Emocja: {st.session_state.p_emocja}, Zach: {st.session_state.p_zachowanie}, Kons: {st.session_state.p_konsekwencja}
                
                RELACJA I HISTORIA: {st.session_state.relacja}, {st.session_state.historia}, {st.session_state.hipotezy}
                
                WYMAGANY FORMAT: Czysty HTML (<table>). Styl profesjonalny, suchy, medyczny.
                """

                with st.spinner('AI przetwarza dane, mapuje zniekształcenia i przygotowuje tabele...'):
                    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                    wynik = wyczysc_html(response.text)
                    
                    st.markdown("---")
                    st.markdown(f"""
                        <div class="report-card">
                            <div class="header-box">KARTA PRACY KLINICZNEJ CBT</div>
                            <table style="width:100%">
                                <tr><td><b>PACJENT:</b> {st.session_state.id_p}</td><td><b>TERAPEUTA:</b> {st.session_state.terapeuta}</td></tr>
                                <tr><td><b>DIAGNOZA:</b> {st.session_state.diagnoza}</td><td><b>DATA:</b> {datetime.now().strftime('%d.%m.%Y')}</td></tr>
                            </table>
                            <br>
                            {wynik}
                        </div>
                    """, unsafe_allow_html=True)
                    st.download_button("Pobierz Dokumentację (TXT)", wynik, file_name=f"Karta_CBT_{st.session_state.id_p}.txt")
                    
            except Exception as e:
                st.error(f"Błąd: {e}")
