import streamlit as st

# --- NASTAVENIE STRÁNKY ---
st.set_page_config(page_title="Ekura Calc", page_icon="💰")

# --- LOGIKA (Funkcie) ---
def parse_yang(hodnota_str):
    """Prevod textu s k/kk/kkk na číslo."""
    try:
        if not hodnota_str: return 0.0
        hodnota_str = str(hodnota_str).lower().replace(" ", "").replace(",", ".")
        
        if "kkk" in hodnota_str:
            return float(hodnota_str.replace("kkk", "")) * 1000
        elif "kk" in hodnota_str:
            return float(hodnota_str.replace("kk", ""))
        elif "k" in hodnota_str:
            return float(hodnota_str.replace("k", "")) / 1000
        else:
            return float(hodnota_str)
    except ValueError:
        return 0.0

# --- INICIALIZÁCIA PREMENNÝCH ---
# Aby si stránka pamätala hodnoty, musíme ich inicializovať
if 'kurz' not in st.session_state: st.session_state.kurz = 180.0
if 'sd_input' not in st.session_state: st.session_state.sd_input = 0.0
if 'yang_input' not in st.session_state: st.session_state.yang_input = ""
if 'pocet_input' not in st.session_state: st.session_state.pocet_input = 200
if 'stack_mode' not in st.session_state: st.session_state.stack_mode = False
if 'history' not in st.session_state: st.session_state.history = []

# --- FUNKCIA RESET ---
def reset_app():
    """Vymaže hodnoty priamo v kľúčoch widgetov"""
    st.session_state.sd_input = 0.0
    st.session_state.yang_input = ""
    st.session_state.pocet_input = 200
    st.session_state.stack_mode = False
    # Kurz neresetujeme, ten si chceme pamätať

# --- DIZAJN APLIKÁCIE ---
st.title("Ekura - SD/Yang kalkulačka")

# Tlačidlo pre otvorenie BM
st.link_button("↗ Otvoriť Black Market", "https://www.ekura.cz/black_market/sindicate", type="secondary")

st.divider()

# 1. Časť - Kurz
# Ukladáme priamo do session_state
st.number_input("Cena šeku na BM (1kkk) v SD:", value=st.session_state.kurz, step=1.0, key="kurz")

# 2. Časť - Stack Logic
# Checkbox je priamo napojený na kľúč 'stack_mode'
is_stack = st.checkbox("zaškrtni, ak má item viac kusov (stack), napr. požehy", key="stack_mode")

pocet = 1
if is_stack:
    # Políčko pre počet, napojené na 'pocet_input'
    pocet = st.number_input("Celkový počet kusov:", min_value=1, step=1, key="pocet_input")

# 3. Časť - Ceny
col1, col2 = st.columns(2)
with col1:
    # Cena SD, napojená na 'sd_input'
    sd_hodnota = st.number_input("Cena CHCENEJ VECI na BM/IS (v SD):", min_value=0.0, step=1.0, key="sd_input")
with col2:
    # Cena Yang, napojená na 'yang_input'
    yang_text = st.text_input("Celková cena CHCENEJ VECI v hre (kk/kkk):", placeholder="napr. 900kk", key="yang_input")

st.write("") 

# Tlačidlo Vypočítať
if st.button("VYPOČÍTAŤ", type="primary", use_container_width=True):
    # Logika výpočtu
    cena_yang = parse_yang(yang_text)
    # Použijeme kurz zo session state
    aktualny_kurz = st.session_state.kurz 
    kurz_1sd = 1000 / aktualny_kurz if aktualny_kurz > 0 else 0
    
    teoreticka_cena = sd_hodnota * kurz_1sd
    rozdiel = cena_yang - teoreticka_cena
    
    percenta = (rozdiel / cena_yang * 100) if cena_yang > 0 else 0

    st.divider()
    
    # Výpis výsledku
    if rozdiel > 0:
        st.success(f" **Kúp to za SD!**\n\nUšetríš: **{rozdiel:.2f}kk**")
    elif rozdiel < 0:
        st.error(f" **Kúp to  za Yangy.**")
    else:
        st.info("⚖️ Ceny sú presne rovnaké.")

    # Detailný rozpis
    st.markdown(f"""
    **Detaily:**
    * Kurz: 1 SD = {kurz_1sd:.2f}kk
    * Výhodnosť: {percenta:.1f}%
    """)
    
    # Tabuľka CELKOVO
    data_total = {
        "Typ": "CELKOVO", 
        "Cena SD (prepočet)": f"{teoreticka_cena:.2f}kk", 
        "Cena v hre": f"{cena_yang:.2f}kk"
    }
    st.dataframe([data_total], use_container_width=True, hide_index=True)

    # Tabuľka NA KUS
    if pocet > 1:
        rozdiel_kus = rozdiel / pocet
        data_kus = {
            "Typ": "NA 1 KUS", 
            "Cena SD (prepočet)": f"{(teoreticka_cena/pocet):.2f}kk", 
            "Cena v hre": f"{(cena_yang/pocet):.2f}kk"
        }
        st.dataframe([data_kus], use_container_width=True, hide_index=True)
        
        if rozdiel_kus > 0:
            st.caption(f"Na jednom kuse ušetríš {rozdiel_kus:.3f}kk")
            
    # --- TARGET PRICE & BREAK EVEN POINT ---
    if cena_yang > 0 and sd_hodnota > 0:
        # Vzorec pre BEP šeku: (Cena v SD * 1000) / Cena v Yangoch
        bep_sek = (sd_hodnota * 1000) / cena_yang
        
        # Vzorec pre Target Price (Koľko SD by to malo stáť, aby si bol na nule)
        target_sd = (cena_yang * aktualny_kurz) / 1000
        
        st.info(f"""
        🎯 **Target price:**
        Aby sa ti nákup vyrovnal cene v Yangoch, musel by si na BM zaplatiť max **{target_sd:.0f} SD**.
        
        📉 **Break even point:**
        Ak by si to kúpil za týchto **{sd_hodnota:.0f} SD**, oplatí sa ti to dovtedy, 
        kým cena šeku na trhu klesne/stúpne MAX na **{bep_sek:.1f} SD/1kkk**.
        """)

    # --- ULOŽENIE DO HISTÓRIE ---
    st.session_state.history.insert(0, {
        "SD Cena": f"{sd_hodnota:.0f}",
        "Yang Cena": f"{cena_yang:.2f}kk",
        "Ks": pocet,
        "Ušetríš": f"{rozdiel:.2f}kk" if rozdiel > 0 else f"{rozdiel:.2f}kk",
        "Verdikt": "SD" if rozdiel > 0 else YANGY"
    })

# Reset tlačidlo - OPRAVENÉ
st.write("")
# Používame parameter on_click, ktorý spustí funkciu BEZPEČNE pred prekreslením
st.button("RESET", type="secondary", use_container_width=True, on_click=reset_app)

# --- HISTÓRIA VÝPOČTOV (Rozbaľovacie okno) ---
st.write("")
with st.expander("📜 História posledných výpočtov (Klikni pre zobrazenie)"):
    if st.session_state.history:
        st.dataframe(st.session_state.history, use_container_width=True)
        
        # Tlačidlo na vymazanie histórie
        if st.button("Vymazať históriu"):
            st.session_state.history = []
            st.rerun()
    else:
        st.caption("Zatiaľ žiadna história v tejto relácii.")
