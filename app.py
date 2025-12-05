import streamlit as st
import pandas as pd
import plotly.express as px

# --- Sayfa Ayarları ---
st.set_page_config(
    page_title="BJK Bilet Analiz",
    page_icon="🦅",
    layout="wide"
)

# --- Özel CSS (Beşiktaş Teması) ---
st.markdown("""
    <style>
        .block-container {padding-top: 1rem;}
        div[data-testid="stMetricValue"] {color: #E30613; font-weight: bold;}
        .stButton>button {
            background-color: #E30613;
            color: white;
            border-radius: 8px;
            width: 100%;
        }
        .css-1d391kg {padding-top: 1rem;}
    </style>
""", unsafe_allow_html=True)

# --- Başlık ---
col_logo, col_title = st.columns([1, 8])
with col_logo:
    # Beşiktaş Logosu (Wikimedia'dan)
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Besiktas_jk.svg/240px-Besiktas_jk.svg.png", width=70)
with col_title:
    st.title("BEŞİKTAŞ JK | Bilet Analiz Paneli")
    st.markdown("2024-2025 Sezonu Bedelsiz Bilet Takip Sistemi")

st.markdown("---")

# --- Sidebar: Dosya Yükleme ---
with st.sidebar:
    st.header("📂 Veri Yükleme")
    st.write("Güncel Excel veya CSV raporunu aşağıya sürükleyin.")
    uploaded_file = st.file_uploader("", type=['xlsx', 'xls', 'csv'])
    
    st.info("""
    **Sistem Nasıl Çalışır?**
    1. Rapor dosyasını yükleyin.
    2. Grafikler otomatik oluşur.
    3. Sonuçlar anlık güncellenir.
    """)

# --- Veri İşleme Fonksiyonu ---
def process_data(file):
    try:
        # Dosya tipine göre oku
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # Kolon isimlerini temizle (boşlukları sil)
        df.columns = [c.strip() for c in df.columns]
        
        # Kolonları Standartlaştır (Tahminleme)
        cols = df.columns
        # Genellikle format: Maç Adı | Tribün | Sayı
        if len(cols) >= 3:
            # Son kolon sayı, sondan bir önceki tribün, ilk kolon maç
            rename_map = {cols[-1]: 'Adet', cols[-2]: 'Tribun', cols[0]: 'Mac'}
            df.rename(columns=rename_map, inplace=True)
        
        # Sayı formatını düzelt (1.000 gibi noktaları kaldır)
        if df['Adet'].dtype == 'object':
             df['Adet'] = df['Adet'].astype(str).str.replace('.', '').str.replace(',', '.').astype(int)

        # "Toplam" satırlarını filtrele (Excel özet satırları)
        df = df[~df['Mac'].astype(str).str.contains('Toplam', case=False, na=False)]
        
        return df
    except Exception as e:
        st.error(f"Dosya formatı hatalı: {e}")
        return None

# --- Ana Akış ---
if uploaded_file:
    df = process_data(uploaded_file)
    
    if df is not None:
        # Özet Tablo Oluştur (Maç Bazlı Toplam)
        match_summary = df.groupby('Mac')['Adet'].sum().sort_values(ascending=False).reset_index()
        
        # KPI Hesaplamaları
        total_tickets = match_summary['Adet'].sum()
        total_matches = len(match_summary)
        top_match = match_summary.iloc[0]['Mac']
        top_match_count = match_summary.iloc[0]['Adet']

        # --- 1. Bölüm: Kartlar (KPI) ---
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Analiz Edilen Maç", f"{total_matches}")
        kpi2.metric("Toplam Yüklenen Bilet", f"{total_tickets:,.0f}".replace(',', '.'))
        kpi3.metric("Rekor Maç", f"{top_match_count:,.0f}", delta="En Yüksek")
        st.caption(f"En yüksek maç: {top_match}")

        st.markdown("---")

        # --- 2. Bölüm: Grafikler ---
        tab_genel, tab_detay = st.tabs(["📊 Genel Bakış", "🔍 Maç Detayı"])

        with tab_genel:
            col_chart1, col_chart2 = st.columns([2, 1])
            
            with col_chart1:
                st.subheader("Maç Bazlı Bilet Yoğunluğu")
                # Bar Chart
                fig_bar = px.bar(
                    match_summary, 
                    x='Mac', 
                    y='Adet',
                    text_auto='.2s',
                    color='Adet',
                    color_continuous_scale=['#333333', '#E30613'] # Siyah -> Kırmızı
                )
                fig_bar.update_layout(xaxis_title="", yaxis_title="Bilet Sayısı", height=450)
                st.plotly_chart(fig_bar, use_container_width=True)

            with col_chart2:
                st.subheader("Dağılım Özeti")
                # Pie Chart (İlk 6 maç + Diğerleri)
                if len(match_summary) > 6:
                    top_6 = match_summary.head(6)
                    others = pd.DataFrame([['Diğerleri', match_summary.iloc[6:]['Adet'].sum()]], columns=['Mac', 'Adet'])
                    pie_data = pd.concat([top_6, others])
                else:
                    pie_data = match_summary

                fig_pie = px.pie(
                    pie_data, 
                    values='Adet', 
                    names='Mac',
                    color_discrete_sequence=['#E30613', '#333333', '#555555', '#777777', '#999999', '#AAAAAA']
                )
                fig_pie.update_layout(showlegend=False, height=450)
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)

        with tab_detay:
            col_select, col_empty = st.columns([1, 2])
            with col_select:
                selected_match = st.selectbox("Detayını görmek istediğiniz maçı seçin:", match_summary['Mac'])
            
            if selected_match:
                # Seçilen maçın verisini süz
                match_detail_df = df[df['Mac'] == selected_match].groupby('Tribun')['Adet'].sum().reset_index().sort_values(by='Adet', ascending=True)
                
                det_col1, det_col2 = st.columns([1, 1])
                
                with det_col1:
                    st.markdown(f"### 🏟️ {selected_match}")
                    st.markdown("Tribün bazlı dağılım grafiği")
                    fig_tribune = px.bar(
                        match_detail_df, 
                        x='Adet', 
                        y='Tribun', 
                        orientation='h', 
                        text_auto=True,
                        color_discrete_sequence=['#333333']
                    )
                    fig_tribune.update_layout(height=500)
                    st.plotly_chart(fig_tribune, use_container_width=True)
                
                with det_col2:
                    st.markdown("### 📋 Liste Görünümü")
                    st.dataframe(
                        match_detail_df.sort_values(by='Adet', ascending=False), 
                        use_container_width=True, 
                        hide_index=True
                    )

else:
    # Boş Durum Ekranı
    st.info("👈 Analize başlamak için lütfen sol menüden 'Dosya Yükleme' alanını kullanın.")
    st.markdown("""
        <div style='text-align: center; margin-top: 50px; opacity: 0.6;'>
            <h1>🦅</h1>
            <h3>Beşiktaş JK Veri Analiz Sistemi</h3>
            <p>Bekleniyor...</p>
        </div>
    """, unsafe_allow_html=True)