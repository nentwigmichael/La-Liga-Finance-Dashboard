import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE SETUP ---
st.set_page_config(page_title="LaLiga Financial Dashboard", page_icon="⚽", layout="wide", initial_sidebar_state="expanded")

# --- LALIGA CUSTOM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Outfit', sans-serif;
    }
    
    h1, h2, h3 {
        color: #FF3535 !important; /* LaLiga EA Sports Coral Red */
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    
    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 28px !important;
        font-weight: 800 !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #B0B0B0 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 12px !important;
    }
    
    .stSelectbox > div > div > div {
        background-color: #1E232B;
        color: white;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- CLUB LOGOS ---
LOGOS = {
    "Real Madrid": "https://upload.wikimedia.org/wikipedia/en/5/56/Real_Madrid_CF.svg",
    "FC Barcelona": "https://upload.wikimedia.org/wikipedia/en/4/47/FC_Barcelona_%28crest%29.svg",
    "Atlético Madrid": "https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg",
    "Valencia CF": "https://upload.wikimedia.org/wikipedia/en/c/ce/Valenciacf.svg",
    "Sevilla FC": "https://upload.wikimedia.org/wikipedia/en/3/3b/Sevilla_FC_logo.svg",
    "Villarreal CF": "https://upload.wikimedia.org/wikipedia/en/7/70/Villarreal_CF_logo.svg",
    "Athletic Bilbao": "https://upload.wikimedia.org/wikipedia/en/9/98/Club_Athletic_Bilbao_logo.svg",
    "Celta Vigo": "https://upload.wikimedia.org/wikipedia/en/1/12/RC_Celta_de_Vigo_logo.svg",
    "Real Sociedad": "https://upload.wikimedia.org/wikipedia/en/f/f1/Real_Sociedad_logo.svg",
    "Real Betis": "https://upload.wikimedia.org/wikipedia/en/1/13/Real_betis_logo.svg",
    "Getafe CF": "https://upload.wikimedia.org/wikipedia/en/4/46/Getafe_logo.svg",
    "RCD Espanyol": "https://upload.wikimedia.org/wikipedia/en/d/d6/Rcd_espanyol_logo.svg",
    "Deportivo Alavés": "https://upload.wikimedia.org/wikipedia/en/2/2e/Deportivo_Alaves_logo.svg"
}

# --- LALIGA LOGO ---
LALIGA_LOGO = "https://upload.wikimedia.org/wikipedia/commons/0/0f/LaLiga_logo_2023.svg"

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/processed/tm_processed_data.csv', sep=';')
    except FileNotFoundError:
        df = pd.read_csv('../data/processed/tm_processed_data.csv', sep=';')
    return df

df = load_data()
seasons = list(df['Season'].unique())
clubs = list(df['Club'].unique())

# --- SIDEBAR ---
st.sidebar.image(LALIGA_LOGO, width=150)
st.sidebar.title("Data Explorer")
mode = st.sidebar.radio("Ansicht wählen", ["LaLiga Übersicht", "Vereins-Analyse"])

if mode == "Vereins-Analyse":
    selected_club = st.sidebar.selectbox("Verein auswählen", clubs)
    selected_season_club = st.sidebar.selectbox("Saison auswählen", ["Alle Saisons (Trend)"] + seasons)
else:
    selected_season_liga = st.sidebar.selectbox("Saison für Liga-Vergleich", ["Alle 10 Jahre (Aggregiert)"] + seasons)

st.sidebar.markdown("---")
st.sidebar.info("Phase 1: Marktdaten\n\nPhase 2: Bilanzen (Coming Soon)")

# --- MAIN CONTENT ---
if mode == "Vereins-Analyse":
    col1, col2 = st.columns([1, 8])
    with col1:
        st.image(LOGOS.get(selected_club, ""), width=80)
    with col2:
        st.title(f"{selected_club} - Marktdaten")
    
    club_df = df[df['Club'] == selected_club].copy()
    
    if selected_season_club == "Alle Saisons (Trend)":
        latest_season = club_df.iloc[-1]
        st.subheader(f"Aktuelle KPIs (Saison {latest_season['Season']})")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Kaderwert", f"€ {latest_season['Squad_Value_TM']:,.2f}m")
        kpi2.metric("Nettotransferbilanz", f"€ {latest_season['Net_Transfer_Balance']:,.2f}m")
        kpi3.metric("Transfervolumen", f"€ {latest_season['Total_Transfer_Activity']:,.2f}m")
        kpi4.metric("Kaderwert-Wachstum YoY", f"{latest_season['YoY_Squad_Value_Growth_%']}%")
        
        st.markdown("---")
        st.subheader("10-Jahres-Trend")
        
        # Plotly layout config for LaLiga theme
        layout_cfg = dict(template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=30, b=0))
        
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=club_df['Season'], y=club_df['Squad_Value_TM'], mode='lines+markers', name='Kaderwert (€m)', line=dict(color='#FF3535', width=4)))
        fig1.update_layout(**layout_cfg, hovermode='x unified')
        st.plotly_chart(fig1, use_container_width=True)
        
        fig2 = px.bar(club_df, x='Season', y='Net_Transfer_Balance', color='Net_Transfer_Balance', 
                      color_continuous_scale=['#FF3535', 'gray', '#00E676'], labels={'Net_Transfer_Balance': 'Netto (€m)'}, title="Nettotransferbilanz")
        fig2.update_layout(**layout_cfg)
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Asset-Effizienz (Kaderwert / Transferausgaben)")
        st.caption("Ein hoher Wert deutet auf gute Jugendarbeit oder smarte Transfers hin. Lücken entstehen in Jahren mit 0€ Transferausgaben.")
        fig3 = px.line(club_df, x='Season', y='SV_to_Spend_Ratio', markers=True, line_shape='spline')
        fig3.update_traces(connectgaps=True, line_color='#00B4D8', line_width=4)
        fig3.update_layout(**layout_cfg)
        st.plotly_chart(fig3, use_container_width=True)

    else:
        season_data = club_df[club_df['Season'] == selected_season_club].iloc[0]
        st.subheader(f"KPIs für Saison {selected_season_club}")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Kaderwert", f"€ {season_data['Squad_Value_TM']:,.2f}m")
        kpi2.metric("Nettotransferbilanz", f"€ {season_data['Net_Transfer_Balance']:,.2f}m")
        kpi3.metric("Transfervolumen", f"€ {season_data['Total_Transfer_Activity']:,.2f}m")
        kpi4.metric("Kaderwert-Wachstum YoY", f"{season_data['YoY_Squad_Value_Growth_%']}%")
        
        st.markdown("---")
        st.write("Weitere Details für diese Saison (Ausgaben vs Einnahmen):")
        colA, colB = st.columns(2)
        with colA:
            st.metric("Transfer-Ausgaben", f"€ {season_data['Transfer_Expenditures']:,.2f}m")
        with colB:
            st.metric("Transfer-Einnahmen", f"€ {season_data['Transfer_Revenues']:,.2f}m")

