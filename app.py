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

# --- 2. GELİŞMİŞ CSS & ANİMASYONLAR ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');

        /* GENEL SAYFA AYARLARI (Renkleri Sabitle) */
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
            color: #333333; /* Varsayılan yazı rengi koyu */
        }
        
        /* Ana Arka Plan */
        .stApp {
            background-color: #f4f6f9; /* Çok açık gri, göz yormaz */
        }

        /* SIDEBAR TASARIMI */
        [data-testid="stSidebar"] {
            background-color: #000000; /* BJK Siyahı */
            background-image: linear-gradient(180deg, #000000 0%, #1a1a1a 100%);
            border-right: 2px solid #E30613;
        }
        [data-testid="stSidebar"] * {
            color: #ffffff !important; /* Sidebar içindeki her şey beyaz */
        }
        
        /* MENÜ (Radyo Butonları) */
        .stRadio > div {
            padding-top: 20px;
        }
        .stRadio label {
            background-color: transparent;
            color: white !important;
            padding: 12px 20px;
            margin-bottom: 8px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            cursor: pointer;
            display: flex;
            align-items: center;
        }
        .stRadio label:hover {
            background-color: #E30613; /* BJK Kırmızısı */
            transform: translateX(5px);
            border-color: #E30613;
            box-shadow: 0 4px 15px rgba(227, 6, 19, 0.4);
        }
        /* Seçili olan menü öğesi */
        .stRadio [data-testid="stMarkdownContainer"] > p {
            font-weight: 600;
            font-size: 1.1rem;
        }

        /* GİRİŞ EKRANI KARTI */
        .login-card {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            border-top: 6px solid #E30613;
            text-align: center;
            animation: fadeIn 1s ease-in-out;
        }
        
        /* KPI KARTLARI (Özel Tasarım) */
        .kpi-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border-left: 5px solid #000;
            position: relative;
            overflow: hidden;
        }
        .kpi-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.15);
        }
        .kpi-card.red-border { border-left-color: #E30613; }
        .kpi-card.gray-border { border-left-color: #6c757d; }
        
        .kpi-title { font-size: 0.9rem; color: #888; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
        .kpi-value { font-size: 2.5rem; font-weight: 800; color: #1a1a1a; margin: 10px 0; }
        .kpi-icon { position: absolute; right: 20px; top: 20px; font-size: 3rem; color: #f0f0f0; z-index: 0; }
        
        /* BUTONLAR */
        .stButton > button {
            background: linear-gradient(45deg, #E30613, #b30000);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 50px;
            font-weight: 600;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 15px rgba(227, 6, 19, 0.3);
            transition: all 0.3s ease;
            width: 100%;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(227, 6, 19, 0.5);
            color: white !important;
        }

        /* ANİMASYONLAR */
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(20px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        
        /* İçerik Konteynerleri */
        .content-box {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.03);
            margin-bottom: 20px;
            animation: fadeIn 0.6s ease-out;
        }
        
        /* Tablo ve Dataframe Düzenlemeleri */
        [data-testid="stDataFrame"] {
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #eee;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# 3. YARDIMCI FONKSİYONLAR
# -------------------------------------------------------------------------
def convert_df_to_excel(df):
    """Excel indirme formatı."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Analiz')
    processed_data = output.getvalue()
    return processed_data

def process_data(file):
    """Veri işleme ve temizleme."""
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
        st.warning("⚠️ SMTP ayarları yapılandırılmamış. Kod: " + code) # Demo için kodu ekrana yaz (Gerçekte silinmeli)
        return True # Demo için True dönüyoruz

    msg = EmailMessage()
    msg.set_content(f"""
    Sayın Kullanıcı,
    
    BJK Portal Giriş Kodunuz: {code}
    
    Güvenliğiniz için bu kodu paylaşmayınız.
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
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        # Kart Başlangıcı
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Besiktas_jk.svg/240px-Besiktas_jk.svg.png", width=120)
        st.markdown("<h2 style='color:black; margin-top:10px;'>Personel Girişi</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#666;'>Beşiktaş JK Yönetim Portalı</p>", unsafe_allow_html=True)

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
    <div style='background-color: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; border-left: 6px solid #E30613; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
        <h1 style='margin:0; font-size: 2rem;'>🦅 Yönetim Paneli</h1>
        <p style='margin:0; color: #666;'>Hoş geldiniz, sisteme başarıyla giriş yaptınız.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Özel HTML KPI Kartları
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Aktif Sezon</div>
            <div class="kpi-value">2024-25</div>
            <div style="color: green; font-size: 0.9rem;">🟢 Sezon Devam Ediyor</div>
            <div class="kpi-icon">⚽</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="kpi-card red-border">
            <div class="kpi-title">Sıradaki Maç</div>
            <div class="kpi-value" style="font-size: 1.8rem;">BJK - FB</div>
            <div style="color: #E30613; font-size: 0.9rem;">📅 07.12.2024 - 20:00</div>
            <div class="kpi-icon">🎫</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="kpi-card gray-border">
            <div class="kpi-title">Bekleyen Rapor</div>
            <div class="kpi-value">3</div>
            <div style="color: #666; font-size: 0.9rem;">📥 Onay Bekliyor</div>
            <div class="kpi-icon">📊</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Alt Bölüm
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.markdown('<div class="content-box"><h3>📢 Duyurular & Bildirimler</h3><hr>', unsafe_allow_html=True)
        st.info("ℹ️ Kombine yenileme dönemi raporlarının Cuma günü mesai bitimine kadar sisteme yüklenmesi gerekmektedir.")
        st.warning("⚠️ Kuzey Tribünü turnike sistemlerinde yapılacak bakım nedeniyle verilerde gecikme olabilir.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_r:
        st.markdown('<div class="content-box"><h3>🔗 Hızlı Erişim</h3><hr>', unsafe_allow_html=True)
        st.button("🎫 Bilet Raporu Yükle")
        st.button("🏟️ Stadyum Planını Gör")
        st.button("📞 Destek Talebi Oluştur")
        st.markdown('</div>', unsafe_allow_html=True)

def page_bilet_analiz():
    st.markdown('<div class="content-box"><h2>🎫 Bilet Raporlama Sistemi</h2><p>Passolig\'den alınan Excel/CSV dosyalarını yükleyerek otomatik analiz yapabilirsiniz.</p></div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", type=['xlsx', 'xls', 'csv'])
    
    if uploaded_file:
        with st.spinner("Dosya analiz ediliyor, lütfen bekleyin..."):
            time.sleep(1) # Yapay gecikme (animasyon hissi için)
            df = process_data(uploaded_file)
            
        if df is not None:
            # Veri Hazırlığı
            match_summary = df.groupby('Mac')['Adet'].sum().sort_values(ascending=False).reset_index()
            total_tickets = match_summary['Adet'].sum()
            total_matches = len(match_summary)
            top_match = match_summary.iloc[0]

            # İstatistik Kartları (HTML)
            st.markdown(f"""
            <div style="display: flex; gap: 20px; margin-bottom: 30px;">
                <div class="kpi-card" style="flex:1; border-left-color: #000;">
                    <div class="kpi-title">Analiz Edilen Maç</div>
                    <div class="kpi-value">{total_matches}</div>
                </div>
                <div class="kpi-card" style="flex:1; border-left-color: #E30613;">
                    <div class="kpi-title">Toplam Bedelsiz Bilet</div>
                    <div class="kpi-value">{total_tickets:,.0f}</div>
                </div>
                <div class="kpi-card" style="flex:1; border-left-color: #555;">
                    <div class="kpi-title">Rekor Maç</div>
                    <div class="kpi-value" style="font-size: 1.5rem;">{top_match['Mac'][:15]}...</div>
                    <div style="color: #E30613; font-weight:bold;">{top_match['Adet']:,.0f} Adet</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Grafikler
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["📊 Genel Analiz", "🔍 Maç Detayı & İndir"])
            
            with tab1:
                fig = px.bar(match_summary, x='Mac', y='Adet', text_auto='.2s', 
                             color='Adet', color_continuous_scale=['#333333', '#E30613'])
                fig.update_layout(
                    title="Maç Bazlı Dağılım",
                    plot_bgcolor='white',
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
                                         color_discrete_sequence=['#1a1a1a'])
                        fig_det.update_layout(title=f"{selected_match} - Tribün Dağılımı", height=600)
                        st.plotly_chart(fig_det, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("👆 Başlamak için lütfen rapor dosyasını yükleyin.")

def page_stadyum_plani():
    st.markdown('<div class="content-box"><h2>🏟️ Tüpraş Stadyumu Planı</h2></div>', unsafe_allow_html=True)
    
    col_img, col_data = st.columns([2, 1])
    with col_img:
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Vodafone_Arena_nuit.jpg/1200px-Vodafone_Arena_nuit.jpg", use_container_width=True)
        st.caption("Stadyum Genel Görünüm")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_data:
        st.markdown("""
        <div class="content-box">
            <h4 style="color:#E30613;">Kapasite Bilgileri</h4>
            <ul style="list-style-type: none; padding: 0;">
                <li style="padding: 10px 0; border-bottom: 1px solid #eee;"><b>Toplam Kapasite:</b> 42.590</li>
                <li style="padding: 10px 0; border-bottom: 1px solid #eee;"><b>Doğu Tribünü:</b> 12.000</li>
                <li style="padding: 10px 0; border-bottom: 1px solid #eee;"><b>Batı Tribünü:</b> 10.500</li>
                <li style="padding: 10px 0; border-bottom: 1px solid #eee;"><b>Kuzey Kale Arkası:</b> 10.045</li>
                <li style="padding: 10px 0;"><b>Güney Kale Arkası:</b> 10.045</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def page_musteri_hizmetleri():
    st.markdown('<div class="content-box"><h2>📞 Müşteri Hizmetleri & Notlar</h2></div>', unsafe_allow_html=True)
    
    with st.expander("➕ Yeni Not Ekle", expanded=True):
        with st.form("not_form"):
            c1, c2 = st.columns(2)
            with c1: konu = st.text_input("Konu")
            with c2: personel = st.text_input("İlgili Personel")
            not_icerik = st.text_area("Not Detayı")
            if st.form_submit_button("Kaydet"):
                st.success("Not başarıyla kaydedildi.")
    
    st.markdown("### Son Kayıtlar")
    # Örnek Dataframe
    df_logs = pd.DataFrame({
        'Tarih': ['05.12.2024', '04.12.2024', '03.12.2024'],
        'Personel': ['Ahmet Y.', 'Mehmet K.', 'Ayşe D.'],
        'Konu': ['VIP Kombine İadesi', 'Passolig Sorunu', 'Engelli Bilet Başvurusu'],
        'Durum': ['🟢 Çözüldü', '🟡 Beklemede', '🟢 Çözüldü']
    })
    st.dataframe(df_logs, use_container_width=True, hide_index=True)

# -------------------------------------------------------------------------
# 6. SIDEBAR & NAVİGASYON
# -------------------------------------------------------------------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Besiktas_jk.svg/240px-Besiktas_jk.svg.png", width=140)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"<div style='background:rgba(255,255,255,0.1); padding:10px; border-radius:10px; margin-bottom:20px;'><small>Aktif Kullanıcı:</small><br><b>{st.session_state.get('email_to_verify', 'Yönetici')}</b></div>", unsafe_allow_html=True)
    
    # Menü
    selected_page = st.radio(
        "MENÜ", 
        ["Ana Sayfa", "Bilet Rapor Sistemi", "Stadyum Planı", "Müşteri Hizmetleri"],
        label_visibility="collapsed"
    )
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("GÜVENLİ ÇIKIŞ"):
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