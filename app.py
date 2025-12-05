import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import smtplib
from email.message import EmailMessage
import random
import time
from io import BytesIO

# --- 1. Sayfa Konfigürasyonu (En başta olmalı) ---
st.set_page_config(
    page_title="BJK Bilet Departmanı",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Özel CSS (BJK Kurumsal Teması) ---
st.markdown("""
    <style>
        /* Genel Arka Plan */
        .stApp {
            background-color: #f8f9fa;
        }
        
        /* Sidebar (Sol Menü) Tasarımı */
        [data-testid="stSidebar"] {
            background-color: #1a1a1a;
            color: white;
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: white !important;
        }
        [data-testid="stSidebar"] label {
            color: #dddddd !important;
            font-weight: bold;
        }
        
        /* Radyo Butonları (Menü Öğeleri) */
        .stRadio > div {
            background-color: transparent;
        }
        .stRadio label {
            color: white !important;
            font-size: 16px;
            padding: 10px;
            border-radius: 5px;
            transition: 0.3s;
        }
        .stRadio label:hover {
            background-color: #333333;
        }
        
        /* Kırmızı Vurgular (Butonlar ve Metrikler) */
        div[data-testid="stMetricValue"] {
            color: #E30613; 
            font-weight: 900;
        }
        .stButton>button {
            background-color: #E30613;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #b30000;
            color: white;
            border: none;
        }

        /* Başlıklar */
        h1, h2, h3 {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-weight: 800;
            color: #1a1a1a;
        }
        
        /* Giriş Ekranı */
        div[data-testid="stForm"] {
            background-color: white;
            border-top: 5px solid #E30613;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# 3. YARDIMCI FONKSİYONLAR
# -------------------------------------------------------------------------
def convert_df_to_excel(df):
    """Dataframe'i indirilebilir Excel formatına çevirir."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Analiz')
    processed_data = output.getvalue()
    return processed_data

def process_data(file):
    """Excel/CSV dosyasını işler ve temizler."""
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
            st.error("Başlık satırı bulunamadı.")
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
        st.error(f"Veri hatası: {e}")
        return None

# -------------------------------------------------------------------------
# 4. GÜVENLİK VE GİRİŞ SİSTEMİ
# -------------------------------------------------------------------------
def send_verification_email(to_email, code):
    try:
        sender_email = st.secrets["smtp"]["email"]
        sender_password = st.secrets["smtp"]["password"]
        smtp_server = st.secrets["smtp"]["server"]
        smtp_port = st.secrets["smtp"]["port"]
    except Exception:
        st.error("SMTP ayarları bulunamadı! Lütfen Secrets ayarlarını yapılandırın.")
        return False

    msg = EmailMessage()
    msg.set_content(f"""
    Merhaba,
    
    Beşiktaş JK Bilet Departmanı Portal giriş kodunuz: {code}
    
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
        st.error(f"E-posta gönderim hatası: {e}")
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

    # Giriş Ekranı Düzeni
    col_spacer1, col_login, col_spacer2 = st.columns([1, 2, 1])
    with col_login:
        st.markdown("<br><br>", unsafe_allow_html=True)
        col_img, col_txt = st.columns([1, 3])
        with col_img:
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Besiktas_jk.svg/240px-Besiktas_jk.svg.png", width=100)
        with col_txt:
            st.markdown("## BJK Bilet Departmanı")
            st.caption("Personel Giriş Portalı")

        if st.session_state["login_step"] == "email":
            with st.form("email_form"):
                st.info("Kurumsal e-posta adresinizi giriniz.")
                email_input = st.text_input("E-posta Adresi", placeholder="ad.soyad@bjk.com.tr")
                submit_email = st.form_submit_button("Doğrulama Kodu Gönder")
                
                if submit_email:
                    if not email_input.strip().lower().endswith("@bjk.com.tr"):
                        st.error("⛔ Sadece @bjk.com.tr uzantılı mail adresleri kabul edilmektedir.")
                    else:
                        code = str(random.randint(100000, 999999))
                        st.session_state["verification_code"] = code
                        st.session_state["email_to_verify"] = email_input
                        with st.spinner("Kod gönderiliyor..."):
                            success = send_verification_email(email_input, code)
                        if success:
                            st.session_state["login_step"] = "verify"
                            st.rerun()

        elif st.session_state["login_step"] == "verify":
            with st.form("verify_form"):
                st.success(f"✅ Kod {st.session_state['email_to_verify']} adresine gönderildi.")
                code_input = st.text_input("6 Haneli Kodu Giriniz", max_chars=6)
                col_btn_ok, col_btn_cancel = st.columns(2)
                with col_btn_ok:
                    submit_code = st.form_submit_button("Girişi Onayla")
                with col_btn_cancel:
                    cancel = st.form_submit_button("Geri Dön")

                if cancel:
                    st.session_state["login_step"] = "email"
                    st.rerun()
                
                if submit_code:
                    if code_input == st.session_state["verification_code"]:
                        st.session_state["logged_in"] = True
                        st.success("Giriş Başarılı!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Hatalı kod!")
    return False

# Giriş Kontrolü
if not check_login():
    st.stop()

# -------------------------------------------------------------------------
# 5. SAYFA İÇERİKLERİ (Modüller)
# -------------------------------------------------------------------------

def page_dashboard():
    st.title("🦅 Yönetim Paneli")
    st.markdown("Hoş geldiniz. Sol menüden işlem yapmak istediğiniz modülü seçebilirsiniz.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background-color:white; padding:20px; border-radius:10px; border-left:5px solid #E30613; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <h4>🎫 Aktif Raporlar</h4>
            <p>Son yüklenen maç verilerine hızlı erişim.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background-color:white; padding:20px; border-radius:10px; border-left:5px solid #1a1a1a; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <h4>🏟️ Stadyum Durumu</h4>
            <p>Blok bazlı doluluk oranları ve planlar.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background-color:white; padding:20px; border-radius:10px; border-left:5px solid #E30613; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <h4>📞 Destek</h4>
            <p>Müşteri hizmetleri kayıtları ve notlar.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### Duyurular")
    st.info("📢 2024-2025 Sezonu Kombine satışları için analiz raporlarının Cuma gününe kadar tamamlanması gerekmektedir.")

def page_bilet_analiz():
    st.title("🎫 Bilet Raporlama Sistemi")
    st.markdown("Excel/CSV formatındaki Passolig raporlarını yükleyerek analiz yapabilirsiniz.")
    
    uploaded_file = st.file_uploader("Dosya Yükle", type=['xlsx', 'xls', 'csv'])
    
    if uploaded_file:
        df = process_data(uploaded_file)
        if df is not None:
            # Özet Veriler
            match_summary = df.groupby('Mac')['Adet'].sum().sort_values(ascending=False).reset_index()
            total_tickets = match_summary['Adet'].sum()
            total_matches = len(match_summary)
            
            # KPI
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Analiz Edilen Maç", f"{total_matches}")
            kpi2.metric("Toplam Bilet", f"{total_tickets:,.0f}".replace(',', '.'))
            kpi3.metric("En Yüksek Maç", f"{match_summary.iloc[0]['Adet']:,.0f}", delta=match_summary.iloc[0]['Mac'][:15]+"...")
            
            st.markdown("---")
            
            # Grafikler
            tab1, tab2 = st.tabs(["📊 Genel Analiz", "🔍 Maç Detayı"])
            
            with tab1:
                fig = px.bar(match_summary, x='Mac', y='Adet', text_auto='.2s', 
                             color='Adet', color_continuous_scale=['#333333', '#E30613'],
                             title="Maç Bazlı Bilet Dağılımı")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                # Excel İndir
                excel_data = convert_df_to_excel(match_summary)
                st.download_button("📥 Özet Tabloyu İndir", data=excel_data, file_name='ozet_rapor.xlsx')

            with tab2:
                selected_match = st.selectbox("Maç Seçiniz:", match_summary['Mac'])
                if selected_match:
                    match_detail = df[df['Mac'] == selected_match].groupby('Tribun')['Adet'].sum().reset_index().sort_values(by='Adet', ascending=True)
                    
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        fig_det = px.bar(match_detail, x='Adet', y='Tribun', orientation='h', text_auto=True, 
                                         color_discrete_sequence=['#1a1a1a'], title=f"{selected_match} Tribün Dağılımı")
                        st.plotly_chart(fig_det, use_container_width=True)
                    with c2:
                        st.dataframe(match_detail.sort_values(by='Adet', ascending=False), use_container_width=True, hide_index=True)
                        
                        det_excel = convert_df_to_excel(match_detail)
                        st.download_button("📥 Detayı İndir", data=det_excel, file_name=f"{selected_match}_detay.xlsx")
    else:
        st.info("👆 Analize başlamak için lütfen yukarıdan dosya yükleyiniz.")

def page_stadyum_plani():
    st.title("🏟️ Stadyum Planı ve Bloklar")
    st.markdown("Tüpraş Stadyumu blok yerleşim planı ve kapasite bilgileri.")
    
    col_img, col_info = st.columns([2, 1])
    with col_img:
        # Temsili stadyum görseli (Placeholder)
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Vodafone_Arena_nuit.jpg/1200px-Vodafone_Arena_nuit.jpg", 
                 caption="Tüpraş Stadyumu", use_container_width=True)
    
    with col_info:
        st.subheader("Kapasite Bilgileri")
        st.markdown("""
        - **Toplam Kapasite:** 42.590
        - **Doğu Tribünü:** 12.000
        - **Batı Tribünü:** 10.500
        - **Kuzey Kale Arkası:** 10.045
        - **Güney Kale Arkası:** 10.045
        """)
        
        st.warning("⚠️ Kuzey Üst Tribünü'nde bakım çalışması planlanmaktadır.")

def page_musteri_hizmetleri():
    st.title("📞 Müşteri Hizmetleri & Notlar")
    
    with st.expander("Yeni Not Ekle", expanded=True):
        with st.form("not_form"):
            konu = st.text_input("Konu")
            not_icerik = st.text_area("Notunuz")
            submitted = st.form_submit_button("Kaydet")
            if submitted:
                st.success("Not sisteme kaydedildi.")
    
    st.markdown("### Son Kayıtlar")
    st.table(pd.DataFrame({
        'Tarih': ['05.12.2024', '04.12.2024'],
        'Personel': ['Ahmet Y.', 'Mehmet K.'],
        'Konu': ['VIP Kombine İadesi', 'Passolig Sorunu'],
        'Durum': ['Çözüldü', 'Beklemede']
    }))

# -------------------------------------------------------------------------
# 6. ANA NAVİGASYON (Sidebar ve Sayfa Yönlendirme)
# -------------------------------------------------------------------------

# Sidebar Logo ve Başlık
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Besiktas_jk.svg/240px-Besiktas_jk.svg.png", width=120)
    st.markdown("### BJK Bilet Departmanı")
    st.markdown(f"👤 **Aktif Kullanıcı:**\n{st.session_state.get('email_to_verify', 'Personel')}")
    st.markdown("---")
    
    # Menü Seçimi
    selected_page = st.radio(
        "MENÜ", 
        ["Ana Sayfa", "Bilet Rapor Sistemi", "Stadyum Planı", "Müşteri Hizmetleri"],
        index=0
    )
    
    st.markdown("---")
    if st.button("🚪 Güvenli Çıkış"):
        st.session_state["logged_in"] = False
        st.session_state["login_step"] = "email"
        st.rerun()

# Sayfa Yönlendirme Mantığı
if selected_page == "Ana Sayfa":
    page_dashboard()
elif selected_page == "Bilet Rapor Sistemi":
    page_bilet_analiz()
elif selected_page == "Stadyum Planı":
    page_stadyum_plani()
elif selected_page == "Müşteri Hizmetleri":
    page_musteri_hizmetleri()