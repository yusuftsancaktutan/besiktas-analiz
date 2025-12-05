import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import smtplib
from email.message import EmailMessage
import random
import time
from io import BytesIO
import datetime

# --- 1. SAYFA KONFİGÜRASYONU ---
st.set_page_config(
    page_title="BJK Bilet Operasyon Merkezi",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. PREMIUM CSS (REACT TASARIMINDAN PORT EDİLDİ) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;600;700&display=swap');

        /* GENEL SAYFA AYARLARI */
        .stApp {
            background-color: #000000;
            background-image: linear-gradient(135deg, #111 0%, #222 100%);
            font-family: 'Segoe UI', sans-serif;
            color: #eee;
        }
        
        /* SCROLLBAR */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #111; }
        ::-webkit-scrollbar-thumb { background: #444; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #d91a2a; }

        /* SIDEBAR TASARIMI */
        [data-testid="stSidebar"] {
            background-image: linear-gradient(180deg, #000 0%, #111 100%);
            border-right: 1px solid #333;
        }
        [data-testid="stSidebar"] * { color: #ccc !important; }
        
        /* CARD GLASS EFFECT (React Kodundan) */
        .card-glass {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            transition: transform 0.2s, border-color 0.2s;
        }
        .card-glass:hover {
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.2);
        }

        /* METRİKLER */
        [data-testid="stMetricValue"] {
            color: #ffffff !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
        }
        [data-testid="stMetricLabel"] {
            color: #888 !important;
            font-size: 0.85rem !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* BUTONLAR */
        .stButton > button {
            background: linear-gradient(45deg, #d91a2a, #b30000);
            color: white !important;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
            width: 100%;
        }
        .stButton > button:hover {
            box-shadow: 0 0 15px rgba(217, 26, 42, 0.5);
            transform: scale(1.02);
        }
        
        /* TABLO */
        [data-testid="stDataFrame"] {
            background-color: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 10px;
        }

        /* CUSTOM BADGES */
        .status-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .status-pending { background: #333; color: #aaa; border: 1px solid #444; }
        .status-success { background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); }
        
        /* MENÜ */
        .stRadio label {
            background: transparent;
            padding: 10px;
            border-radius: 8px;
            transition: 0.2s;
        }
        .stRadio label:hover {
            background: rgba(255,255,255,0.05);
            color: #d91a2a !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. VERİ YAPILARI & STATE YÖNETİMİ ---

# Fikstür Verisi (React Kodundan)
INITIAL_MATCHES = [
    { "id": 'm1', "opponent": 'Antalyaspor', "date": '2024-08-18', "league": 'Süper Lig', "score": '4-2' },
    { "id": 'm2', "opponent": 'Lugano', "date": '2024-08-29', "league": 'UEFA Avrupa Ligi', "score": '5-1' },
    { "id": 'm3', "opponent": 'Sivasspor', "date": '2024-09-01', "league": 'Süper Lig', "score": '2-0' },
    { "id": 'm4', "opponent": 'Eyüpspor', "date": '2024-09-22', "league": 'Süper Lig', "score": '2-1' },
    { "id": 'm5', "opponent": 'Eintracht Frankfurt', "date": '2024-10-03', "league": 'UEFA Avrupa Ligi', "score": '1-3' },
    { "id": 'm6', "opponent": 'Konyaspor', "date": '2024-10-20', "league": 'Süper Lig', "score": '2-0' },
    { "id": 'm7', "opponent": 'Kasımpaşa', "date": '2024-11-02', "league": 'Süper Lig', "score": '1-3' },
    { "id": 'm8', "opponent": 'Malmö', "date": '2024-11-06', "league": 'UEFA Avrupa Ligi', "score": '2-1' },
    { "id": 'm9', "opponent": 'Göztepe', "date": '2024-11-24', "league": 'Süper Lig', "score": '-' },
    { "id": 'm10', "opponent": 'Maccabi Tel Aviv', "date": '2024-11-28', "league": 'UEFA Avrupa Ligi', "score": '-' },
    { "id": 'm11', "opponent": 'Fenerbahçe', "date": '2024-12-07', "league": 'Süper Lig', "score": '-' },
]

if 'matches' not in st.session_state:
    st.session_state['matches'] = INITIAL_MATCHES

# Raporları Saklamak İçin (ID bazlı)
if 'reports' not in st.session_state:
    st.session_state['reports'] = {} 

if 'selected_match_id' not in st.session_state:
    st.session_state['selected_match_id'] = None

# --- 4. YARDIMCI FONKSİYONLAR ---

def format_currency(value):
    return f"₺{value:,.0f}"

def process_data(file):
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, header=None)
        else:
            df = pd.read_excel(file, header=None)
        
        # Başlık satırını bul
        header_index = -1
        for i, row in df.head(20).iterrows(): 
            row_str = row.astype(str).str.lower().to_string()
            if "maç" in row_str or "tribün" in row_str or "tribun" in row_str:
                header_index = i
                break
        
        if header_index == -1:
            st.error("❌ Dosyada uygun başlık satırı bulunamadı.")
            return None

        df.columns = df.iloc[header_index]
        df = df[header_index + 1:].reset_index(drop=True)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Kolon Eşleştirme (Otomatik Algılama)
        cols = df.columns
        # Genellikle: [..., Tribün, Sayı] veya [Kategori, ..., Adet, Tutar]
        # React kodundaki mantık: Kategori (Col 0), Adet (Col 10) gibi. Biz burada esnek olalım.
        
        # Basit Eşleştirme Denemesi
        target_cols = {'Mac': None, 'Tribun': None, 'Adet': None, 'Tutar': None}
        
        # Eğer 'Adet' veya 'Satılan' kolonu varsa
        for c in cols:
            cl = c.lower()
            if 'adet' in cl or 'sayı' in cl or 'satılan' in cl: target_cols['Adet'] = c
            elif 'tribün' in cl or 'kategori' in cl or 'blok' in cl: target_cols['Tribun'] = c
            elif 'maç' in cl or 'organizasyon' in cl: target_cols['Mac'] = c
            elif 'tutar' in cl or 'bedel' in cl or 'hasılat' in cl: target_cols['Tutar'] = c

        # Eğer bulamazsa pozisyona göre (Son kolonlar genelde sayıdır)
        if not target_cols['Adet'] and len(cols) >= 3:
             target_cols['Adet'] = cols[-1]
             target_cols['Tribun'] = cols[-2]
             target_cols['Mac'] = cols[0]

        if not target_cols['Adet'] or not target_cols['Tribun']:
             st.error("Gerekli kolonlar (Tribün, Adet) bulunamadı.")
             return None

        df_clean = df.rename(columns={
            target_cols['Mac']: 'Mac',
            target_cols['Tribun']: 'Tribun',
            target_cols['Adet']: 'Adet',
            target_cols.get('Tutar', 'Yok'): 'Tutar'
        })
        
        # Sayısal Temizlik
        df_clean['Adet'] = pd.to_numeric(df_clean['Adet'], errors='coerce').fillna(0)
        if 'Tutar' in df_clean.columns:
             df_clean['Tutar'] = pd.to_numeric(df_clean['Tutar'], errors='coerce').fillna(0)
        else:
             df_clean['Tutar'] = 0 # Tutar yoksa 0

        # Toplam satırlarını at
        if 'Mac' in df_clean.columns:
             df_clean = df_clean[~df_clean['Mac'].astype(str).str.contains('Toplam', case=False, na=False)]
        
        return df_clean

    except Exception as e:
        st.error(f"Dosya okuma hatası: {e}")
        return None

# --- 5. GÜVENLİK (Basitleştirilmiş) ---
def check_login():
    if st.session_state.get("logged_in", False):
        return True
    
    # Giriş Ekranı
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="card-glass" style="text-align:center; padding: 40px; border-top: 4px solid #d91a2a;">
            <div style="width:80px; height:80px; background:white; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; margin-bottom:20px; box-shadow:0 0 20px rgba(255,255,255,0.2);">
                <span style="font-size:24px; font-weight:900; color:black;">BJK</span>
            </div>
            <h2 style="color:white; margin-bottom:5px;">PERSONEL GİRİŞİ</h2>
            <p style="color:#888; font-size:0.9rem; margin-bottom:30px;">Bilet Operasyon Merkezi</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login"):
            email = st.text_input("Kurumsal E-Posta", placeholder="ad.soyad@bjk.com.tr")
            pw = st.text_input("Şifre", type="password")
            if st.form_submit_button("GİRİŞ YAP"):
                # Demo Girişi (Herhangi bir BJK maili ve doğru şifre)
                if email.endswith("@bjk.com.tr") and pw == st.secrets.get("password", "1903"):
                    st.session_state["logged_in"] = True
                    st.session_state["user_email"] = email
                    st.rerun()
                else:
                    st.error("Hatalı e-posta veya şifre!")
    return False

if not check_login():
    st.stop()

# -------------------------------------------------------------------------
# 6. SAYFA MODÜLLERİ
# -------------------------------------------------------------------------

# --- MAÇ LİSTESİ MODÜLÜ ---
def module_match_list():
    st.markdown("## 📅 Fikstür ve Raporlar")
    
    # Maç Kartları Grid
    cols = st.columns(3)
    for i, match in enumerate(st.session_state['matches']):
        has_report = match['id'] in st.session_state['reports']
        col = cols[i % 3]
        
        with col:
            # HTML Kart Tasarımı
            border_color = "#10B981" if has_report else "#444"
            status_html = f'<span class="status-badge status-success">ANALİZ HAZIR</span>' if has_report else '<span class="status-badge status-pending">RAPOR BEKLENİYOR</span>'
            
            # Kart Tıklama Yerine Buton Kullanımı (Streamlit Kısıtı)
            st.markdown(f"""
            <div class="card-glass" style="border-left: 4px solid {border_color}; position:relative;">
                <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                    <span style="font-size:0.7rem; color:#888; font-weight:bold;">{match['league'].upper()}</span>
                    {status_html}
                </div>
                <h3 style="margin:0; color:white;">{match['opponent']}</h3>
                <p style="color:#aaa; font-size:0.9rem;">{match['date']}</p>
                <div style="margin-top:15px; font-size:0.8rem; color:#666;">
                    {match.get('score') or 'Skor Girilmedi'}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"{'Raporu İncele' if has_report else 'Rapor Yükle'}", key=f"btn_{match['id']}"):
                st.session_state['selected_match_id'] = match['id']
                st.rerun()

# --- RAPOR DETAY MODÜLÜ ---
def module_report_detail():
    match_id = st.session_state['selected_match_id']
    match = next((m for m in st.session_state['matches'] if m['id'] == match_id), None)
    
    if not match:
        st.error("Maç bulunamadı.")
        return

    # Header
    c1, c2 = st.columns([1, 5])
    with c1:
        if st.button("← Geri Dön"):
            st.session_state['selected_match_id'] = None
            st.rerun()
    with c2:
        st.markdown(f"## 📊 {match['opponent']} - Maç Analizi")

    # Rapor Var mı?
    if match_id in st.session_state['reports']:
        df = st.session_state['reports'][match_id]
        
        # KPI Kartları
        total_tickets = df['Adet'].sum()
        total_revenue = df['Tutar'].sum()
        top_tribune = df.loc[df['Adet'].idxmax()]
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Toplam Bilet", f"{total_tickets:,.0f}")
        k2.metric("Toplam Hasılat", format_currency(total_revenue))
        k3.metric("En Dolu Blok", f"{top_tribune['Tribun']}", f"{top_tribune['Adet']:,.0f} Adet")
        
        st.markdown("---")
        
        # Grafikler
        g1, g2 = st.columns([2, 1])
        with g1:
            st.markdown("#### 🎫 Blok Bazlı Dağılım")
            fig = px.bar(df.sort_values('Adet', ascending=False).head(15), 
                         x='Tribun', y='Adet', text_auto='.2s',
                         color='Adet', color_continuous_scale=['#333', '#d91a2a'])
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400)
            st.plotly_chart(fig, use_container_width=True)
            
        with g2:
            st.markdown("#### 💰 Hasılat Payı")
            fig_pie = px.pie(df.head(10), values='Tutar', names='Tribun', hole=0.4,
                             color_discrete_sequence=px.colors.sequential.RdBu)
            fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', showlegend=False, height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        # Veri Tablosu
        with st.expander("Detaylı Veri Listesi"):
            st.dataframe(df, use_container_width=True)
            
        # Silme Butonu
        if st.button("🗑️ Raporu Sil", type="primary"):
            del st.session_state['reports'][match_id]
            st.rerun()
            
    else:
        # Rapor Yükleme Ekranı
        st.info(f"{match['opponent']} maçı için henüz rapor yüklenmemiş.")
        
        uploaded_file = st.file_uploader("Passolig Raporunu Yükle (Excel/CSV)", type=['xlsx', 'xls', 'csv'])
        if uploaded_file:
            with st.spinner("Dosya işleniyor..."):
                time.sleep(1)
                df = process_data(uploaded_file)
                if df is not None:
                    st.session_state['reports'][match_id] = df
                    st.success("Rapor başarıyla yüklendi!")
                    st.rerun()

# --- STADYUM PLANI MODÜLÜ ---
def module_stadium():
    st.markdown("## 🏟️ Stadyum Blok Planı")
    st.markdown("Aşağıdaki harita, stadyum bloklarını ve (varsa) son yüklenen raporun doluluk durumunu gösterir.")
    
    # Son yüklenen raporu bul (Referans için)
    last_df = None
    if st.session_state['reports']:
        last_match_id = list(st.session_state['reports'].keys())[-1]
        last_df = st.session_state['reports'][last_match_id]
        st.caption(f"Veri Kaynağı: Son yüklenen maç raporu")

    # Koordinat Haritası (React kodundaki pozisyonlara benzer)
    # Basit bir Scatter Mapbox veya Plotly Scatter ile stadyum şekli çiziyoruz
    
    fig = go.Figure()

    # Saha (Ortada)
    fig.add_trace(go.Scatter(
        x=[0], y=[0], mode='text', text=['SAHA'],
        textfont=dict(color='white', size=20, weight='bold')
    ))
    
    # Blok Koordinatları (Temsili - React kodundakine benzer yerleşim)
    # Kuzey (Üst) - Güney (Alt) - Doğu (Sağ) - Batı (Sol)
    
    blocks = [
        # Batı (VIP) - Sol
        {'x': -3, 'y': 0, 'name': 'VIP 100', 'color': '#FFD700'},
        {'x': -3, 'y': 1, 'name': '101', 'color': '#333'},
        {'x': -3, 'y': -1, 'name': '102', 'color': '#333'},
        
        # Doğu - Sağ
        {'x': 3, 'y': 0, 'name': '415', 'color': '#d91a2a'},
        {'x': 3, 'y': 1, 'name': '416', 'color': '#d91a2a'},
        {'x': 3, 'y': -1, 'name': '414', 'color': '#d91a2a'},
        
        # Kuzey - Üst
        {'x': 0, 'y': 3, 'name': '408', 'color': '#444'},
        {'x': 1, 'y': 3, 'name': '409', 'color': '#444'},
        {'x': -1, 'y': 3, 'name': '407', 'color': '#444'},
        
        # Güney - Alt
        {'x': 0, 'y': -3, 'name': '422', 'color': '#444'},
        {'x': 1, 'y': -3, 'name': '423', 'color': '#444'},
        {'x': -1, 'y': -3, 'name': '421', 'color': '#444'},
    ]
    
    # Blokları Çiz
    for blk in blocks:
        # Eğer veri varsa rengi doluluğa göre ayarla (Burada sabit renk örnekli)
        fig.add_trace(go.Scatter(
            x=[blk['x']], y=[blk['y']],
            mode='markers+text',
            marker=dict(symbol='square', size=60, color=blk['color'], line=dict(width=2, color='white')),
            text=[blk['name']],
            textfont=dict(color='white'),
            hoverinfo='text',
            hovertext=f"Blok: {blk['name']}"
        ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False, visible=False, range=[-5, 5]),
        yaxis=dict(showgrid=False, zeroline=False, visible=False, range=[-5, 5]),
        height=600,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="card-glass">
        <h4>ℹ️ Blok Bilgileri</h4>
        <ul>
            <li><b>Doğu Tribünü:</b> Maraton (413-418)</li>
            <li><b>Batı Tribünü:</b> VIP ve Basın (100-126)</li>
            <li><b>Kuzey/Güney:</b> Kale Arkaları (404-412 / 419-427)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------------------
# 7. ANA NAVİGASYON VE SIDEBAR
# -------------------------------------------------------------------------

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Besiktas_jk.svg/240px-Besiktas_jk.svg.png", width=120)
    st.markdown("<br>", unsafe_allow_html=True)
    
    user = st.session_state.get('user_email', 'Misafir')
    st.markdown(f"""
    <div style='padding:10px; background:rgba(255,255,255,0.05); border-radius:8px; border-left:3px solid #d91a2a;'>
        <small style='color:#888'>Kullanıcı:</small><br>
        <b style='color:#fff'>{user}</b>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    menu = st.radio("MENÜ", ["Fikstür & Raporlar", "Stadyum Planı", "Ayarlar"], label_visibility="collapsed")
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("ÇIKIŞ"):
        st.session_state["logged_in"] = False
        st.rerun()

# SAYFA YÖNLENDİRME
if st.session_state['selected_match_id']:
    module_report_detail() # Detay görünümü aktifse onu göster
else:
    if menu == "Fikstür & Raporlar":
        module_match_list()
    elif menu == "Stadyum Planı":
        module_stadium()
    else:
        st.markdown("## ⚙️ Ayarlar")
        st.info("Kullanıcı yönetimi ve sistem ayarları bu alanda yer alacaktır.")