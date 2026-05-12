import streamlit as st
import pandas as pd
import plotly.graph_objects as go # type: ignore
from plotly.subplots import make_subplots # type: ignore
import numpy as np

# ============================================================
# Page setup
# ============================================================
st.set_page_config(
    page_title="The System Is Improving. But Are People?",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling
st.markdown("""
<style>
    .main > div {
        padding-top: 1rem;
    }

    /* ── Headings adapt to theme ── */
    h1 {
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    h2 {
        margin-top: 2rem;
    }

    /* ── Metric cards adapt to theme ── */
    .stMetric {
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3498DB;
    }

    /* ── Sidebar map tightening ── */
    section[data-testid="stSidebar"] .js-plotly-plot {
        margin-top: -10px;
        margin-bottom: -10px;
    }

    /* ── Progress indicator cards — dark mode ── */
    @media (prefers-color-scheme: dark) {
        .progress-card-active {
            background: #1A2535 !important;
            border-color: #3498DB !important;
        }
        .progress-card-done {
            background: #1A3A2A !important;
            border-color: #27AE60 !important;
        }
        .progress-card-pending {
            background: #2C2C2C !important;
            border-color: #444 !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# Data loaders
# ============================================================
@st.cache_data
def load_master_data():
    try:
        df = pd.read_csv('master_quarterly_enriched.csv')
        # The new master CSV has 31 columns (vs 29 before): two extra
        # columns 'housing_cpi_yoy' and 'housing_vs_overall_yoy_gap' are
        # loaded automatically and available downstream if needed.
        df = df[df['period'].notna()].copy()
        return df
    except FileNotFoundError:
        st.error("❌ master_quarterly_enriched.csv not found!")
        st.stop()

@st.cache_data
def load_labour_data():
    try:
        df_labour = pd.read_csv('labour_cleaned.csv')
        df_labour = df_labour[df_labour['date'].notna()].copy()
        df_labour['date'] = pd.to_datetime(df_labour['date'])
        return df_labour
    except Exception:
        return None

@st.cache_data
def load_cpi_city_data():
    try:
        df_cpi = pd.read_csv('cpi_by_city_cleaned.csv')
        df_cpi['date'] = pd.to_datetime(df_cpi['date'])
        return df_cpi
    except Exception:
        return None

@st.cache_data
def load_city_coords():
    try:
        return pd.read_csv('city_coordinates.csv')
    except Exception:
        return None

# Load
df = load_master_data()
df_labour = load_labour_data()
df_cpi = load_cpi_city_data()
city_coords = load_city_coords()

# --- Theme detection ---
CHART_FONT_COLOR = 'rgba(180,180,180,0.9)'  # dark mode default
AXIS_COLOR = 'rgba(128,128,128,0.4)'
GRID_COLOR = 'rgba(128,128,128,0.2)'

# Professional color palette
COLORS = {
    'primary': '#3498DB',
    'danger': '#E74C3C',
    'success': '#27AE60',
    'warning': '#F39C12',
    'secondary': '#95A5A6',
    'dark': '#2C3E50',
    'light': '#ECF0F1'
}

CITIES = ['Australia (All)', 'Sydney', 'Melbourne', 'Brisbane', 'Adelaide',
          'Perth', 'Hobart', 'Darwin', 'Canberra']

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("Dashboard Controls")

scene_nav = st.sidebar.radio(
    "📍 Jump to Scene:",
    ["All Scenes", "Scene 1: Crime Scene", "Scene 2: Red Herring",
     "Scene 3: Culprit", "Scene 4: Deeper Motive", "Scene 5: Verdict"],
    index=0
)

st.sidebar.markdown("---")

# --------------------------------------------------------
# City Filter — interactive Australia map
# --------------------------------------------------------
st.sidebar.markdown("### City Filter")
st.sidebar.caption("Filters Scene 4 - Regional CPI by City")
st.sidebar.caption("Click a city dot or select below")

# Initialise session state
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = 'Australia (All)'

def _build_city_map(coords_df: pd.DataFrame, active_city: str) -> go.Figure:
    """Build the interactive Australia city map for the sidebar."""
    fig = go.Figure()

    # National (centre-of-country) marker — green star
    is_national_active = active_city == 'Australia (All)'
    fig.add_trace(go.Scattergeo(
        lat=[-25.5],
        lon=[134.5],
        mode='markers+text',
        marker=dict(
            size=24 if is_national_active else 20,
            color=COLORS['success'],
            symbol='star',
            line=dict(color='white', width=2.5)
        ),
        text=['National'],
        textposition='top center',
        textfont=dict(
            color='white',
            size=12,
            family='Arial Black' if is_national_active else 'Arial'
        ),
        customdata=[['Australia (All)']],
        hovertemplate='<b>National</b><br>(All Australia)<extra></extra>',
        name='national',
        showlegend=False
    ))

    # City dots — highlight active city in red
    marker_colors = [
        COLORS['danger'] if city == active_city else COLORS['primary']
        for city in coords_df['city']
    ]
    marker_sizes = [
        18 if city == active_city else 13
        for city in coords_df['city']
    ]
    text_styles = [
        'Arial Black' if city == active_city else 'Arial'
        for city in coords_df['city']
    ]

    fig.add_trace(go.Scattergeo(
        lat=coords_df['latitude'],
        lon=coords_df['longitude'],
        mode='markers+text',
        marker=dict(
            size=marker_sizes,
            color=marker_colors,
            line=dict(color='white', width=2)
        ),
        text=coords_df['city'],
        textposition='top center',
        textfont=dict(color='white', size=11, family='Arial'),
        customdata=coords_df[['city']].values,
        hovertemplate='<b>%{text}</b><extra></extra>',
        name='cities',
        showlegend=False
    ))

    fig.update_geos(
        scope='world',
        projection_type='mercator',
        center=dict(lat=-26, lon=134),
        lonaxis_range=[110, 156],
        lataxis_range=[-44, -9],
        showland=True,
        landcolor='rgba(45, 55, 85, 0.55)',
        showocean=False,
        showcoastlines=True,
        coastlinecolor='rgba(160, 175, 215, 0.45)',
        coastlinewidth=1,
        showcountries=False,
        showframe=True,
        framecolor='rgba(160, 175, 215, 0.25)',
        framewidth=1,
        bgcolor='rgba(0,0,0,0)'
    )

    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=15, b=10),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        dragmode=False,
        clickmode='event+select'
    )
    return fig

if city_coords is not None:
    fig_map = _build_city_map(city_coords, st.session_state.selected_city)

    with st.sidebar:
        map_event = st.plotly_chart(
            fig_map,
            use_container_width=True,
            key='city_map_widget',
            on_select='rerun',
            selection_mode='points',
            config={'displayModeBar': False, 'scrollZoom': False}
        )

    # Process click — update session state BEFORE the selectbox renders
    # so the selectbox shows the new selection.
    if map_event is not None:
        # Streamlit returns a dict-like with a 'selection' key
        sel = (
            map_event.get('selection') if isinstance(map_event, dict)
            else getattr(map_event, 'selection', None)
        )
        if sel:
            pts = (
                sel.get('points', []) if isinstance(sel, dict)
                else getattr(sel, 'points', [])
            )
            if pts:
                first = pts[0]
                cd = (
                    first.get('customdata') if isinstance(first, dict)
                    else getattr(first, 'customdata', None)
                )
                if cd is not None:
                    clicked_city = cd[0] if isinstance(cd, (list, tuple)) else cd
                    if clicked_city and clicked_city != st.session_state.selected_city:
                        st.session_state.selected_city = clicked_city
                        st.rerun()

# Selectbox — uses session_state key so map clicks and dropdown stay in sync
idx = (
    CITIES.index(st.session_state.selected_city)
    if st.session_state.selected_city in CITIES else 0
)
selected_city = st.sidebar.selectbox(
    "Or select a city:",
    CITIES,
    index=idx,
    key='city_selectbox'
)
if selected_city != st.session_state.selected_city:
    st.session_state.selected_city = selected_city
    st.rerun()

st.sidebar.markdown("---")

# --------------------------------------------------------
# What-If Sliders
# --------------------------------------------------------
st.sidebar.markdown("### What-If Analysis")
wage_increase = st.sidebar.slider("Wage Increase (%):", 0.0, 10.0, 3.5, 0.5)
cpi_forecast = st.sidebar.slider("CPI Forecast (%):", 0.0, 8.0, 3.0, 0.5)

purchasing_power_change = wage_increase - cpi_forecast
future_purchasing_power = 100 * (1 + purchasing_power_change / 100)

if purchasing_power_change > 0:
    st.sidebar.success(f"✅ +{purchasing_power_change:.1f}% gain")
elif purchasing_power_change < 0:
    st.sidebar.error(f"❌ {purchasing_power_change:.1f}% loss")
else:
    st.sidebar.warning(f"➖ {purchasing_power_change:.1f}% breakeven")

st.sidebar.metric("Purchasing Power", f"{future_purchasing_power:.1f}",
                  f"{purchasing_power_change:.1f}%")

# ============================================================
# MAIN DASHBOARD
# ============================================================
st.markdown("""
<div style='text-align: center; padding: 2rem 0 1rem 0;'>
    <div style='font-size: 20px; letter-spacing: 4px; color: #3498DB; 
                font-weight: 600; text-transform: uppercase; 
                margin-bottom: 12px;'>
        🔍 ECONOMIC INTELLIGENCE BRIEF
    </div>
    <div style='font-size: 58px; font-weight: 800; 
                background: linear-gradient(135deg, #3498DB, #E74C3C);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                line-height: 1.2; margin-bottom: 12px;'>
        The System Is Improving.<br>But Are People?
    </div>
    <div style='font-size: 24px; color: #7F8C8D; font-style: italic;
                letter-spacing: 1px; margin-bottom: 8px;'>
        A Detective Arc Investigation into Australia's Economic Reality
    </div>
    <div style='font-size: 16px; color: #95A5A6; letter-spacing: 2px;
                text-transform: uppercase;'>
        Paula - Senior Economic Policy Advisor, Federal Treasury
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- Paula's instant insight banner ---
st.markdown("### Instant Brief")
col1, col2, col3, col4 = st.columns(4)

gdp_val = df.iloc[-1]['gdp_growth_pct']
real_wage_val = df['real_wage_growth'].iloc[-2]  # Dec-2025 (last WPI quarter)
housing_yoy_val = pd.read_csv("housing_cpi_yoy.csv").iloc[-1]['housing_cpi_yoy']
cumulative_val = df['cpi_cumulative_pct'].iloc[-1]

with col1:
    sign1 = "+" if gdp_val > 0 else ""
    st.markdown(f"""
    <div style='text-align:center; background:var(--secondary-background-color); 
                border-radius:8px; padding:15px; border-left: 5px solid #3498DB;'>
        <div style='font-size:16px; color:#3498DB; font-weight:600; text-transform:uppercase;'>
            GDP Growth</div>
        <div style='font-size:32px; font-weight:700;'>{sign1}{gdp_val:.1f}%</div>
        <div style='font-size:16px; color:#3498DB;'>↑ Macro positive</div>
    </div>""", unsafe_allow_html=True)

with col2:
    sign2 = "+" if real_wage_val > 0 else ""
    color2 = '#E74C3C' if real_wage_val < 0 else '#27AE60'
    arrow2 = '↓' if real_wage_val < 0 else '↑'
    st.markdown(f"""
    <div style='text-align:center; background:var(--secondary-background-color); 
                border-radius:8px; padding:15px; border-left: 5px solid {color2};'>
        <div style='font-size:16px; color:{color2}; font-weight:600; text-transform:uppercase;'>
            Real Wages</div>
        <div style='font-size:32px; font-weight:700; color:{color2};'>{sign2}{real_wage_val:.2f}%</div>
        <div style='font-size:16px; color:{color2};'>{arrow2} Purchasing power {'lost' if real_wage_val < 0 else 'gained'}</div>
    </div>""", unsafe_allow_html=True)

with col3:
    sign3 = "+" if housing_yoy_val > 0 else ""
    st.markdown(f"""
    <div style='text-align:center; background:var(--secondary-background-color); 
                border-radius:8px; padding:15px; border-left: 5px solid #E74C3C;'>
        <div style='font-size:16px; color:#E74C3C; font-weight:600; text-transform:uppercase;'>
            Housing CPI YoY</div>
        <div style='font-size:32px; font-weight:700; color:#E74C3C;'>{sign3}{housing_yoy_val:.2f}%</div>
        <div style='font-size:16px; color:#E74C3C;'>↑ Primary culprit</div>
    </div>""", unsafe_allow_html=True)

with col4:
    sign4 = "+" if cumulative_val > 0 else ""
    st.markdown(f"""
    <div style='text-align:center; background:var(--secondary-background-color); 
                border-radius:8px; padding:15px; border-left: 5px solid #E74C3C;'>
        <div style='font-size:16px; color:#E74C3C; font-weight:600; text-transform:uppercase;'>
            Prices Since 2024</div>
        <div style='font-size:32px; font-weight:700; color:#E74C3C;'>{sign4}{cumulative_val:.1f}%</div>
        <div style='font-size:16px; color:#E74C3C;'>↑ Cumulative burden</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# SCENE 1: THE CRIME SCENE
# ============================================================
if scene_nav in ["All Scenes", "Scene 1: Crime Scene"]:
    st.markdown('## <span style="color:#2C5AA0; font-size:1.1em">●</span> Scene 1: The Crime Scene', unsafe_allow_html=True)
    st.subheader("GDP Growth vs GDP Per Capita Growth (2024-2025)")

    fig1 = go.Figure()

    fig1.add_trace(go.Scatter(
        x=df['period'],
        y=df['gdp_growth_pct'],
        mode='lines+markers',
        name='GDP Growth',
        line=dict(color=COLORS['primary'], width=4),
        marker=dict(size=10, color=COLORS['primary'], symbol='circle',
                    line=dict(width=2, color='white')),
        fill='tonexty',
        fillcolor='rgba(52, 152, 219, 0.1)',
        hovertemplate='<b>%{x}</b><br>GDP Growth: %{y:.2f}%<extra></extra>'
    ))

    fig1.add_trace(go.Scatter(
        x=df['period'],
        y=df['gdp_per_capita_growth_pct'],
        mode='lines+markers',
        name='GDP Per Capita',
        line=dict(color=COLORS['danger'], width=4, dash='dash'),
        marker=dict(size=10, color=COLORS['danger'], symbol='diamond',
                    line=dict(width=2, color='white')),
        hovertemplate='<b>%{x}</b><br>Per Capita: %{y:.2f}%<extra></extra>'
    ))

    fig1.add_hline(y=0, line_dash="dot", line_color=COLORS['dark'],
                   line_width=2, opacity=0.5)

    first_per_capita = df['gdp_per_capita_growth_pct'].iloc[0]
    fig1.add_annotation(
        x='2024-Q1', y=first_per_capita,
        text="<b>Critical Divergence Point</b><br>Per capita turned negative",
        showarrow=True, arrowhead=3, arrowsize=1.5, arrowwidth=3,
        arrowcolor=COLORS['danger'], ax=150, ay=60,
        bgcolor="rgba(30,30,30,0.9)", bordercolor=COLORS['danger'],
        borderwidth=3, borderpad=10,
        font=dict(family="Arial", size=13, color='rgba(180,180,180,0.9)')
    )

    fig1.update_layout(
        xaxis_title="<b>Quarter</b>",
        yaxis_title="<b>Growth Rate (%)</b>",
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=13, color='rgba(180,180,180,0.9)'),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)",
            bordercolor='rgba(128,128,128,0.3)',
            borderwidth=1,
            font=dict(size=13)
        ),
        height=450,
        margin=dict(l=80, r=50, t=80, b=80),
        title=dict(
            text="<b>The Great Divergence: Aggregate vs Individual Prosperity</b>",
            font=dict(size=16),
            x=0.5, xanchor='center'
        )
    )

    fig1.update_xaxes(
        showgrid=False,
        showline=True, linewidth=1,
        linecolor='rgba(128,128,128,0.4)',
        mirror=True,
        ticks="outside", ticklen=6,
        tickcolor='rgba(128,128,128,0.4)',
        tickfont=dict()
    )
    fig1.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128,128,128,0.2)',
        showline=True, linewidth=1,
        linecolor='rgba(128,128,128,0.4)',
        mirror=True,
        zeroline=False,
        ticks="outside", ticklen=6,
        tickcolor='rgba(128,128,128,0.4)',
        tickfont=dict()
    )


    st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

    col1, col2 = st.columns([2, 1])
    with col1:
        st.info("""
        **Policy Insight:** Macro indicators show economic growth, but per capita analysis 
        reveals declining individual prosperity. This divergence signals population growth 
        outpacing economic gains, a critical metric for household-focused policy interventions.
        """)
    with col2:
        gdp_latest = df.iloc[-1]['gdp_growth_pct']
        sign1 = "+" if gdp_latest > 0 else ""
        st.metric("Latest GDP Growth",
                 f"{sign1}{gdp_latest:.1f}%",
                 f"{'Positive' if gdp_latest > 0 else 'Negative'}",
                 delta_color="normal" if gdp_latest > 0 else "inverse")
        per_capita_latest = df.iloc[-1]['gdp_per_capita_growth_pct']
        sign2 = "+" if per_capita_latest > 0 else ""
        st.metric("Latest Per Capita",
                 f"{sign2}{per_capita_latest:.1f}%",
                 f"{'Positive' if per_capita_latest > 0 else 'Negative'}",
                 delta_color="normal" if per_capita_latest > 0 else "inverse")

    if scene_nav == "All Scenes":
        st.markdown("---")

# ============================================================
# SCENE 2: THE RED HERRING
# ============================================================
if scene_nav in ["All Scenes", "Scene 2: Red Herring"]:
    st.markdown('## <span style="color:#8B2635; font-size:1.1em">●</span> Scene 2: The Red Herring', unsafe_allow_html=True)
    st.subheader("Employment Trends - Strong on Surface, Weak on Substance")

    if df_labour is not None:
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])

        fig2.add_trace(
            go.Scatter(
                x=df_labour['date'], y=df_labour['employed_total_sa'],
                mode='lines+markers', name='Employed Total',
                line=dict(color=COLORS['primary'], width=4),
                marker=dict(size=8, symbol='circle'),
                hovertemplate='<b>%{x|%b %Y}</b><br>Employed: %{y:,.0f}k<extra></extra>'
            ),
            secondary_y=False
        )

        fig2.add_trace(
            go.Scatter(
                x=df_labour['date'], y=df_labour['unemployment_rate_sa'],
                mode='lines+markers', name='Unemployment Rate',
                line=dict(color=COLORS['warning'], width=4, dash='dash'),
                marker=dict(size=8, symbol='diamond'),
                hovertemplate='<b>%{x|%b %Y}</b><br>Rate: %{y:.1f}%<extra></extra>'
            ),
            secondary_y=True
        )

        fig2.update_layout(
            title="<b>Employment Metrics: The Deceptive Indicators</b>",
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial", size=13, color='rgba(180,180,180,0.9)'),
            legend=dict(
                orientation="h", y=1.15, x=0.5, xanchor="center",
                bgcolor="rgba(0,0,0,0)",
                bordercolor='rgba(128,128,128,0.3)',
                borderwidth=1,
                font=dict(size=13)
            ),
            height=450,
            margin=dict(l=80, r=50, t=120, b=80)
        )

        fig2.update_xaxes(
            title="<b>Date</b>",
            showgrid=False,
            showline=True, linewidth=1,
            linecolor='rgba(128,128,128,0.4)',
            mirror=True,
            tickfont=dict()
        )
        fig2.update_yaxes(
            title_text="<b>Employed (000s)</b>",
            showgrid=True, gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            showline=True, linewidth=1,
            linecolor='rgba(128,128,128,0.4)',
            mirror=True,
            tickfont=dict(),
            title_font=dict(color=COLORS['primary']),
            secondary_y=False
        )
        fig2.update_yaxes(
            title_text="<b>Unemployment Rate (%)</b>",
            showgrid=False,
            showline=True, linewidth=1,
            linecolor='rgba(128,128,128,0.4)',
            tickfont=dict(),
            title_font=dict(color=COLORS['warning']),
            secondary_y=True
        )

        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

        employed_latest = df_labour['employed_total_sa'].iloc[-1]
        employed_start = df_labour['employed_total_sa'].iloc[0]
        jobs_added = employed_latest - employed_start
        unemp_latest = df_labour['unemployment_rate_sa'].iloc[-1]
        unemp_start = df_labour['unemployment_rate_sa'].iloc[0]

        st.success(f"""
        **The Red Herring:** Employment grew by **{jobs_added:,.0f}k** jobs since 
        Jan-2024, reaching **{employed_latest:,.0f}k** total. Yet unemployment also 
        rose from **{unemp_start:.1f}%** to **{unemp_latest:.1f}%**. High employment 
        tells us jobs exist, not whether wages cover living costs.
        """)
    else:
        st.warning("⚠️ Labour data unavailable")

    if scene_nav == "All Scenes":
        st.markdown("---")

# ============================================================
# SCENE 3: THE CULPRIT REVEALED
# ============================================================
if scene_nav in ["All Scenes", "Scene 3: Culprit"]:
    st.markdown('## <span style="color:#E89B5B; font-size:1.1em">●</span> Scene 3: The Culprit Revealed', unsafe_allow_html=True)
    st.subheader("Real Wage Growth - The Smoking Gun")

    colors_gradient = [
        COLORS['danger'] if x < 0 else
        COLORS['success'] if x > 1 else
        COLORS['warning']
        for x in df['real_wage_growth']
    ]

    fig3 = go.Figure()

    # --- Actual real wage growth bars ---
    fig3.add_trace(go.Bar(
        x=df['period'],
        y=df['real_wage_growth'],
        name='Actual Real Wage Growth',
        marker=dict(
            color=colors_gradient,
            line=dict(color='white', width=2),
            pattern_shape=["/" if x < 0 else "" for x in df['real_wage_growth']]
        ),
        text=[f"<b>{val:.2f}%</b>" for val in df['real_wage_growth']],
        textposition='outside',
        textfont=dict(size=12, family="Arial"),
        hovertemplate='<b>%{x}</b><br>Real Wage Growth: %{y:.2f}%<extra></extra>',
        showlegend=True
    ))

    # --- What-If projected line ---
    projected_real_wage = wage_increase - cpi_forecast
    fig3.add_trace(go.Scatter(
        x=df['period'],
        y=[projected_real_wage] * len(df),
        mode='lines',
        name=f'What-If: Wages {wage_increase}% - CPI {cpi_forecast}% = {projected_real_wage:.1f}%',
        line=dict(
            color=COLORS['success'] if projected_real_wage > 0 else COLORS['danger'],
            width=3,
            dash='dashdot'
        ),
        hovertemplate=f'<b>Projected Real Wage: {projected_real_wage:.1f}%</b><extra></extra>'
    ))

    # --- Zero line ---
    fig3.add_hline(y=0, line_dash="solid", line_color=COLORS['dark'],
                   line_width=3, opacity=0.7)

    # --- Annotation for first negative quarter ---
    fig3.add_annotation(
        x='2025-Q4', y=-0.23,
        text="<b>⚠️ FIRST NEGATIVE QUARTER</b><br>Purchasing power decline begins",
        showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=4,
        arrowcolor=COLORS['danger'], ax=120, ay=60,
        bgcolor="rgba(30,30,30,0.9)", bordercolor=COLORS['danger'],
        borderwidth=3, borderpad=12,
        font=dict(family="Arial", size=13, color='rgba(180,180,180,0.9)'),
    )

    # --- What-If annotation ---
    fig3.add_annotation(
        x=df['period'].iloc[-1],
        y=projected_real_wage,
        text=f"<b>What-If Projection<br>{projected_real_wage:.1f}%</b>",
        showarrow=True,
        arrowhead=2,
        arrowcolor=COLORS['success'] if projected_real_wage > 0 else COLORS['danger'],
        ax=-80, ay=-40,
        bgcolor="rgba(30,30,30,0.9)",
        bordercolor=COLORS['success'] if projected_real_wage > 0 else COLORS['danger'],
        borderwidth=2,
        borderpad=8,
        font=dict(family="Arial", size=13, color='rgba(180,180,180,0.9)')
    )

    fig3.update_layout(
        title="<b>Real Wage Growth: WPI Growth Minus CPI Growth</b>",
        xaxis_title="<b>Quarter</b>",
        yaxis_title="<b>Real Wage Growth (%)</b>",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=13),
        height=450,
        margin=dict(l=80, r=50, t=120, b=80),
        legend=dict(
            orientation="h", y=1.15, x=0.5, xanchor="center",
            bgcolor="rgba(0,0,0,0)",
            bordercolor='rgba(128,128,128,0.3)',
            borderwidth=1,
            font=dict(size=13)
        )
    )

    fig3.update_xaxes(
        showgrid=False,
        showline=True, linewidth=1,
        linecolor='rgba(128,128,128,0.4)',
        mirror=True,
        ticks="outside", ticklen=6,
        tickcolor='rgba(128,128,128,0.4)',
        tickfont=dict()
    )
    fig3.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128,128,128,0.2)',
        showline=True, linewidth=1,
        linecolor='rgba(128,128,128,0.4)',
        mirror=True,
        zeroline=False,
        ticks="outside", ticklen=6,
        tickcolor='rgba(128,128,128,0.4)',
        tickfont=dict()
    )

    st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

    # --- Metric cards ---
    col1, col2, col3, col4 = st.columns(4)

    peak_real_wage = df['real_wage_growth'].max()
    peak_quarter = df.loc[df['real_wage_growth'].idxmax(), 'period']
    latest_real_wage = df['real_wage_growth'].iloc[-2]
    latest_quarter = df['period'].iloc[-2]
    latest_wpi = df['wpi_pct_change_yoy_sa'].iloc[-2]
    latest_cpi = df['cpi_yoy_quarterly'].iloc[-2]

    with col1:
        sign1 = "+" if peak_real_wage > 0 else ""
        st.metric(f"Peak Gain ({peak_quarter})",
                  f"{sign1}{peak_real_wage:.2f}%",
                  f"{'Workers ahead' if peak_real_wage > 0 else 'Workers behind'}",
                  delta_color="normal" if peak_real_wage > 0 else "inverse")
    with col2:
        sign2 = "+" if latest_real_wage > 0 else ""
        st.metric(f"Latest ({latest_quarter})",
                  f"{sign2}{latest_real_wage:.2f}%",
                  f"{'Workers ahead' if latest_real_wage > 0 else 'Workers behind'}",
                  delta_color="normal" if latest_real_wage > 0 else "inverse")
    with col3:
        net_change = df['real_wage_growth'].sum()
        sign3 = "+" if net_change > 0 else ""
        st.metric("Cumulative Impact", f"{sign3}{net_change:.2f}%", "Overall period")
    with col4:
        st.metric("What-If Projection",
                  f"{projected_real_wage:.1f}%",
                  "✅ Gain" if projected_real_wage > 0 else "➖ Breakeven" if projected_real_wage == 0 else "❌ Loss",
                  delta_color="normal" if projected_real_wage > 0 else "inverse" if projected_real_wage < 0 else "warning")

    # --- What-If insight box ---
    if projected_real_wage > 0:
        st.success(f"""
        **What-If Scenario:** If wages grow at **{wage_increase}%** and CPI holds 
        at **{cpi_forecast}%**, real wages would recover to **+{projected_real_wage:.1f}%**, 
        workers would regain purchasing power. Policy should target wage growth above 
        {cpi_forecast}% to sustain real gains.
        """)
    elif projected_real_wage == 0:
        st.warning(f"""
        **What-If Scenario:** If wages grow at **{wage_increase}%** and CPI holds 
        at **{cpi_forecast}%**, real wages would **break even at 0%**, workers 
        maintain but don't improve purchasing power.
        """)
    else:
        st.error(f"""
        **What-If Scenario:** If wages grow at **{wage_increase}%** and CPI holds 
        at **{cpi_forecast}%**, real wages would remain negative at **{projected_real_wage:.1f}%**, 
        workers continue losing purchasing power. Policy intervention urgently needed.
        """)

    # Critical Finding box
    first_negative = df[df['real_wage_growth'] < 0]['period'].iloc[0]
    st.error(f"""
    **Critical Finding:** Real wages turned negative for the first time in 
    **{first_negative}**. Despite nominal wage increases of **{latest_wpi:.1f}%**, 
    CPI growth of **{latest_cpi:.2f}%** means workers lost **{abs(latest_real_wage):.2f}%** 
    purchasing power. This quantifies the household financial pressure requiring 
    policy response.
    """)

    if scene_nav == "All Scenes":
        st.markdown("---")

# ============================================================
# SCENE 4: THE DEEPER MOTIVE
# ============================================================
if scene_nav in ["All Scenes", "Scene 4: Deeper Motive"]:
    st.markdown('## <span style="color:#6BAEDB; font-size:1.1em">●</span> Scene 4: The Deeper Motive', unsafe_allow_html=True)
    st.subheader("Regional CPI Inequality - Perth Bears the Brunt")
    st.info("Use the **City Filter** in the sidebar to highlight a specific city on the chart below.")

    if df_cpi is not None:
        cities_list = ['sydney', 'melbourne', 'brisbane', 'adelaide', 'perth',
                       'hobart', 'darwin', 'canberra']
        city_avgs = []
        for city in cities_list:
            col_name = f'cpi_pct_{city}'
            if col_name in df_cpi.columns:
                avg = df_cpi[col_name].mean()
                city_avgs.append({'city': city.capitalize(), 'avg_cpi': avg})

        df_city_avg = pd.DataFrame(city_avgs).sort_values('avg_cpi', ascending=False)
        df_city_avg['rank'] = range(1, len(df_city_avg) + 1)

        if selected_city == 'Australia (All)':
            colors_city = [COLORS['danger'] if city == 'Perth' else COLORS['primary']
                           for city in df_city_avg['city']]
        else:
            colors_city = [COLORS['danger'] if city == selected_city else COLORS['secondary']
                           for city in df_city_avg['city']]

        fig4 = go.Figure()

        fig4.add_trace(go.Bar(
            y=df_city_avg['city'],
            x=df_city_avg['avg_cpi'],
            orientation='h',
            marker=dict(
                color=colors_city,
                line=dict(color='white', width=2),
                opacity=0.9
            ),
            text=[f"#{row['rank']} - {row['avg_cpi']:.2f}%"
                  for _, row in df_city_avg.iterrows()],
            textposition='outside',
            textfont=dict(size=13, family="Arial Black"),
            hovertemplate='<b>%{y}</b><br>Avg CPI: %{x:.2f}%<br>Rank: #%{text}<extra></extra>',
            showlegend=False
        ))

        start_date = df_cpi['date'].min().strftime('%Y')
        end_date = df_cpi['date'].max().strftime('%Y')

        fig4.update_layout(
            title=f"<b>Average Quarterly CPI Growth by City ({start_date}-{end_date})</b>",
            xaxis_title="<b>Average CPI Growth (%)</b>",
            yaxis_title="",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial", size=13, color='rgba(180,180,180,0.9)'),
            height=450,
            margin=dict(l=120, r=100, t=100, b=80)
        )

        fig4.update_xaxes(
            showgrid=False,
            showline=True, linewidth=1,
            linecolor='rgba(128,128,128,0.4)',
            mirror=True,
            ticks="outside", ticklen=6,
            tickcolor='rgba(128,128,128,0.4)',
            tickfont=dict()
        )
        fig4.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            showline=True, linewidth=1,
            linecolor='rgba(128,128,128,0.4)',
            mirror=True,
            zeroline=False,
            ticks="outside", ticklen=6,
            tickcolor='rgba(128,128,128,0.4)',
            tickfont=dict()
        )

        st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})

# --- City Time Series Chart ---
        st.markdown(f"#### CPI Trend Over Time - {selected_city if selected_city != 'Australia (All)' else 'Australia (National)'}")

        fig4b = go.Figure()

        if selected_city == 'Australia (All)':
            # Show all cities as light lines + Australia bold
            for city in cities_list:
                col_name = f'cpi_pct_{city}'
                if col_name in df_cpi.columns:
                    fig4b.add_trace(go.Scatter(
                        x=df_cpi['date'].dt.strftime('%Y-Q') + df_cpi['date'].dt.quarter.astype(str),
                        y=df_cpi[col_name],
                        mode='lines',
                        name=city.capitalize(),
                        line=dict(width=1, color='rgba(128,128,128,0.3)'),
                        showlegend=False
                    ))
            # Australia bold
            fig4b.add_trace(go.Scatter(
                x=df_cpi['date'].dt.strftime('%Y-Q') + df_cpi['date'].dt.quarter.astype(str),
                y=df_cpi['cpi_pct_australia'],
                mode='lines+markers',
                name='Australia',
                line=dict(width=3, color=COLORS['primary']),
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>CPI: %{y:.2f}%<extra></extra>'
            ))
        else:
            # Show selected city vs Australia
            city_col = f"cpi_pct_{selected_city.lower()}"
            if city_col in df_cpi.columns:
                fig4b.add_trace(go.Scatter(
                    x=df_cpi['date'].dt.strftime('%Y-Q') + df_cpi['date'].dt.quarter.astype(str),
                    y=df_cpi[city_col],
                    mode='lines+markers',
                    name=selected_city,
                    line=dict(width=3, color=COLORS['danger']),
                    marker=dict(size=8),
                    hovertemplate='<b>%{x}</b><br>' + selected_city + ': %{y:.2f}%<extra></extra>'
                ))
            fig4b.add_trace(go.Scatter(
                x=df_cpi['date'].dt.strftime('%Y-Q') + df_cpi['date'].dt.quarter.astype(str),
                y=df_cpi['cpi_pct_australia'],
                mode='lines+markers',
                name='Australia (National)',
                line=dict(width=2, color=COLORS['primary'], dash='dash'),
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>Australia: %{y:.2f}%<extra></extra>'
            ))

        fig4b.update_layout(
            title=f"<b>Quarterly CPI % Change - {selected_city if selected_city != 'Australia (All)' else 'All Cities vs National'}</b>",
            xaxis_title="<b>Quarter</b>",
            yaxis_title="<b>CPI % Change</b>",
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial", size=13),
            legend=dict(
                orientation="h", y=1.02, x=0.5, xanchor="center",
                bgcolor="rgba(0,0,0,0)",
                bordercolor='rgba(128,128,128,0.3)',
                borderwidth=1,
                font=dict(size=13)
            ),
            height=400,
            margin=dict(l=80, r=50, t=100, b=80)
        )
        fig4b.update_xaxes(
            showgrid=False, showline=True, linewidth=1,
            linecolor='rgba(128,128,128,0.4)', mirror=True,
            tickfont=dict()
        )
        fig4b.update_yaxes(
            showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)',
            showline=True, linewidth=1, linecolor='rgba(128,128,128,0.4)',
            mirror=True, zeroline=False, tickfont=dict()
        )

        st.plotly_chart(fig4b, use_container_width=True, config={'displayModeBar': False})

        perth_avg = df_city_avg[df_city_avg['city'] == 'Perth']['avg_cpi'].values[0]
        lowest_city = df_city_avg.iloc[-1]

        col1, col2, col3 = st.columns(3)
        highest_city = df_city_avg.iloc[0]
        lowest_city = df_city_avg.iloc[-1]
        spread = highest_city['avg_cpi'] - lowest_city['avg_cpi']

        with col1:
            sign1 = "+" if highest_city['avg_cpi'] > 0 else ""
            st.metric(f"Highest ({highest_city['city']})",
                      f"{sign1}{highest_city['avg_cpi']:.2f}%",
                      f"#{highest_city['rank']}",
                      delta_color="inverse")
        with col2:
            sign2 = "+" if lowest_city['avg_cpi'] > 0 else ""
            st.metric(f"Lowest ({lowest_city['city']})",
                      f"{sign2}{lowest_city['avg_cpi']:.2f}%",
                      f"#{lowest_city['rank']}",
                      delta_color="normal")
        with col3:
            sign3 = "+" if spread > 0 else ""
            st.metric("Regional Spread",
                      f"{sign3}{spread:.2f}%",
                      "Inequality gap")

        st.error(f"""
        **Geographic Disparity:** Perth experienced {perth_avg:.2f}% average quarterly CPI growth, 
        the highest nationally. This represents a {spread:.2f}% point gap from the 
        lowest city, indicating significant regional inequality in cost-of-living pressures.
        National policies may inadequately address localized inflation hotspots.
        """)
    else:
        st.warning("⚠️ CPI city data unavailable")

    if scene_nav == "All Scenes":
        st.markdown("---")

# ============================================================
# SCENE 5: THE VERDICT
# ============================================================
if scene_nav in ["All Scenes", "Scene 5: Verdict"]:
    st.markdown('## <span style="color:#5B8A4E; font-size:1.1em">●</span> Scene 5: The Verdict', unsafe_allow_html=True)
    st.subheader("Housing CPI - The Primary Culprit")

    fig5 = go.Figure()

    fig5.add_trace(go.Scatter(
        x=df['period'],
        y=df['housing_cpi_pct_change'],
        mode='lines+markers',
        name='Housing CPI',
        line=dict(color=COLORS['danger'], width=4),
        marker=dict(size=10, color=COLORS['danger'], symbol='square',
                    line=dict(width=2, color='white')),
        fill='tozeroy',
        fillcolor='rgba(231, 76, 60, 0.08)',
        hovertemplate='<b>%{x}</b><br>Housing: %{y:.2f}%<extra></extra>'
    ))

    fig5.add_trace(go.Scatter(
        x=df['period'],
        y=df['cpi_pct_australia'],
        mode='lines+markers',
        name='Overall CPI',
        line=dict(color=COLORS['primary'], width=4, dash='dash'),
        marker=dict(size=10, color=COLORS['primary'], symbol='diamond',
                    line=dict(width=2, color='white')),
        hovertemplate='<b>%{x}</b><br>Overall: %{y:.2f}%<extra></extra>'
    ))

    housing_avg = df['housing_cpi_pct_change'].mean()
    cpi_avg = df['cpi_pct_australia'].mean()

    fig5.add_hline(
        y=housing_avg, line_dash="dot", line_color=COLORS['danger'],
        annotation_text=f"Housing Avg: {housing_avg:.2f}%",
        annotation_position="right"
    )
    fig5.add_hline(
        y=cpi_avg, line_dash="dot", line_color=COLORS['primary'],
        annotation_text=f"CPI Avg: {cpi_avg:.2f}%",
        annotation_position="right"
    )

    fig5.update_layout(
        title="<b>Housing CPI vs Overall CPI: Isolating the Driver</b>",
        xaxis_title="<b>Quarter</b>",
        yaxis_title="<b>CPI Change (%)</b>",
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=13, color='rgba(180,180,180,0.9)'),
        legend=dict(
            orientation="h", y=1.02, x=0.5, xanchor="center",
            bgcolor="rgba(0,0,0,0)",
            bordercolor='rgba(128,128,128,0.3)',
            font=dict(size=13),
            borderwidth=1
        ),
        height=450,
        margin=dict(l=80, r=50, t=100, b=80)
    )

    fig5.update_xaxes(
        showgrid=False,
        showline=True, linewidth=1,
        linecolor='rgba(128,128,128,0.4)',
        mirror=True,
        ticks="outside", ticklen=6,
        tickcolor='rgba(128,128,128,0.4)',
        tickfont=dict()
    )
    fig5.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128,128,128,0.2)',
        showline=True, linewidth=1,
        linecolor='rgba(128,128,128,0.4)',
        mirror=True,
        zeroline=False,
        ticks="outside", ticklen=6,
        tickcolor='rgba(128,128,128,0.4)',
        tickfont=dict()
    )

    st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})
    
    # --- Second chart: Housing YoY vs Overall CPI YoY ---
    housing_yoy = pd.read_csv("housing_cpi_yoy.csv", parse_dates=["date"])
    cpi_yoy = pd.read_csv("cpi_yoy_quarterly_australia.csv", parse_dates=["date"])
    df_yoy = pd.merge(housing_yoy, cpi_yoy, on="date", how="inner")
    df_yoy["period"] = df_yoy["date"].dt.strftime("%Y-Q") + df_yoy["date"].dt.quarter.astype(str)

    fig5b = go.Figure()

    fig5b.add_trace(go.Scatter(
        x=df_yoy["period"],
        y=df_yoy["housing_cpi_yoy"],
        mode="lines+markers",
        name="Housing CPI YoY %",
        line=dict(color=COLORS["danger"], width=4),
        marker=dict(size=10, color=COLORS["danger"], symbol="square",
                    line=dict(width=2, color="white")),
        fill="tozeroy",
        fillcolor="rgba(231, 76, 60, 0.1)",
        hovertemplate="<b>%{x}</b><br>Housing YoY: %{y:.2f}%<extra></extra>"
    ))

    fig5b.add_trace(go.Scatter(
        x=df_yoy["period"],
        y=df_yoy["cpi_yoy_quarterly"],
        mode="lines+markers",
        name="Overall CPI YoY %",
        line=dict(color=COLORS["primary"], width=4, dash="dash"),
        marker=dict(size=10, color=COLORS["primary"], symbol="diamond",
                    line=dict(width=2, color="white")),
        hovertemplate="<b>%{x}</b><br>Overall YoY: %{y:.2f}%<extra></extra>"
    ))

    # Shade gap between housing and overall
    fig5b.add_trace(go.Scatter(
        x=df_yoy["period"].tolist() + df_yoy["period"].tolist()[::-1],
        y=df_yoy["housing_cpi_yoy"].tolist() + df_yoy["cpi_yoy_quarterly"].tolist()[::-1],
        fill="toself",
        fillcolor="rgba(231, 76, 60, 0.08)",
        line=dict(color="rgba(255,255,255,0)"),
        showlegend=True,
        name="Housing Premium",
        hoverinfo="skip"
    ))

    # Latest values
    latest_housing_yoy = df_yoy["housing_cpi_yoy"].iloc[-1]
    latest_overall_yoy = df_yoy["cpi_yoy_quarterly"].iloc[-1]
    latest_gap = latest_housing_yoy - latest_overall_yoy

    fig5b.update_layout(
        title="<b>Housing vs Overall CPI: Annual Growth (YoY %)</b>",
        xaxis_title="<b>Quarter</b>",
        yaxis_title="<b>Annual % Change (YoY)</b>",
        hovermode="x unified",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=13, color='rgba(180,180,180,0.9)'),
        legend=dict(
            orientation="h", y=1.02, x=0.5, xanchor="center",
            bgcolor="rgba(0,0,0,0)",
            bordercolor='rgba(128,128,128,0.3)',
            font=dict(size=13),
            borderwidth=1
        ),
        height=450,
        margin=dict(l=80, r=50, t=100, b=80)
    )

    fig5b.update_xaxes(
        showgrid=False,
        showline=True, linewidth=1,
        linecolor='rgba(128,128,128,0.4)',
        mirror=True,
        ticks="outside", ticklen=6,
        tickcolor='rgba(128,128,128,0.4)',
        tickfont=dict()
    )
    fig5b.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128,128,128,0.2)',
        showline=True, linewidth=1,
        linecolor='rgba(128,128,128,0.4)',
        mirror=True,
        zeroline=False,
        ticks="outside", ticklen=6,
        tickcolor='rgba(128,128,128,0.4)',
        tickfont=dict()
    )

    st.plotly_chart(fig5b, use_container_width=True, config={'displayModeBar': False})

    # YoY metric cards
    latest_date_label = df_yoy["date"].iloc[-1].strftime("%b-%y")

    col1b, col2b, col3b = st.columns(3)
    with col1b:
        sign1 = "+" if latest_housing_yoy > 0 else ""
        st.metric(f"Housing CPI YoY ({latest_date_label})",
                  f"{sign1}{latest_housing_yoy:.2f}%",
                  "Annual housing inflation",
                  delta_color="inverse")
    with col2b:
        sign2 = "+" if latest_overall_yoy > 0 else ""
        st.metric(f"Overall CPI YoY ({latest_date_label})",
                  f"{sign2}{latest_overall_yoy:.2f}%",
                  "Annual overall inflation",
                  delta_color="inverse")
    with col3b:
        sign3 = "+" if latest_gap > 0 else ""
        st.metric("Housing Premium",
                  f"{sign3}{latest_gap:.2f}%",
                  "Housing above overall CPI",
                  delta_color="inverse")

    st.warning(f"""
    **Annual View:** Housing costs rose {latest_housing_yoy:.2f}% annually 
    vs overall inflation of {latest_overall_yoy:.2f}% in {latest_date_label}. 
    Housing is rising {latest_housing_yoy/latest_overall_yoy:.1f}x faster than 
    overall CPI. The gap has widened to {latest_gap:.2f} percentage points, 
    making housing the single biggest driver of household financial pressure.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        sign1 = "+" if housing_avg > 0 else ""
        st.metric("Housing CPI Average",
                  f"{sign1}{housing_avg:.2f}%",
                  f"{'Above' if housing_avg > cpi_avg else 'Below'} Overall CPI",
                  delta_color="inverse")
    with col2:
        sign2 = "+" if cpi_avg > 0 else ""
        st.metric("Overall CPI Average",
                  f"{sign2}{cpi_avg:.2f}%",
                  f"{'Below' if cpi_avg < housing_avg else 'Above'} Housing",
                  delta_color="normal")
    with col3:
        ratio = housing_avg / cpi_avg if cpi_avg != 0 else 0
        st.metric("Housing/CPI Ratio",
                  f"{ratio:.2f}x",
                  "Multiplier",
                  delta_color="inverse")

    st.error(f"""
    **The Verdict:** Housing CPI grew {ratio:.2f}x faster than overall CPI on average. 
    As the single largest household expense, housing inflation is the primary driver of the 
    negative real wage growth identified in Scene 3. Broad economic stimulus will not address 
    this structural issue. Paula should recommend housing-specific interventions (supply, 
    rent controls, mortgage relief) as the most effective policy lever.
    """)

    if scene_nav == "All Scenes":
        st.markdown("---")

# ============================================================
# EXECUTIVE SUMMARY
# ============================================================
if scene_nav == "All Scenes":
    st.header("Executive Summary: The Complete Economic Picture")

    col1, col2, col3, col4 = st.columns(4)

    gdp_val = df.iloc[-1]['gdp_growth_pct']
    per_capita_val = df.iloc[-1]['gdp_per_capita_growth_pct']
    real_wage_val = df['real_wage_growth'].iloc[-2]
    housing_latest = df.iloc[-1]['housing_cpi_pct_change']

    with col1:
        sign1 = "+" if gdp_val > 0 else ""
        st.metric("GDP Growth",
                  f"{sign1}{gdp_val:.1f}%",
                  f"{'Macro positive' if gdp_val > 0 else 'Macro negative'}",
                  delta_color="normal" if gdp_val > 0 else "inverse")
    with col2:
        sign2 = "+" if per_capita_val > 0 else ""
        st.metric("Per Capita",
                  f"{sign2}{per_capita_val:.1f}%",
                  f"{'Individual positive' if per_capita_val > 0 else 'Individual negative'}",
                  delta_color="normal" if per_capita_val > 0 else "inverse")
    with col3:
        sign3 = "+" if real_wage_val > 0 else ""
        st.metric("Real Wages",
                  f"{sign3}{real_wage_val:.2f}%",
                  f"{'Purchasing power gained' if real_wage_val > 0 else 'Purchasing power lost'}",
                  delta_color="normal" if real_wage_val > 0 else "inverse")
    with col4:
        sign4 = "+" if housing_latest > 0 else ""
        st.metric("Housing CPI",
                  f"{sign4}{housing_latest:.2f}%",
                  "Primary driver",
                  delta_color="inverse")

    st.markdown("### The Detective Arc: Five Scenes to Policy Clarity")

# Dynamic values for summary
    gdp_val = df.iloc[-1]['gdp_growth_pct']
    per_capita_val = df.iloc[-1]['gdp_per_capita_growth_pct']
    real_wage_val = df['real_wage_growth'].iloc[-2]
    first_negative_q = df[df['real_wage_growth'] < 0]['period'].iloc[0]
    perth_avg = df_cpi[['cpi_pct_perth']].mean().values[0] if df_cpi is not None else 0
    employed_latest = f"{df_labour['employed_total_sa'].iloc[-1]/1000:.1f}M" if df_labour is not None else "14M+"
    housing_ratio = df['housing_cpi_pct_change'].mean() / df['cpi_pct_australia'].mean()

    st.markdown(f"""
    <div style='background-color: var(--secondary-background-color); 
                padding: 1.5rem; border-radius: 0.5rem; 
                border-left: 5px solid #3498DB; margin: 1rem 0;'>
    <h4 style='color: #3498DB; margin-top: 0;'>For Paula's Policy Briefing:</h4>
    
    <p><b>1. Crime Scene:</b> GDP grows {gdp_val:.1f}% while per capita at 
    {per_capita_val:+.1f}% - macro vs household divergence</p>
    
    <p><b>2. Red Herring:</b> Employment strong ({employed_latest} employed) - 
    but employment ≠ wage adequacy</p>
    
    <p><b>3. Culprit:</b> Real wages turned negative ({real_wage_val:.2f}% in 
    {first_negative_q}) - first quantifiable household pressure</p>
    
    <p><b>4. Deeper Motive:</b> Perth CPI highest ({perth_avg:.2f}%) - 
    geographic inequality compounds national trend</p>
    
    <p><b>5. Verdict:</b> Housing CPI {housing_ratio:.1f}x faster than overall CPI - 
    specific policy target identified</p>
    
    <p style='margin-bottom: 0;'><b>Defensible Recommendation:</b> Traditional 
    macro indicators mask household financial pressure. Real wage decline driven 
    primarily by housing inflation. Paula should advocate for housing-targeted 
    interventions rather than broad economic stimulus.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #95A5A6; padding: 1.5rem;'>
    <p style='margin: 0;'><em>Built with Streamlit | Data: Australian Bureau of Statistics (ABS)</em></p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.9em;'>National Accounts (5206) • Labour Force (6202) • WPI (6345) • CPI (6401)</p>
</div>
""", unsafe_allow_html=True)