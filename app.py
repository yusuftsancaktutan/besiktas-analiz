import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import smtplib
from email.message import EmailMessage
import random
import time
from io import BytesIO

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(
    page_title="BJK Yönetim Portalı",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. GELİŞMİŞ "DARK MODE" CSS ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');

        /* GENEL SAYFA (Koyu Gri Zemin) */
        .stApp {
            background-color: #121212; /* En koyu gri */
            font-family: 'Poppins', sans-serif;
        }
        
        /* TÜM YAZILAR (Beyaz) */
        h1, h2, h3, h4, h5, h6, p, li, span, div {
            color: #e0e0e0 !important;
        }
        
        /* SIDEBAR (Tam Siyah) */
        [data-testid="stSidebar"] {
            background-color: #000000;
            border-right: 1px solid #333;
        }
        
        /* MENÜ BUTONLARI */
        .stRadio label {
            background-color: transparent;
            color: #e0e0e0 !important;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #333;
            transition: all 0.3s ease;
            margin-bottom: 5px;
        }
        .stRadio label:hover {
            background-color: #1a1a1a;
            border-color: #E30613; /* Kırmızı Çerçeve */
            color: #E30613 !important;
        }
        /* Radyo butonu yuvarlağını gizle, tam buton gibi görünsün */
        .stRadio div[role="radiogroup"] > label > div:first-child {
            display: none;
        }

        /* İÇERİK KUTULARI (Daha Açık Koyu Gri) */
        .content-box {
            background-color: #1e1e1e;
            padding: 25px;
            border-radius: 12px;
            border: 1px solid #333;
            border-left: 5px solid #E30613; /* Sol Kırmızı Çizgi */
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }
        
        /* GİRİŞ KARTI */
        .login-card {
            background-color: #1e1e1e;
            padding: 40px;
            border-radius: 20px;
            border: 2px solid #E30613; /* Kırmızı Çerçeve */
            box-shadow: 0 0 20px rgba(227, 6, 19, 0.2);
            text-align: center;
        }

        /* KPI KARTLARI */
        .kpi-card {
            background-color: #1e1e1e;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #333;
            border-bottom: 4px solid #E30613; /* Alt Kırmızı Çizgi */
            text-align: center;
            transition: transform 0.2s;
        }
        .kpi-card:hover {
            transform: translateY(-5px);
            border-color: #E30613;
        }
        .kpi-title { font-size: 0.9rem; color: #aaa !important; text-transform: uppercase; letter-spacing: 1px; }
        .kpi-value { font-size: 2.2rem; font-weight: 800; color: #ffffff !important; margin: 5px 0; }
        .kpi-sub { font-size: 0.8rem; color: #E30613 !important; font-weight: bold; }

        /* INPUT ALANLARI (Koyu Zemin) */
        .stTextInput > div > div > input {
            background-color: #2d2d2d;
            color: white;
            border: 1px solid #444;
            border-radius: 5px;
        }
        .stTextInput > div > div > input:focus {
            border-color: #E30613;
            box-shadow: none;
        }
        
        /* BUTONLAR (Kırmızı) */
        .stButton > button {
            background-color: #E30613;
            color: white !important;
            border: none;
            border-radius: 5px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: 0.3s;
        }
        .stButton > button:hover {
            background-color: #ff1f1f;
            box-shadow: 0 0 10px #E30613;
        }
        
        /* TABLO/DATAFRAME */
        [data-testid="stDataFrame"] {
            background-color: #1e1e1e;
            border: 1px solid #333;
        }
        
        /* METRİK RENKLERİ (Streamlit Native) */
        [data-testid="stMetricValue"] {
            color: #ffffff !important;
        }
        [data-testid="stMetricLabel"] {
            color: #aaaaaa !important;
        }
        
        /* SELECTBOX & UPLOAD */
        .stSelectbox > div > div {
            background-color: #2d2d2d;
            color: white;
        }
        .stFileUploader {
            background-color: #1e1e1e;
            padding: 20px;
            border: 1px dashed #555;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# 3. YARDIMCI FONKSİYONLAR
# -------------------------------------------------------------------------
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Analiz')
    processed_data = output.getvalue()
    return processed_data

def process_data(file):
    try:
        if file.name.endswith('.csv'):
            df_raw = pd.read_csv(file, header=None)
        else:
            df_raw = pd.read_excel(file, header=None)
        
        header_index = -1
        for i, row in df_raw.head(20).iterrows(): 
            row_str = row.astype(str).str.lower().to_string()
            if "maç" in row_str or "tribün" in row_str or "tribun" in row_str:
                header_index = i
                break
        
        if header_index == -1:
            st.error("❌ Dosyada uygun başlık satırı bulunamadı.")
            return None

        df_raw.columns = df_raw.iloc[header_index]
        df = df_raw[header_index + 1:].reset_index(drop=True)
        df.columns = [str(c).strip() for c in df.columns]
        
        cols = df.columns
        if len(cols) >= 3:
            rename_map = {cols[-1]: 'Adet', cols[-2]: 'Tribun', cols[0]: 'Mac'}
            df.rename(columns=rename_map, inplace=True)
        
        df = df[pd.to_numeric(df['Adet'], errors='coerce').notnull()]
        
        if df['Adet'].dtype == 'object':
             df['Adet'] = df['Adet'].astype(str).str.replace('.', '').str.replace(',', '.').astype(int)
        else:
             df['Adet'] = df['Adet'].astype(int)

        df = df[~df['Mac'].astype(str).str.contains('Toplam', case=False, na=False)]
        return df

    except Exception as e:
        st.error(f"Veri işlenirken hata oluştu: {e}")
        return None

# -------------------------------------------------------------------------
# 4. GÜVENLİK
# -------------------------------------------------------------------------
def send_verification_email(to_email, code):
    try:
        sender_email = st.secrets["smtp"]["email"]
        sender_password = st.secrets["smtp"]["password"]
        smtp_server = st.secrets["smtp"]["server"]
        smtp_port = st.secrets["smtp"]["port"]
    except Exception:
        st.warning(f"⚠️ SMTP Ayarı Yok. Kod: {code}") 
        return True 

    msg = EmailMessage()
    msg.set_content(f"""
    Giriş Kodunuz: {code}
    
    Bu kodu kimseyle paylaşmayınız.
    """)
    msg['Subject'] = 'BJK Portal - Giris Kodu'
    msg['From'] = sender_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"E-posta hatası: {e}")
        return False

def check_login():
    if st.session_state.get("logged_in", False):
        return True

    if "login_step" not in st.session_state:
        st.session_state["login_step"] = "email"
    if "verification_code" not in st.session_state:
        st.session_state["verification_code"] = None
    if "email_to_verify" not in st.session_state:
        st.session_state["email_to_verify"] = None

    # Şık Giriş Ekranı
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Kart Başlangıcı
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Besiktas_jk.svg/240px-Besiktas_jk.svg.png", width=100)
        st.markdown("<h3 style='margin-top:15px; color:white !important;'>PERSONEL GİRİŞİ</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888 !important; font-size:0.9rem;'>BJK Yönetim Portalı</p>", unsafe_allow_html=True)

        if st.session_state["login_step"] == "email":
            email_input = st.text_input("Kurumsal E-Posta", placeholder="ad.soyad@bjk.com.tr")
            if st.button("KOD GÖNDER"):
                if not email_input.strip().lower().endswith("@bjk.com.tr"):
                    st.error("⛔ Sadece @bjk.com.tr mailleri kabul edilir.")
                else:
                    code = str(random.randint(100000, 999999))
                    st.session_state["verification_code"] = code
                    st.session_state["email_to_verify"] = email_input
                    with st.spinner("Kod gönderiliyor..."):
                        if send_verification_email(email_input, code):
                            st.session_state["login_step"] = "verify"
                            st.rerun()

        elif st.session_state["login_step"] == "verify":
            st.success(f"📩 Kod gönderildi: {st.session_state['email_to_verify']}")
            code_input = st.text_input("Doğrulama Kodu", max_chars=6)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("GİRİŞ YAP"):
                    if code_input == st.session_state["verification_code"]:
                        st.session_state["logged_in"] = True
                        st.rerun()
                    else:
                        st.error("Hatalı kod!")
            with c2:
                if st.button("GERİ DÖN"):
                    st.session_state["login_step"] = "email"
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True) # Kart Bitişi

    return False

if not check_login():
    st.stop()

# -------------------------------------------------------------------------
# 5. SAYFA MODÜLLERİ
# -------------------------------------------------------------------------

def page_dashboard():
    # Header
    st.markdown("""
    <div style='background-color: #1e1e1e; padding: 20px; border-radius: 15px; margin-bottom: 20px; border-left: 6px solid #E30613;'>
        <h2 style='margin:0; color:white !important;'>🦅 YÖNETİM PANELİ</h2>
        <p style='margin:0; color: #888 !important;'>Hoş geldiniz, güncel veriler aşağıdadır.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Kartları
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">AKTİF SEZON</div>
            <div class="kpi-value">2024-25</div>
            <div class="kpi-sub">SEZON DEVAM EDİYOR</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">SIRADAKİ MAÇ</div>
            <div class="kpi-value" style="font-size:1.8rem;">BJK - FB</div>
            <div class="kpi-sub">📅 07.12.2024 - 20:00</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">BEKLEYEN RAPOR</div>
            <div class="kpi-value">3</div>
            <div class="kpi-sub">📥 ONAY BEKLİYOR</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Alt Bölüm
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.markdown('<div class="content-box"><h3>📢 Duyurular</h3><hr style="border-color:#333;">', unsafe_allow_html=True)
        st.info("ℹ️ Kombine yenileme raporları Cuma gününe kadar yüklenmelidir.")
        st.warning("⚠️ Kuzey Tribünü turnike bakım çalışması devam etmektedir.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_r:
        st.markdown('<div class="content-box"><h3>🔗 Hızlı Erişim</h3><hr style="border-color:#333;">', unsafe_allow_html=True)
        st.button("🎫 Bilet Raporu Yükle")
        st.button("🏟️ Stadyum Planı")
        st.markdown('</div>', unsafe_allow_html=True)

def page_bilet_analiz():
    st.markdown('<div class="content-box"><h2>🎫 Bilet Raporlama</h2><p style="color:#aaa;">Passolig raporunu yükleyerek analiz başlatın.</p></div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", type=['xlsx', 'xls', 'csv'])
    
    if uploaded_file:
        with st.spinner("Analiz ediliyor..."):
            time.sleep(1)
            df = process_data(uploaded_file)
            
        if df is not None:
            match_summary = df.groupby('Mac')['Adet'].sum().sort_values(ascending=False).reset_index()
            total_tickets = match_summary['Adet'].sum()
            total_matches = len(match_summary)
            top_match = match_summary.iloc[0]

            # KPI (Özet)
            st.markdown(f"""
            <div style="display: flex; gap: 20px; margin-bottom: 20px;">
                <div class="kpi-card" style="flex:1;">
                    <div class="kpi-title">ANALİZ EDİLEN</div>
                    <div class="kpi-value">{total_matches} Maç</div>
                </div>
                <div class="kpi-card" style="flex:1;">
                    <div class="kpi-title">TOPLAM BİLET</div>
                    <div class="kpi-value">{total_tickets:,.0f}</div>
                </div>
                <div class="kpi-card" style="flex:1;">
                    <div class="kpi-title">REKOR</div>
                    <div class="kpi-value" style="font-size:1.5rem;">{top_match['Mac'][:15]}...</div>
                    <div class="kpi-sub">{top_match['Adet']:,.0f} Adet</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Grafikler
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["📊 GENEL ANALİZ", "🔍 MAÇ DETAYI"])
            
            with tab1:
                # Plotly Dark Theme
                fig = px.bar(match_summary, x='Mac', y='Adet', text_auto='.2s', 
                             color='Adet', color_continuous_scale=['#333333', '#E30613'])
                fig.update_layout(
                    title="Maç Bazlı Bilet Dağılımı",
                    template="plotly_dark", # Koyu tema
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=500,
                    xaxis_title=None,
                    yaxis_title="Bilet Sayısı"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                excel_data = convert_df_to_excel(match_summary)
                st.download_button("📥 Özet Tabloyu İndir (Excel)", data=excel_data, file_name='genel_ozet.xlsx')

            with tab2:
                col_sel, col_gr = st.columns([1, 3])
                with col_sel:
                    st.markdown("### Maç Seçimi")
                    selected_match = st.selectbox("Detayını görmek istediğiniz maçı seçin:", match_summary['Mac'])
                    
                    if selected_match:
                        match_detail = df[df['Mac'] == selected_match].groupby('Tribun')['Adet'].sum().reset_index().sort_values(by='Adet', ascending=True)
                        st.markdown("<br>", unsafe_allow_html=True)
                        det_excel = convert_df_to_excel(match_detail)
                        st.download_button(f"📥 {selected_match[:10]}... İndir", data=det_excel, file_name=f"{selected_match}.xlsx")
                
                with col_gr:
                    if selected_match:
                        fig_det = px.bar(match_detail, x='Adet', y='Tribun', orientation='h', text_auto=True, 
                                         color_discrete_sequence=['#E30613'])
                        fig_det.update_layout(
                            title=f"{selected_match} - Tribün Dağılımı", 
                            template="plotly_dark",
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            height=600
                        )
                        st.plotly_chart(fig_det, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("👆 Başlamak için yukarıdaki alana rapor dosyasını sürükleyin.")

def page_stadyum_plani():
    st.markdown('<div class="content-box"><h2>🏟️ Tüpraş Stadyumu Planı</h2></div>', unsafe_allow_html=True)
    
    col_img, col_data = st.columns([2, 1])
    with col_img:
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        # Placeholder Resim
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Vodafone_Arena_nuit.jpg/1200px-Vodafone_Arena_nuit.jpg", use_container_width=True)
        st.caption("Stadyum Genel Görünüm")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_data:
        st.markdown("""
        <div class="content-box">
            <h4 style="color:#E30613 !important;">Kapasite Bilgileri</h4>
            <ul style="list-style-type: none; padding: 0; color:#ddd;">
                <li style="padding: 10px 0; border-bottom: 1px solid #333;"><b>Toplam Kapasite:</b> 42.590</li>
                <li style="padding: 10px 0; border-bottom: 1px solid #333;"><b>Doğu Tribünü:</b> 12.000</li>
                <li style="padding: 10px 0; border-bottom: 1px solid #333;"><b>Batı Tribünü:</b> 10.500</li>
                <li style="padding: 10px 0; border-bottom: 1px solid #333;"><b>Kuzey Kale Arkası:</b> 10.045</li>
                <li style="padding: 10px 0;"><b>Güney Kale Arkası:</b> 10.045</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def page_musteri_hizmetleri():
    st.markdown('<div class="content-box"><h2>📞 Destek & Notlar</h2></div>', unsafe_allow_html=True)
    
    with st.expander("➕ Yeni Not Ekle"):
        with st.form("not_form"):
            c1, c2 = st.columns(2)
            with c1: konu = st.text_input("Konu")
            with c2: personel = st.text_input("Personel")
            not_icerik = st.text_area("Not")
            if st.form_submit_button("KAYDET"):
                st.success("Kaydedildi.")
    
    st.markdown("### Son Kayıtlar")
    df_logs = pd.DataFrame({
        'Tarih': ['05.12.2024', '04.12.2024'],
        'Personel': ['Ahmet Y.', 'Mehmet K.'],
        'Konu': ['VIP İade', 'Passolig Sorunu'],
        'Durum': ['🟢 Çözüldü', '🟡 Beklemede']
    })
    st.dataframe(df_logs, use_container_width=True, hide_index=True)

# -------------------------------------------------------------------------
# 6. SIDEBAR & NAVİGASYON
# -------------------------------------------------------------------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Besiktas_jk.svg/240px-Besiktas_jk.svg.png", width=100)
    st.markdown("<br>", unsafe_allow_html=True)
    
    user_email = st.session_state.get('email_to_verify', 'Yönetici')
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; border-left:3px solid #E30613; margin-bottom:20px;'>
        <small style='color:#888;'>Aktif Kullanıcı:</small><br>
        <b style='color:white; font-size:0.9rem;'>{user_email}</b>
    </div>
    """, unsafe_allow_html=True)
    
    # Menü
    selected_page = st.radio(
        "MENÜ", 
        ["Ana Sayfa", "Bilet Rapor Sistemi", "Stadyum Planı", "Müşteri Hizmetleri"],
        label_visibility="collapsed"
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("ÇIKIŞ YAP"):
        st.session_state["logged_in"] = False
        st.session_state["login_step"] = "email"
        st.rerun()

# Yönlendirme
if selected_page == "Ana Sayfa":
    page_dashboard()
elif selected_page == "Bilet Rapor Sistemi":
    page_bilet_analiz()
elif selected_page == "Stadyum Planı":
    page_stadyum_plani()
elif selected_page == "Müşteri Hizmetleri":
    page_musteri_hizmetleri()