elif mode == "LaLiga Übersicht":
    col1, col2 = st.columns([1, 8])
    with col1:
        st.image(LALIGA_LOGO, width=100)
    with col2:
        st.title("LaLiga EA Sports - Gesamtübersicht")
    
    if selected_season_liga == "Alle 10 Jahre (Aggregiert)":
        st.markdown("Zeigt die kumulierten Werte der letzten 10 Jahre an.")
        agg_df = df.groupby('Club').agg({
            'Squad_Value_TM': 'last', # current value
            'Transfer_Expenditures': 'sum',
            'Transfer_Revenues': 'sum',
            'Net_Transfer_Balance': 'sum',
            'Total_Transfer_Activity': 'sum'
        }).reset_index()
        season_title = "Letzte 10 Jahre"
    else:
        st.markdown(f"Zeigt die Werte für die Saison **{selected_season_liga}** an.")
        agg_df = df[df['Season'] == selected_season_liga].copy()
        season_title = selected_season_liga
        
    st.markdown("### Top & Flops")
    layout_cfg = dict(template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=0, b=0))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"Kaderwert-Ranking")
        agg_df_sv = agg_df.sort_values(by='Squad_Value_TM', ascending=True)
        fig_sv = px.bar(agg_df_sv, x='Squad_Value_TM', y='Club', orientation='h')
        fig_sv.update_traces(marker_color='#00B4D8')
        fig_sv.update_layout(**layout_cfg)
        st.plotly_chart(fig_sv, use_container_width=True)
        
        st.subheader(f"Transfer-Verluste (Flops)")
        agg_df_net_flop = agg_df.sort_values(by='Net_Transfer_Balance', ascending=True).head(5)
        fig_net_flop = px.bar(agg_df_net_flop, x='Net_Transfer_Balance', y='Club', orientation='h', color_discrete_sequence=['#FF3535'])
        fig_net_flop.update_layout(**layout_cfg)
        st.plotly_chart(fig_net_flop, use_container_width=True)
        
    with col2:
        st.subheader(f"Transfervolumen (Aktivität)")
        agg_df_act = agg_df.sort_values(by='Total_Transfer_Activity', ascending=True)
        fig_act = px.bar(agg_df_act, x='Total_Transfer_Activity', y='Club', orientation='h')
        fig_act.update_traces(marker_color='#FFB800')
        fig_act.update_layout(**layout_cfg)
        st.plotly_chart(fig_act, use_container_width=True)
        
        st.subheader(f"Transfer-Gewinne (Tops)")
        agg_df_net_top = agg_df.sort_values(by='Net_Transfer_Balance', ascending=False).head(5)
        fig_net_top = px.bar(agg_df_net_top, x='Net_Transfer_Balance', y='Club', orientation='h', color_discrete_sequence=['#00E676'])
        fig_net_top.update_layout(**layout_cfg)
        st.plotly_chart(fig_net_top, use_container_width=True)

# Placeholder for Financials
st.markdown("---")
st.header("🔒 Phase 2: Interne Finanzdaten")
st.caption("Die Module für 'Stille Reserven', 'Asset-Effizienz (Umsatz)' und 'Reinvestitionsquote' werden hier integriert, sobald die Book Value Daten vorliegen.")
