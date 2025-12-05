import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import random
import datetime

# --- 1. SAYFA KONFİGÜRASYONU ---
st.set_page_config(
    page_title="Beşiktaş JK - Bilet Operasyon Merkezi",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS & TASARIM (React Kodundan Port Edildi) ---
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
        
        /* SIDEBAR */
        [data-testid="stSidebar"] {
            background-image: linear-gradient(180deg, #000 0%, #111 100%);
            border-right: 1px solid #333;
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
            color: #ccc !important;
        }

        /* CARD GLASS EFFECT */
        .card-glass {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            transition: transform 0.2s;
        }
        .card-glass:hover {
            border-color: rgba(255, 255, 255, 0.2);
        }

        /* METRİKLER */
        div[data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: #ffffff !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.85rem !important;
            color: #888 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* BUTONLAR (Kırmızı Gradient) */
        .stButton > button {
            background: linear-gradient(45deg, #d91a2a, #b30000);
            color: white !important;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
        }
        .stButton > button:hover {
            box-shadow: 0 0 15px rgba(217, 26, 42, 0.5);
            transform: scale(1.02);
        }
        
        /* SECONDARY BUTONLAR */
        .stButton > button[kind="secondary"] {
            background: transparent;
            border: 1px solid #555;
            color: #aaa !important;
        }
        .stButton > button[kind="secondary"]:hover {
            border-color: white;
            color: white !important;
        }

        /* TABLOLAR */
        [data-testid="stDataFrame"] {
            background-color: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.1);
        }

        /* STATUS BADGES */
        .badge-success {
            background-color: rgba(16, 185, 129, 0.2);
            color: #34D399;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: bold;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        .badge-pending {
            background-color: rgba(107, 114, 128, 0.2);
            color: #9CA3AF;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: bold;
            border: 1px solid rgba(107, 114, 128, 0.3);
        }
        
        /* MENÜ */
        .stRadio > div { background: transparent; }
        .stRadio label {
            padding: 10px 15px;
            border-radius: 8px;
            transition: 0.2s;
            margin-bottom: 5px;
            color: #aaa !important;
        }
        .stRadio label:hover {
            background: rgba(255,255,255,0.05);
            color: #fff !important;
        }
        /* Seçili Olan */
        .stRadio div[aria-checked="true"] + div {
            color: #d91a2a !important;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. VERİ VE SABİTLER ---

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

# VIP Blok Planları (React Kodundan)
PLANS = {
    "427": { "name": "427", "rowsStartNumber": 1, "rows": [{ "start": 1, "count": 28 }, { "start": 1, "count": 28 }, { "start": 1, "count": 27 }, { "start": 1, "count": 26 }, { "start": 1, "count": 25 }, { "start": 1, "count": 25 }, { "start": 1, "count": 25 }, { "start": 1, "count": 23 }, { "start": 1, "count": 23 }, { "start": 1, "count": 23 }, { "start": 1, "count": 23 }, { "start": 1, "count": 23 }, { "start": 1, "count": 23 }, { "start": 1, "count": 23 }, { "start": 1, "count": 23 }, { "start": 1, "count": 18 }, { "start": 1, "count": 18 }] },
    "426": { "name": "426", "rowsStartNumber": 1, "rows": [{ "start": 1, "count": 19 }, { "start": 1, "count": 36 }, { "start": 1, "count": 36 }, { "start": 1, "count": 34 }, { "start": 1, "count": 32 }, { "start": 1, "count": 32 }, { "start": 1, "count": 32 }, { "start": 1, "count": 30 }, { "start": 1, "count": 30 }, { "start": 1, "count": 30 }, { "start": 1, "count": 30 }, { "start": 1, "count": 30 }, { "start": 1, "count": 30 }, { "start": 1, "count": 29 }, { "start": 1, "count": 28 }, { "start": 1, "count": 26 }, { "start": 1, "count": 26 }] },
    "100": { "name": "VIP 100", "rowsStartNumber": 4, "rows": [{ "start": 21, "count": 37 }, { "start": 21, "count": 37 }, { "start": 21, "count": 37 }, { "start": 21, "count": 37 }, { "start": 21, "count": 37 }, { "start": 20, "count": 37 }, { "start": 25, "count": 37 }, { "start": 25, "count": 37 }, { "start": 25, "count": 37 }, { "start": 25, "count": 37 }, { "start": 25, "count": 37 }, { "start": 25, "count": 37 }, { "start": 25, "count": 37 }, { "start": 25, "count": 37 }, { "start": 25, "count": 37 }, { "start": 25, "count": 37 }, { "start": 25, "count": 37 }, { "start": 25, "count": 37 }, { "start": 25, "count": 37 }, { "start": 25, "count": 37 }] },
    "113": { "name": "113", "rowsStartNumber": 1, "rows": [{ "start": 1, "count": 18 }, { "start": 1, "count": 15 }, { "start": 1, "count": 15 }, { "start": 1, "count": 15 }, { "start": 1, "count": 15 }, { "start": 1, "count": 15 }, { "start": 1, "count": 14 }, { "start": 1, "count": 20 }, { "start": 1, "count": 20 }, { "start": 1, "count": 20 }, { "start": 1, "count": 20 }, { "start": 1, "count": 20 }, { "start": 1, "count": 20 }, { "start": 1, "count": 20 }, { "start": 1, "count": 20 }, { "start": 1, "count": 20 }, { "start": 1, "count": 20 }, { "start": 1, "count": 20 }, { "start": 1, "count": 20 }, { "start": 1, "count": 20 }, { "start": 1, "count": 20 }, { "start": 1, "count": 20 }, { "start": 1, "count": 20 }, { "start": 1, "count": 20 }] },
}

CATEGORY_MAPPINGS = {
    "1. Kategori": "115-116 VIP", "2. Kategori": "101-126 DOĞU ÜST", "3. Kategori": "103-124", 
    "4. Kategori": "102-125", "5. Kategori": "114-117", "6. Kategori": "3. Kategori", 
    "10. Kategori": "VIP100"
}

# Session State Başlatma
if 'matches' not in st.session_state: st.session_state['matches'] = INITIAL_MATCHES
if 'reports' not in st.session_state: st.session_state['reports'] = {} 
if 'seats' not in st.session_state: st.session_state['seats'] = {} # Koltuk durumu
if 'selected_match_id' not in st.session_state: st.session_state['selected_match_id'] = None

# --- 4. EXCEL İŞLEME (React Mantığına Göre) ---
def process_excel_report(file):
    try:
        # Excel'i oku (Header yok, koordinatla çalışacağız)
        df = pd.read_excel(file, header=None)
        
        # 1. Hasılat Verileri (Özel Hücreler: C116, C120, C122 vb.)
        # Pandas 0-indexed, Excel 1-indexed. C116 -> Row 115, Col 2
        try:
            val_c116 = float(df.iloc[115, 2]) if pd.notnull(df.iloc[115, 2]) else 0
            val_c120 = float(df.iloc[119, 2]) if pd.notnull(df.iloc[119, 2]) else 0
            val_c122 = float(df.iloc[121, 2]) if pd.notnull(df.iloc[121, 2]) else 0
            net_income = val_c116 - val_c120 - val_c122
        except:
            net_income = 0

        # 2. Fiyat Listesi (A12:B25 Aralığı)
        # React kodundaki range: { s: { c: 0, r: 11 }, e: { c: 1, r: 24 } }
        price_map = {}
        try:
            price_df = df.iloc[11:25, 0:2] # Rows 11-24, Cols A-B
            for _, row in price_df.iterrows():
                cat = str(row[0]).split('-')[0].strip()
                price = float(row[1]) if pd.notnull(row[1]) else 0
                if cat and price > 0:
                    price_map[cat] = price
        except:
            pass

        # 3. Satış Verileri (A45:K58 Aralığı)
        # React: { s: { c: 0, r: 44 }, e: { c: 10, r: 57 } }
        sales_data = []
        try:
            sales_df = df.iloc[44:58, 0:11] # Rows 44-57, Cols A-K (K is index 10)
            
            for _, row in sales_df.iterrows():
                raw_cat = str(row[0])
                if "Toplam" in raw_cat or pd.isna(raw_cat): continue
                
                base_cat = raw_cat.split('-')[0].strip()
                display_cat = CATEGORY_MAPPINGS.get(base_cat, base_cat)
                
                price = price_map.get(base_cat, 0)
                sold_count = float(row[10]) if pd.notnull(row[10]) else 0 # K sütunu (Index 10)
                
                if sold_count > 0:
                    sales_data.append({
                        'category': display_cat,
                        'price': price,
                        'sold': int(sold_count),
                        'gross_revenue': sold_count * price
                    })
        except:
            st.warning("Tablo aralığı okunamadı, standart formatta olmayabilir.")

        result_df = pd.DataFrame(sales_data)
        return result_df, net_income

    except Exception as e:
        st.error(f"Hata: {e}")
        return None, 0

def format_currency(val):
    return f"₺{val:,.0f}"

# --- 5. ANA SAYFA MODÜLLERİ ---

def module_dashboard():
    # Header
    st.markdown("""
    <div style='background: #111; padding: 20px; border-radius: 12px; border-left: 5px solid #d91a2a; margin-bottom: 20px;'>
        <h2 style='margin:0; color:white;'>🦅 Bilet Operasyon Merkezi</h2>
        <p style='margin:0; color:#888;'>Hoş geldiniz, Admin.</p>
    </div>
    """, unsafe_allow_html=True)

    # Maç Listesi (Kartlar)
    st.markdown("### 📅 Fikstür ve Rapor Durumu")
    
    cols = st.columns(3)
    for i, match in enumerate(st.session_state['matches']):
        has_report = match['id'] in st.session_state['reports']
        col = cols[i % 3]
        
        with col:
            # Durum Rozeti
            badge_html = f'<span class="badge-success">ANALİZ HAZIR</span>' if has_report else '<span class="badge-pending">RAPOR YOK</span>'
            border_color = "#10B981" if has_report else "#333"
            
            # HTML Kart
            st.markdown(f"""
            <div class="card-glass" style="border-left: 4px solid {border_color}; min-height: 160px; position:relative;">
                <div style="display:flex; justify-content:space-between;">
                    <span style="color:#666; font-size:0.75rem; font-weight:bold;">{match['league'].upper()}</span>
                    {badge_html}
                </div>
                <h3 style="margin-top:10px; margin-bottom:5px; color:white; font-size:1.3rem;">{match['opponent']}</h3>
                <p style="color:#aaa; font-size:0.9rem;">{match['date']}</p>
                <div style="position:absolute; bottom:20px; right:20px; font-size:1.5rem; font-weight:bold; color:#333;">
                    {match['score']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Aksiyon Butonu
            btn_text = "Raporu İncele" if has_report else "Rapor Yükle"
            if st.button(btn_text, key=match['id']):
                st.session_state['selected_match_id'] = match['id']
                st.rerun()

def module_report_detail():
    match_id = st.session_state['selected_match_id']
    match = next((m for m in st.session_state['matches'] if m['id'] == match_id), None)
    
    if not match: st.error("Hata"); return

    # Üst Bar
    c1, c2 = st.columns([1, 6])
    with c1:
        if st.button("← Geri"):
            st.session_state['selected_match_id'] = None
            st.rerun()
    with c2:
        st.markdown(f"## {match['opponent']} - Rapor Detayı")

    # Veri Var mı?
    if match_id in st.session_state['reports']:
        data = st.session_state['reports'][match_id]
        df = data['df']
        net_income = data['net_income']
        
        # React'taki KPI Kartları
        total_rev = df['gross_revenue'].sum()
        total_sold = df['sold'].sum()
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Toplam Hasılat (Brüt)", format_currency(total_rev))
        k2.metric("Net Gelir (Tahmini)", format_currency(net_income), delta="Passo kesintisi hariç")
        k3.metric("Satılan Bilet", f"{total_sold:,.0f}")
        
        st.markdown("---")
        
        # Grafikler
        g1, g2 = st.columns([2, 1])
        with g1:
            st.markdown("#### Hasılat Dağılımı")
            fig_bar = px.bar(df, x='category', y='gross_revenue', text_auto='.2s', 
                             color='gross_revenue', color_continuous_scale=['#333', '#d91a2a'])
            fig_bar.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with g2:
            st.markdown("#### Satış Adet Payı")
            fig_pie = px.pie(df, values='sold', names='category', hole=0.4,
                             color_discrete_sequence=px.colors.sequential.RdBu)
            fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        # Tablo
        st.dataframe(df, use_container_width=True)
        
        # Silme
        if st.button("Raporu Sil", type="primary"):
            del st.session_state['reports'][match_id]
            st.rerun()

    else:
        # Upload Ekranı (React tarzı)
        st.info("Bu maç için henüz rapor yüklenmedi.")
        
        # Dropzone benzeri alan
        uploaded_file = st.file_uploader("Passolig Raporunu (.xlsx) Buraya Sürükleyin", type=['xlsx', 'xls'])
        
        if uploaded_file:
            df, income = process_excel_report(uploaded_file)
            if df is not None and not df.empty:
                st.session_state['reports'][match_id] = {'df': df, 'net_income': income}
                st.success("Rapor işlendi!")
                st.rerun()

def module_stadium_vip():
    st.markdown("## 🏟️ VIP Tribün Yönetimi")
    
    # 2 Görünüm: Genel Plan veya Blok Detayı
    if 'selected_block' not in st.session_state:
        # --- GÖRÜNÜM 1: STADYUM PLANI (React Koordinatlarıyla) ---
        st.markdown("İşlem yapmak istediğiniz bloğu haritadan seçiniz.")
        
        # Plotly ile İnteraktif Harita
        # React kodundaki 'top' ve 'left' değerlerini X/Y koordinatına çeviriyoruz.
        # React: top (Y ekseni ters), left (X ekseni). width=1000, height=700.
        
        blocks = [
            {'id': '112', 'x': 220, 'y': 700-145}, {'id': '113', 'x': 270, 'y': 700-145}, 
            {'id': '114', 'x': 340, 'y': 700-145}, {'id': '115', 'x': 444, 'y': 700-145},
            {'id': 'VIP 100', 'x': 480, 'y': 700-550}, # VIP 100 Örneği
            {'id': '426', 'x': 830, 'y': 700-590}, # 426 Örneği
            {'id': '427', 'x': 780, 'y': 700-630}, # 427 Örneği
        ]
        
        # Hızlıca tüm React koordinatlarını eklemek yerine örnek set kullanıyoruz
        # Kullanıcı '427', '426', '100', '113' bloklarını tanımlamış.
        selectable_blocks = ['427', '426', '100', '113']
        
        fig = go.Figure()
        
        # Saha
        fig.add_trace(go.Scatter(x=[500], y=[350], mode='text', text=['SAHA'], textfont=dict(size=30, color='rgba(255,255,255,0.2)')))
        
        # Bloklar
        for b in blocks:
            color = '#d91a2a' if b['id'].replace('VIP ', '') in selectable_blocks else '#333'
            fig.add_trace(go.Scatter(
                x=[b['x']], y=[b['y']],
                mode='markers+text',
                marker=dict(symbol='square', size=40, color=color, line=dict(width=1, color='white')),
                text=[b['id']],
                textfont=dict(color='white', size=10),
                hoverinfo='text',
                hovertext=f"Blok: {b['id']}",
                name=b['id']
            ))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(20,20,20,1)',
            xaxis=dict(range=[0, 1000], showgrid=False, visible=False),
            yaxis=dict(range=[0, 700], showgrid=False, visible=False),
            height=600,
            showlegend=False,
            clickmode='event+select'
        )
        
        # Blok Seçimi (Selectbox ile simüle ediyoruz çünkü Plotly click event Streamlit'te bazen gecikmeli)
        col_sel, col_map = st.columns([1, 3])
        with col_sel:
            st.info("Harita üzerindeki kırmızı bloklar yönetilebilir.")
            sel = st.selectbox("Blok Seçiniz:", selectable_blocks)
            if st.button("Bloğa Git"):
                st.session_state['selected_block'] = sel
                st.rerun()
        
        with col_map:
            st.plotly_chart(fig, use_container_width=True)

    else:
        # --- GÖRÜNÜM 2: BLOK DETAYI & KOLTUKLAR ---
        block_id = st.session_state['selected_block']
        plan = PLANS.get(block_id)
        
        # Header
        hb1, hb2 = st.columns([1, 6])
        with hb1:
            if st.button("← Haritaya Dön"):
                del st.session_state['selected_block']
                st.rerun()
        with hb2:
            st.markdown(f"## Blok {block_id} - Koltuk Planı")

        if not plan:
            st.error("Plan verisi bulunamadı.")
            return

        # Koltuk Haritasını Çiz (Plotly Scatter ile)
        # React'taki "Row" ve "Count" mantığını X,Y koordinatına döküyoruz.
        seat_x = []
        seat_y = []
        seat_text = []
        seat_colors = []
        
        # Kayıtlı koltukları al
        saved_seats = st.session_state['seats'].get(block_id, {})

        rows = plan['rows'] # [{start:1, count:28}, ...]
        start_row_num = plan['rowsStartNumber'] # 1
        
        # Y ekseni: Sıra numarası (Ters sıra ile gelir genelde stadyumlarda, saha aşağıdadır)
        # React kodunda: rowNo = start + (length - 1 - i) -> Üstten alta çiziyor.
        
        for i, row_data in enumerate(rows):
            row_num = start_row_num + (len(rows) - 1 - i)
            count = row_data['count']
            start_seat = row_data['start']
            
            # Hizalama (Basitçe ortalayalım)
            x_offset = (50 - count) / 2 # 50 varsayılan genişlik
            
            for j in range(count):
                seat_num = start_seat + j
                seat_key = f"{row_num}-{seat_num}"
                
                seat_x.append(x_offset + j)
                seat_y.append(row_num)
                seat_text.append(f"Sıra:{row_num} No:{seat_num}")
                
                # Renk (Dolu mu boş mu)
                if seat_key in saved_seats:
                    seat_colors.append("#FACC15") # Sarı (Dolu/Kombine)
                else:
                    seat_colors.append("#ffffff") # Beyaz (Boş)

        fig_seats = go.Figure(data=go.Scatter(
            x=seat_x, y=seat_y,
            mode='markers',
            marker=dict(size=12, color=seat_colors, line=dict(width=1, color='#333')),
            text=seat_text,
            hoverinfo='text'
        ))
        
        fig_seats.update_layout(
            title="SAHA BU TARAFTA ↓",
            title_x=0.5,
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, visible=False),
            yaxis=dict(showgrid=False, title="Sıra Numarası"),
            height=600,
            hovermode='closest'
        )
        
        c_map, c_panel = st.columns([3, 1])
        
        with c_map:
            st.plotly_chart(fig_seats, use_container_width=True)
            
        with c_panel:
            st.markdown("### 💺 Koltuk Yönetimi")
            st.info("Grafik üzerinde koltukların durumunu görebilirsiniz.")
            
            with st.form("seat_assign"):
                st.write("Koltuk Ata / Düzenle")
                r_num = st.number_input("Sıra No", min_value=1, step=1)
                s_num = st.number_input("Koltuk No", min_value=1, step=1)
                cat = st.selectbox("Kategori", ["Kombine", "Sponsor", "Boş"])
                
                if st.form_submit_button("Kaydet"):
                    k = f"{r_num}-{s_num}"
                    if block_id not in st.session_state['seats']:
                        st.session_state['seats'][block_id] = {}
                    
                    if cat == "Boş":
                        if k in st.session_state['seats'][block_id]:
                            del st.session_state['seats'][block_id][k]
                    else:
                        st.session_state['seats'][block_id][k] = cat
                    st.success("Güncellendi!")
                    st.rerun()

# --- 6. NAVİGASYON ---

with st.sidebar:
    st.markdown("### BJK Bilet Merkezi")
    menu = st.radio("Menü", ["Fikstür & Raporlar", "VIP & Stadyum"], label_visibility="collapsed")
    st.markdown("---")
    if st.button("Çıkış Yap"):
        st.session_state['logged_in'] = False
        st.rerun()

if menu == "Fikstür & Raporlar":
    if st.session_state['selected_match_id']:
        module_report_detail()
    else:
        module_dashboard()
elif menu == "VIP & Stadyum":
    module_stadium_vip()