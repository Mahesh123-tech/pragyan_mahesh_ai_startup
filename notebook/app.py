import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- PAGE SETUP & UI THEMING ---
st.set_page_config(
    page_title="VenturePulse | Startup Deep Analytics",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling via CSS
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
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px 6px 0px 0px;
        color: #8b949e;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f6feb !important;
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA ACQUISITION & PREPROCESSING ---
@st.cache_data
def load_and_process_data():
    # Referencing the exact user-specified file name
    df = pd.read_csv("startup_success_dataset (1)_2.csv")
    
    # Calculate auxiliary metrics for deep analytics
    df['is_success'] = df['outcome'].isin(['IPO', 'Acquisition']).astype(int)
    
    # Check revenue metric format (handling scaled numbers if necessary)
    if df['revenue_million'].max() > 10000:
        df['revenue_clean_million'] = df['revenue_million'] / 1_000_000
    else:
        df['revenue_clean_million'] = df['revenue_million']
        
    df['runway_months'] = np.where(
        df['burn_rate_million'] > 0, 
        (df['revenue_clean_million'] / df['burn_rate_million']) * 12, 
        48 # Cap/default proxy if burn is 0
    )
    return df

try:
    df = load_and_process_data()
except FileNotFoundError:
    st.error("⚠️ Global Dataset File Missing")
    st.info("Ensure **startup_success_dataset (1)_2.csv** is positioned in the application root execution directory.")
    st.stop()

# --- SIDEBAR INTERFACE (CONTROL PANEL) ---
st.sidebar.image("https://img.icons8.com/external-flat-juicy-fish/100/external-startup-agile-development-flat-juicy-fish.png", width=70)
st.sidebar.title("VenturePulse Engine")
st.sidebar.markdown("Filter ecosystem cohorts dynamically.")

st.sidebar.write("---")
selected_sectors = st.sidebar.multiselect(
    "💡 Industry Verticals", 
    options=sorted(df['sector'].unique()), 
    default=sorted(df['sector'].unique())
)

selected_bg = st.sidebar.multiselect(
    "🧬 Founder Origin Profile", 
    options=sorted(df['founder_background'].unique()), 
    default=sorted(df['founder_background'].unique())
)

min_exp, max_exp = int(df['founder_experience_years'].min()), int(df['founder_experience_years'].max())
selected_exp = st.sidebar.slider("⏳ Minimum Founder Domain Experience (Years)", min_exp, max_exp, (min_exp, max_exp))

# Execution Filter Matrix
mask = (
    df['sector'].isin(selected_sectors) & 
    df['founder_background'].isin(selected_bg) &
    df['founder_experience_years'].between(selected_exp[0], selected_exp[1])
)
filtered_df = df[mask]

# --- APP BRAND HEADER ---
st.title("🚀 Startup Venture Deep Analytics Console")
st.markdown("Macro-ecosystem pattern validation, structural run-rate analysis, and milestone correlations.")
st.write("---")

# --- CONTROL GUARD ---
if filtered_df.empty:
    st.warning("No data matching selection parameters. Broaden sidebar target groups.")
    st.stop()

# --- SECTION 1: EXECUTION METRICS ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Cohort Size (N)", value=f"{len(filtered_df):,}")
with col2:
    succ_rate = filtered_df['is_success'].mean() * 100
    st.metric(label="Success Exit Delta (IPO/Acq)", value=f"{succ_rate:.1f}%")
with col3:
    avg_rev = filtered_df['revenue_clean_million'].mean()
    st.metric(label="Mean Annualized Revenue", value=f"${avg_rev:.2f}M")
with col4:
    avg_burn = filtered_df['burn_rate_million'].mean()
    st.metric(label="Mean Run-Rate Burn", value=f"${avg_burn:.2f}M/yr")

st.write("---")

# --- SECTION 2: DEEP ANALYTICS ARTIFACTS ---
tab_macro, tab_financial, tab_team = st.tabs([
    "📈 Macro Market Dynamics", 
    "💸 Runway & Yield Efficiency", 
    "🧠 Human Capital Index"
])

# TAB 1: MACRO MARKET DYNAMICS
with tab_macro:
    c1, c2 = st.columns([2, 3])
    with c1:
        st.markdown("#### Outcome Cohort Allocation")
        fig_pie = px.pie(
            filtered_df, names='outcome', hole=0.5,
            color_discrete_sequence=px.colors.qualitative.G10
        )
        fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        st.markdown("#### Exit Density Across Addressable Market (TAM)")
        fig_box = px.box(
            filtered_df, x='outcome', y='market_size_billion', color='outcome',
            points="outliers", color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_box.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_box, use_container_width=True)

# TAB 2: RUNWAY & YIELD EFFICIENCY
with tab_financial:
    st.markdown("#### Capital Consumption Matrix (Burn vs Revenue)")
    st.caption("Bubble sizing represents total addressable market size (TAM in Billions). Diagnostic crosshairs help evaluate capital efficiency.")
    
    fig_scatter = px.scatter(
        filtered_df, 
        x='burn_rate_million', 
        y='revenue_clean_million',
        color='outcome', 
        size='market_size_billion', 
        hover_data=['funding_rounds', 'product_traction_users'],
        color_discrete_map={'Failure': '#ff4b4b', 'IPO': '#00f2fe', 'Acquisition': '#4caf50'},
        max_size=35
    )
    fig_scatter.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_scatter, use_container_width=True)

# TAB 3: HUMAN CAPITAL INDEX
with tab_team:
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("#### Investor Type Deployment vs Outcomes")
        fig_hist = px.histogram(
            filtered_df, x='investor_type', color='outcome', barmode='group',
            color_discrete_sequence=px.colors.palette.Tealgrn
        )
        fig_hist.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_hist, use_container_width=True)
        
    with c4:
        st.markdown("#### Scaled Team Growth vs Founder Background")
        fig_strip = px.strip(
            filtered_df, x='founder_background', y='team_size', color='outcome',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_strip.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_strip, use_container_width=True)

# --- SECTION 3: DEEP INSIGHTS RECONCILIATION ---
st.write("---")
st.subheader("💡 Strategic Insight Ledger")

# Compute data-driven insights dynamically based on subset values
top_performing_sector = filtered_df.groupby('sector')['is_success'].mean().idxmax()
top_performing_rate = filtered_df.groupby('sector')['is_success'].mean().max() * 100
capital_heavyweight_bg = filtered_df.groupby('founder_background')['burn_rate_million'].mean().idxmax()

st.info(f"**Dominant Growth Subsector:** Companies tracking within **{top_performing_sector}** yield the current peak exit efficiency profile of **{top_performing_rate:.1f}%** relative to alternatives inside this slice.")
st.warning(f"**Capital Expenditure Profile:** Cohorts run by founders with a background in **{capital_heavyweight_bg}** express the peak mean burn-rate footprints inside the filtered subset.")

# --- SECTION 4: COHORT RAW LOOKUP ---
st.write("---")
with st.expander("👁️ Inspect Live Filtered Registry"):
    st.dataframe(filtered_df, use_container_width=True)
