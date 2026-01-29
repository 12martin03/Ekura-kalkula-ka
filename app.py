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

# Inicializácia premenných (aby si stránka pamätala hodnoty a fungoval Reset)
if 'kurz' not in st.session_state: st.session_state.kurz = 180.0
if 'sd' not in st.session_state: st.session_state.sd = 0.0
if 'yang' not in st.session_state: st.session_state.yang = ""
if 'pocet' not in st.session_state: st.session_state.pocet = 200
if 'stack_mode' not in st.session_state: st.session_state.stack_mode = False

def reset_app():
    """Vymaže všetko okrem kurzu"""
    st.session_state.sd = 0.0
    st.session_state.yang = ""
    st.session_state.pocet = 200
    st.session_state.stack_mode = False

# --- DIZAJN APLIKÁCIE ---
st.title("Ekura - SD/Yang calc")

# Tlačidlo pre otvorenie BM (Nenásilné, pod nadpisom)
st.link_button("↗ Otvoriť Black Market", "https://www.ekura.cz/black_market/sindicate", type="secondary")

st.divider() # Čiara pre oddelenie

# 1. Časť - Kurz
st.session_state.kurz = st.number_input("Cena šeku (1kkk) v SD:", value=st.session_state.kurz, step=1.0)

# 2. Časť - Stack Logic (Viac kusov)
is_stack = st.checkbox("Viac kusov (Stack)", value=st.session_state.stack_mode, key="stack_mode")

pocet = 1
if is_stack:
    # Ak je zaškrtnuté, ukáže sa toto políčko hneď pod tým
    pocet = st.number_input("Celkový počet kusov:", min_value=1, value=st.session_state.pocet, step=1, key="pocet_input")
    st.session_state.pocet = pocet 

# 3. Časť - Ceny (SD a Yangy vedľa seba)
col1, col2 = st.columns(2)
with col1:
    sd_input = st.number_input("Cena BM (SD):", min_value=0.0, value=st.session_state.sd, step=1.0, key="sd_input")
    st.session_state.sd = sd_input
with col2:
    yang_input = st.text_input("Celková cena (Yang):", value=st.session_state.yang, placeholder="napr. 900kk", key="yang_input")
    st.session_state.yang = yang_input

st.write("") # Malá medzera

# Tlačidlo Vypočítať (Hlavné, výrazné - Primary)
if st.button("VYPOČÍTAŤ", type="primary", use_container_width=True):
    # Logika výpočtu
    cena_yang = parse_yang(yang_input)
    kurz_1sd = 1000 / st.session_state.kurz if st.session_state.kurz > 0 else 0
    teoreticka_cena = sd_input * kurz_1sd
    rozdiel = cena_yang - teoreticka_cena
    
    percenta = (rozdiel / cena_yang * 100) if cena_yang > 0 else 0

    st.divider()
    
    # Výpis výsledku (Zelená / Červená / Modrá)
    if rozdiel > 0:
        st.success(f"✅ **OPLATÍ SA ZA SD!**\n\nUšetríš: **{rozdiel:.2f}kk**")
    elif rozdiel < 0:
        st.error(f"❌ **NEOPLATÍ SA!**\n\nKúp to radšej za Yangy.")
    else:
        st.info("⚖️ Ceny sú presne rovnaké.")

    # Detailný rozpis (Kurz a percentá)
    st.markdown(f"""
    **Detaily:**
    * Kurz: 1 SD = {kurz_1sd:.2f}kk
    * Výhodnosť: {percenta:.1f}%
    """)
    
    # Tabuľka pre prehľad CELKOVO
    data_total = {
        "Typ": "CELKOVO", 
        "Cena SD (prepočet)": f"{teoreticka_cena:.2f}kk", 
        "Cena v hre": f"{cena_yang:.2f}kk"
    }
    st.dataframe([data_total], use_container_width=True, hide_index=True)

    # Tabuľka pre prehľad NA KUS (len ak je viac kusov)
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

# Reset tlačidlo (Pod čiarou, Secondary = sivé/biele podľa témy)
st.write("")
if st.button("RESET", type="secondary", use_container_width=True):
    reset_app()
    st.rerun()
