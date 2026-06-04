# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Startup Success Analytics",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLE (Glassmorphism / Tech Aesthetic) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    # Load dataset (assumes the CSV is in the same directory)
    df = pd.read_csv("startup_success_dataset (1).csv")
    
    # Simple data cleaning/formatting
    if 'outcome' in df.columns:
        df['Is_Successful'] = df['outcome'].isin(['IPO', 'Acquisition']).astype(int)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.info("Please ensure 'startup_success_dataset (1).csv' is in the same folder as this script.")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.title("🚀 Navigation & Filters")
st.sidebar.markdown("Filter the dataset to customize the deep analytics view.")

# Sector Filter
all_sectors = sorted(df['sector'].unique()) if 'sector' in df.columns else []
selected_sectors = st.sidebar.multiselect("Select Sectors", all_sectors, default=all_sectors)

# Founder Background Filter
all_bg = sorted(df['founder_background'].unique()) if 'founder_background' in df.columns else []
selected_bg = st.sidebar.multiselect("Founder Background", all_bg, default=all_bg)

# Filter Data
filtered_df = df[df['sector'].isin(selected_sectors) & df['founder_background'].isin(selected_bg)]

# --- MAIN APP INTERFACE ---
st.title("📊 Startup Success Deep-Analytics Dashboard")
st.markdown("Gain data-driven insights into startup outcomes, burn rates, and growth trajectories.")
st.write("---")

# --- SECTION 1: HIGH-LEVEL KPIs ---
st.subheader("📌 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_startups = len(filtered_df)
    st.metric(label="Total Startups Analyzed", value=f"{total_startups:,}")

with col2:
    if 'outcome' in filtered_df.columns:
        success_rate = (filtered_df['Is_Successful'].mean() * 100)
        st.metric(label="Success Rate (IPO/Acquisition)", value=f"{success_rate:.1f}%")
    else:
        st.metric(label="Success Rate", value="N/A")

with col3:
    if 'revenue_million' in filtered_df.columns:
        avg_rev = filtered_df['revenue_million'].mean()
        st.metric(label="Avg Revenue", value=f"${avg_rev:.2f}M")
    else:
        st.metric(label="Avg Revenue", value="N/A")

with col4:
    if 'burn_rate_million' in filtered_df.columns:
        avg_burn = filtered_df['burn_rate_million'].mean()
        st.metric(label="Avg Burn Rate", value=f"${avg_burn:.2f}M/yr")
    else:
        st.metric(label="Avg Burn Rate", value="N/A")

st.write("---")

# --- SECTION 2: DEEP ANALYTICS & CHARTS ---
st.subheader("📈 Core Analysis & Ecosystem Insights")

tab1, tab2, tab3 = st.tabs(["🎯 Outcome Breakdown", "💸 Financial Health & Runway", "🧠 Founder & Team Dynamics"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Distribution of Startup Outcomes")
        fig_outcome = px.pie(
            filtered_df, 
            names='outcome', 
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_outcome.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_outcome, use_container_width=True)
        
    with c2:
        st.markdown("#### Success Rate by Sector")
        sector_success = filtered_df.groupby('sector')['Is_Successful'].mean().reset_index()
        sector_success['Success Rate (%)'] = sector_success['Is_Successful'] * 100
        sector_success = sector_success.sort_values(by='Success Rate (%)', ascending=False)
        
        fig_sector = px.bar(
            sector_success, 
            x='Success Rate (%)', 
            y='sector', 
            orientation='h',
            color='Success Rate (%)',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_sector, use_container_width=True)

with tab2:
    st.markdown("#### Revenue vs. Burn Rate Matrix")
    st.markdown("> **Insight:** Startups above the diagonal line are generating more revenue than their annual burn rate, translating into sustainable scaling paths.")
    
    fig_scatter = px.scatter(
        filtered_df,
        x='burn_rate_million',
        y='revenue_million',
        color='outcome',
        size='market_size_billion',
        hover_data=['team_size', 'funding_rounds'],
        labels={
            'burn_rate_million': 'Burn Rate (Millions $)',
            'revenue_million': 'Revenue (Millions $)'
        },
        color_discrete_map={'Failure': '#ef553b', 'IPO': '#636efa', 'Acquisition': '#00cc96'}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### How Investor Types Impact Success")
        fig_inv = px.histogram(
            filtered_df, 
            x="investor_type", 
            color="outcome", 
            barmode="group",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        st.plotly_chart(fig_inv, use_container_width=True)
        
    with col_b:
        st.markdown("#### Experience vs. Team Scaling Size")
        fig_bubble = px.scatter(
            filtered_df,
            x='founder_experience_years',
            y='team_size',
            color='founder_background',
            marginal_x="box",
            labels={'founder_experience_years': 'Years of Experience', 'team_size': 'Team Size'}
        )
        st.plotly_chart(fig_bubble, use_container_width=True)

# --- SECTION 3: RAW DATA EXPLOIT ---
st.write("---")
st.subheader("📋 Filtered Dataset Explorer")
st.dataframe(filtered_df, use_container_width=True)
#Initialize local git repository
git init

# Add all files (app.py, requirements.txt, and your dataset CSV)
git add .

# Commit files locally
git commit -m "Initial commit: Streamlit startup dashboard"

# Rename your primary branch to main
git branch -M main

# Link to your newly created GitHub Repo (Replace with your actual repo link!)
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/startup-success-analytics.git

# Push it live!
git push -u origin main
