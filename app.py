import streamlit as st
import pandas as pd
import plotly.express as px
import smtplib
from email.message import EmailMessage
import random
import time
from io import BytesIO

# --- Sayfa Ayarları ---
st.set_page_config(
    page_title="BJK Bilet Analiz",
    page_icon="🦅",
    layout="wide"
)

# -------------------------------------------------------------------------
# YARDIMCI FONKSİYONLAR (Excel İndirme vb.)
# -------------------------------------------------------------------------
def convert_df_to_excel(df):
    """Dataframe'i indirilebilir Excel formatına çevirir."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Analiz')
    processed_data = output.getvalue()
    return processed_data

# -------------------------------------------------------------------------
# GÜVENLİK MODÜLÜ
# -------------------------------------------------------------------------
def send_verification_email(to_email, code):
    """Kullanıcıya doğrulama kodu gönderir."""
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
    
    Beşiktaş JK Bilet Analiz Paneli giriş kodunuz: {code}
    
    Güvenliğiniz için bu kodu paylaşmayınız.
    """)
    msg['Subject'] = 'BJK Analiz - Giriş Kodu'
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

    st.markdown("""
    <style>
        .stTextInput > div > div > input {text-align: center;}
        div[data-testid="stForm"] {border: 2px solid #E30613; padding: 30px; border-radius: 15px;}
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Besiktas_jk.svg/240px-Besiktas_jk.svg.png", width=100)
        st.markdown("<h3 style='text-align: center;'>Güvenli Giriş Paneli</h3>", unsafe_allow_html=True)

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

if not check_login():
    st.stop()

# -------------------------------------------------------------------------
# ANA UYGULAMA
# -------------------------------------------------------------------------

st.markdown("""
    <style>
        .block-container {padding-top: 1rem;}
        div[data-testid="stMetricValue"] {color: #E30613; font-weight: bold;}
        .stButton>button {background-color: #E30613; color: white; border-radius: 8px; width: 100%;}
    </style>
""", unsafe_allow_html=True)

col_title_main = st.columns([1, 8])
with col_title_main[1]:
    st.title("BEŞİKTAŞ JK | Bilet Analiz Paneli")
    st.caption("2024-2025 Sezonu Bedelsiz Bilet Takip Sistemi")

st.markdown("---")

with st.sidebar:
    st.header("📂 Veri Yükleme")
    uploaded_file = st.file_uploader("Rapor dosyasını yükleyin", type=['xlsx', 'xls', 'csv'])
    
    st.markdown("---")
    if st.button("Çıkış Yap"):
        st.session_state["logged_in"] = False
        st.session_state["login_step"] = "email"
        st.rerun()

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

if uploaded_file:
    df = process_data(uploaded_file)
    
    if df is not None:
        # Veri Hazırlığı
        match_summary = df.groupby('Mac')['Adet'].sum().sort_values(ascending=False).reset_index()
        tribune_summary = df.groupby('Tribun')['Adet'].sum().sort_values(ascending=False).reset_index()
        
        total_tickets = match_summary['Adet'].sum()
        total_matches = len(match_summary)
        top_match = match_summary.iloc[0]['Mac']
        top_match_count = match_summary.iloc[0]['Adet']

        # KPI Alanı
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Analiz Edilen Maç", f"{total_matches}")
        kpi2.metric("Toplam Yüklenen Bilet", f"{total_tickets:,.0f}".replace(',', '.'))
        kpi3.metric("Rekor Maç", f"{top_match_count:,.0f}", delta="En Yüksek")
        
        st.markdown("---")

        # Sekmeler
        tab1, tab2, tab3 = st.tabs(["📊 Genel Bakış", "🏟️ Tribün Analizi", "🔍 Maç Detayı"])

        # TAB 1: GENEL BAKIŞ
        with tab1:
            col_chart1, col_chart2 = st.columns([2, 1])
            with col_chart1:
                st.subheader("Maç Bazlı Yoğunluk")
                fig_bar = px.bar(match_summary, x='Mac', y='Adet', text_auto='.2s', color='Adet', color_continuous_scale=['#333333', '#E30613'])
                fig_bar.update_layout(xaxis_title="", yaxis_title="Bilet Sayısı", height=450)
                st.plotly_chart(fig_bar, use_container_width=True)

            with col_chart2:
                st.subheader("Veri İndir")
                st.write("Analiz sonuçlarını Excel olarak indirin.")
                
                # Excel İndirme Butonu
                excel_data = convert_df_to_excel(match_summary)
                st.download_button(
                    label="📥 Özet Tabloyu İndir (Excel)",
                    data=excel_data,
                    file_name='bjk_mac_ozeti.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                )
                
                st.markdown("---")
                st.subheader("Dağılım")
                fig_pie = px.pie(match_summary.head(8), values='Adet', names='Mac', color_discrete_sequence=px.colors.sequential.RdBu)
                fig_pie.update_layout(showlegend=False, height=300)
                fig_pie.update_traces(textposition='inside', textinfo='percent')
                st.plotly_chart(fig_pie, use_container_width=True)

        # TAB 2: TRİBÜN ANALİZİ (YENİ)
        with tab2:
            st.subheader("Sezonluk Tribün Doluluk Analizi")
            st.write("Hangi tribüne sezon boyunca toplam ne kadar bedelsiz bilet yüklenmiş?")
            
            fig_tribune_all = px.bar(tribune_summary, x='Adet', y='Tribun', orientation='h', text_auto='.2s', color='Adet', color_continuous_scale=['#E30613', '#000000'])
            fig_tribune_all.update_layout(height=600, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_tribune_all, use_container_width=True)
            
            with st.expander("Tribün Verilerini Gör"):
                st.dataframe(tribune_summary, use_container_width=True)

        # TAB 3: MAÇ DETAYI
        with tab3:
            col_select, col_dl = st.columns([2, 1])
            with col_select:
                selected_match = st.selectbox("İncelemek istediğiniz maçı seçin:", match_summary['Mac'])
            
            if selected_match:
                match_detail_df = df[df['Mac'] == selected_match].groupby('Tribun')['Adet'].sum().reset_index().sort_values(by='Adet', ascending=True)
                
                with col_dl:
                    st.write("") # Boşluk
                    st.write("") 
                    # Seçilen maçın detayını indirme butonu
                    match_excel = convert_df_to_excel(match_detail_df.sort_values(by='Adet', ascending=False))
                    st.download_button(
                        label=f"📥 {selected_match[:15]}... Detayını İndir",
                        data=match_excel,
                        file_name=f'{selected_match}_detay.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    )

                det_col1, det_col2 = st.columns([1, 1])
                with det_col1:
                    st.markdown(f"### 🏟️ {selected_match}")
                    fig_tribune = px.bar(match_detail_df, x='Adet', y='Tribun', orientation='h', text_auto=True, color_discrete_sequence=['#333333'])
                    fig_tribune.update_layout(height=500)
                    st.plotly_chart(fig_tribune, use_container_width=True)
                with det_col2:
                    st.markdown("### 📋 Liste Görünümü")
                    st.dataframe(match_detail_df.sort_values(by='Adet', ascending=False), use_container_width=True, hide_index=True)

else:
    st.info("👈 Veri yükleyerek analize başlayın.")