import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 1. PAGE SETUP & THEME TRICKS ---
st.set_page_config(
    page_title="VenturePulse | Startup Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium dark UI / Glassmorphism container styling via CSS injection
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    div[data-testid="metric-container"] {
        background: rgba(22, 27, 34, 0.8);
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px 6px 0px 0px;
        color: #8b949e;
        padding: 10px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f6feb !important;
        color: #ffffff !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. FAST DATA PIPELINE (CACHED) ---
@st.cache_data
def load_and_clean_data():
    # Reads the exact filename provided
    df = pd.read_csv("startup_success_dataset (1).csv")
    
    # Check if revenue needs to be adjusted to Millions 
    # (Your dataset contains raw values like 1,483,962; we divide by 1M for clean chart labels)
    if df['revenue_million'].max() > 100000:
        df['revenue_clean_million'] = df['revenue_million'] / 1_000_000
    else:
        df['revenue_clean_million'] = df['revenue_million']
        
    # Helper tracker column for calculation (1 if successful, 0 if failed)
    df['is_success'] = df['outcome'].isin(['IPO', 'Acquisition']).astype(int)
    return df

try:
    df = load_and_clean_data()
except FileNotFoundError:
    st.error("❌ Critical File Missing!")
    st.info("Please make sure **`startup_success_dataset (1).csv`** is in the exact same folder as this `app.py` file.")
    st.stop()

# --- 3. SIDEBAR CONTROLS (FILTERS) ---
st.sidebar.markdown("## 📊 Dashboard Controls")
st.sidebar.markdown("Filter the global startup ecosystem metrics instantly:")

# Filter 1: Industry Selection
all_sectors = sorted(df['sector'].unique())
selected_sectors = st.sidebar.multiselect("💡 Industry Sectors", all_sectors, default=all_sectors)

# Filter 2: Founder Background
all_bg = sorted(df['founder_background'].unique())
selected_bg = st.sidebar.multiselect("🧬 Founder Backgrounds", all_bg, default=all_bg)

# Filter 3: Experience Slider
min_exp, max_exp = int(df['founder_experience_years'].min()), int(df['founder_experience_years'].max())
selected_exp = st.sidebar.slider("⏳ Founder Experience (Years)", min_exp, max_exp, (min_exp, max_exp))

# Apply combined filters to the dataset
mask = (
    df['sector'].isin(selected_sectors) & 
    df['founder_background'].isin(selected_bg) &
    df['founder_experience_years'].between(selected_exp[0], selected_exp[1])
)
filtered_df = df[mask]

# --- 4. HERO HEADER ---
st.title("🚀 Startup Analytics & Outcome Telemetry")
st.markdown("Deep interactive data analytics tracking capital efficiency, founder profiles, and market paths.")
st.write("---")

if filtered_df.empty:
    st.warning("⚠️ No records found matching your active filter choices. Broaden your sidebar settings.")
    st.stop()

# --- 5. HIGH-LEVEL EXECUTIVE METRICS ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric(label="Total Startups Tracked", value=f"{len(filtered_df):,}")
with kpi2:
    success_rate = filtered_df['is_success'].mean() * 100
    st.metric(label="Success Exit Rate (IPO/Acq)", value=f"{success_rate:.1f}%")
with kpi3:
    st.metric(label="Average Revenue Generated", value=f"${filtered_df['revenue_clean_million'].mean():.2f}M")
with kpi4:
    st.metric(label="Average Annual Burn Rate", value=f"${filtered_df['burn_rate_million'].mean():.2f}M")

st.write("---")

# --- 6. CHART TABS SECTION ---
tab_macro, tab_financial, tab_team = st.tabs([
    "📈 Market Outcomes", 
    "💸 Burn vs. Revenue Efficiency", 
    "🧠 Team & Experience Metrics"
])

# TAB 1: MARKET DISTRIBUTION
with tab_macro:
    c1, c2 = st.columns([2, 3])
    with c1:
        st.markdown("#### Global Outcome Distribution")
        fig_pie = px.pie(
            filtered_df, names='outcome', hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        st.markdown("#### Total Addressable Market (TAM in Billions) vs Exit Route")
        fig_box = px.box(
            filtered_df, x='outcome', y='market_size_billion', color='outcome',
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_box.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_box, use_container_width=True)

# TAB 2: CAPITAL EFFICIENCY MATRIX
with tab_financial:
    st.markdown("#### Capital Consumption Matrix (Burn Rate vs. Topline Revenue)")
    st.caption("Bubble sizes visualize Total Addressable Market (TAM in Billions). Colors differentiate company lifecycle final outcomes.")
    
    fig_scatter = px.scatter(
        filtered_df, 
        x='burn_rate_million', 
        y='revenue_clean_million',
        color='outcome', 
        size='market_size_billion',
        hover_data=['funding_rounds', 'product_traction_users', 'team_size'],
        color_discrete_map={'Failure': '#ff4b4b', 'IPO': '#00f2fe', 'Acquisition': '#4caf50'},
        labels={'burn_rate_million': 'Annual Burn Rate ($ Millions)', 'revenue_clean_million': 'Annual Revenue ($ Millions)'},
        max_size=35
    )
    fig_scatter.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_scatter, use_container_width=True)

# TAB 3: TEAM & HUMAN EXPERIENCE
with tab_team:
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("#### Outcome Volume by Backing Investor Type")
        fig_hist = px.histogram(
            filtered_df, x='investor_type', color='outcome', barmode='group',
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        fig_hist.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_hist, use_container_width=True)
        
    with c4:
        st.markdown("#### Operational Team Scaling Size vs Founder Origin")
        fig_strip = px.strip(
            filtered_df, x='founder_background', y='team_size', color='outcome',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_strip.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_strip, use_container_width=True)

# --- 7. AUTOMATED INSIGHT MACHINE ---
st.write("---")
st.subheader("💡 Automatically Extracted Ecosystem Insights")

# Generate statistics dynamically based on current slider inputs
best_sector = filtered_df.groupby('sector')['is_success'].mean().idxmax()
best_rate = filtered_df.groupby('sector')['is_success'].mean().max() * 100
heavy_burn_bg = filtered_df.groupby('founder_background')['burn_rate_million'].mean().idxmax()

st.info(f"📊 **Subsector Leader:** Within this subset, **{best_sector}** companies hold the highest historical exit efficiency rating, with **{best_rate:.1f}%** reaching an IPO or Acquisition.")
st.warning(f"💸 **Capital Burn Pattern:** Teams led by founders with a background as an **{heavy_burn_bg}** express the highest mean burn rate in this current view.")

# --- 8. LIVE DATABASE LOOKUP ---
st.write("---")
with st.expander("👁️ Open Raw Filtered Data Registry (Inspect Spreadsheet Rows)"):
    st.dataframe(filtered_df, use_container_width=True)
