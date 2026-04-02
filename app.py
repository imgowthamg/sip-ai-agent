import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import numpy as np

DB_PATH = '/home/user/Desktop/SIP/market_data.db'

# ============================================================================
# PAGE CONFIG & CUSTOM STYLING
# ============================================================================
st.set_page_config(
    page_title="Pro SIP Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Dark Theme with Neon Accents
custom_css = """
<style>
:root {
    --primary: #00D9FF;      /* Cyan accent */
    --secondary: #FF006E;    /* Magenta accent */
    --success: #00F5A0;      /* Mint */
    --warning: #FFB800;      /* Amber */
    --danger: #FF3860;       /* Red */
    --bg-dark: #0A0E27;      /* Deep navy */
    --bg-card: #1A1F3A;      /* Card background */
    --text-primary: #ECEFF4; /* Light text */
    --text-secondary: #8892B0;
    --border: #2D3561;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background: linear-gradient(135deg, var(--bg-dark) 0%, #0F1535 100%);
    color: var(--text-primary);
    font-family: 'Segoe UI', Trebuchet MS, sans-serif;
    overflow-x: hidden;
}

/* Streamlit Main Container */
.main {
    background: transparent !important;
}

.main-content {
    background: linear-gradient(135deg, var(--bg-dark) 0%, #0F1535 100%);
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--bg-dark) 0%, #0D1228 100%);
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] > div {
    background: transparent !important;
}

/* Text & Typography */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-weight: 700;
    letter-spacing: -0.5px;
}

p, span, div {
    color: var(--text-primary) !important;
}

/* Buttons with Glow */
button {
    background: linear-gradient(135deg, var(--primary), #00B4CC) !important;
    color: var(--bg-dark) !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 20px rgba(0, 217, 255, 0.3) !important;
    cursor: pointer !important;
}

button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 30px rgba(0, 217, 255, 0.6) !important;
}

button:active {
    transform: translateY(0) !important;
}

/* Metric Cards */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, var(--bg-card), rgba(0, 217, 255, 0.05)) !important;
    border: 1px solid rgba(0, 217, 255, 0.2) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    backdrop-filter: blur(10px) !important;
    transition: all 0.3s ease !important;
}

[data-testid="metric-container"]:hover {
    border-color: var(--primary) !important;
    box-shadow: 0 0 20px rgba(0, 217, 255, 0.2) !important;
    transform: translateY(-4px) !important;
}

/* Tabs */
[data-testid="stTabs"] {
    background: transparent !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: rgba(0, 217, 255, 0.05) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 5px !important;
}

.stTabs [data-baseweb="tab"] {
    color: var(--text-secondary) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

.stTabs [aria-selected="true"] {
    color: var(--bg-dark) !important;
    background: linear-gradient(135deg, var(--primary), #00B4CC) !important;
}

/* Input Fields */
input, textarea, select {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
    padding: 10px 15px !important;
    transition: all 0.2s ease !important;
}

input:focus, textarea:focus, select:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 15px rgba(0, 217, 255, 0.3) !important;
}

/* Alert Boxes */
.stSuccess {
    background: rgba(0, 245, 160, 0.1) !important;
    border: 1px solid rgba(0, 245, 160, 0.3) !important;
    border-radius: 10px !important;
}

.stError {
    background: rgba(255, 56, 96, 0.1) !important;
    border: 1px solid rgba(255, 56, 96, 0.3) !important;
    border-radius: 10px !important;
}

.stWarning {
    background: rgba(255, 184, 0, 0.1) !important;
    border: 1px solid rgba(255, 184, 0, 0.3) !important;
    border-radius: 10px !important;
}

.stInfo {
    background: rgba(0, 217, 255, 0.1) !important;
    border: 1px solid rgba(0, 217, 255, 0.3) !important;
    border-radius: 10px !important;
}

/* Dividers */
hr {
    border-color: var(--border) !important;
}

/* Markdown */
.markdown-text-container {
    color: var(--text-primary) !important;
}

/* Plots */
.plotly-graph-div {
    filter: brightness(1.1);
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-dark);
}

::-webkit-scrollbar-thumb {
    background: var(--primary);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #00B4CC;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

@keyframes glow {
    0%, 100% { box-shadow: 0 0 20px rgba(0, 217, 255, 0.3); }
    50% { box-shadow: 0 0 30px rgba(0, 217, 255, 0.6); }
}

.animated {
    animation: fadeIn 0.6s ease-out;
}

.live-indicator {
    animation: pulse 2s infinite;
}

.glow-effect {
    animation: glow 2s infinite;
}

/* Badge */
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    background: linear-gradient(135deg, var(--primary), #00B4CC);
    color: var(--bg-dark);
}

.badge-success {
    background: linear-gradient(135deg, var(--success), #00D97F);
}

.badge-danger {
    background: linear-gradient(135deg, var(--danger), #FF1744);
}

.badge-warning {
    background: linear-gradient(135deg, var(--warning), #FFA000);
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_nifty_value(nifty_json):
    """Extract NIFTYBEES value from JSON"""
    try:
        data = json.loads(nifty_json)
        return data.get("NIFTYBEES.NS", 0)
    except:
        return float(nifty_json) if nifty_json else 0

def parse_sentiment(text):
    """Parse sentiment from AI summary"""
    if "SENTIMENT:" in text:
        parts = text.split("SENTIMENT:")
        analysis = parts[0].strip()
        sentiment = parts[1].strip().replace(".", "").capitalize()
    else:
        analysis, sentiment = text, "Neutral"
    return analysis, sentiment

def render_sentiment_badge(sentiment):
    """Render sentiment with color coding"""
    if "Bullish" in sentiment:
        return f'<span class="badge badge-success">🚀 {sentiment}</span>'
    elif "Bearish" in sentiment:
        return f'<span class="badge badge-danger">📉 {sentiment}</span>'
    else:
        return f'<span class="badge badge-warning">⚖️ {sentiment}</span>'

def create_enhanced_price_chart(df):
    """Create beautiful price chart with Plotly"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['chart_price'],
        mode='lines+markers',
        name='NIFTYBEES',
        line=dict(
            color='#00D9FF',
            width=3,
            shape='spline'
        ),
        marker=dict(
            size=8,
            color='#00D9FF',
            symbol='circle',
            line=dict(width=2, color='#0A0E27')
        ),
        fill='tozeroy',
        fillcolor='rgba(0, 217, 255, 0.1)',
        hovertemplate='<b>%{x}</b><br>₹%{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': '<b>📊 Intraday & Historical Movement</b>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#ECEFF4'}
        },
        xaxis=dict(
            gridcolor='rgba(45, 53, 97, 0.3)',
            showgrid=True,
            zeroline=False,
            title=dict(text='Date & Time', font=dict(size=12, color='#8892B0')),
            tickfont=dict(size=11, color='#8892B0')
        ),
        yaxis=dict(
            gridcolor='rgba(45, 53, 97, 0.3)',
            showgrid=True,
            zeroline=False,
            title=dict(text='Price (₹)', font=dict(size=12, color='#8892B0')),
            tickfont=dict(size=11, color='#8892B0')
        ),
        hovermode='x unified',
        plot_bgcolor='rgba(10, 14, 39, 0.5)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(family='Segoe UI', color='#ECEFF4'),
        margin=dict(l=50, r=50, t=80, b=50),
        height=500
    )
    
    return fig

def create_price_distribution_chart(df):
    """Create histogram of price distribution"""
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=df['chart_price'],
        nbinsx=20,
        marker=dict(
            color='#FF006E',
            line=dict(color='#ECEFF4', width=1)
        ),
        opacity=0.75,
        hovertemplate='Price Range: ₹%{x:.2f}<br>Occurrences: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': '<b>📈 Price Distribution</b>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#ECEFF4'}
        },
        xaxis=dict(
            title=dict(text='Price (₹)', font=dict(size=12, color='#8892B0')),
            tickfont=dict(size=11, color='#8892B0'),
            gridcolor='rgba(45, 53, 97, 0.3)'
        ),
        yaxis=dict(
            title=dict(text='Frequency', font=dict(size=12, color='#8892B0')),
            tickfont=dict(size=11, color='#8892B0'),
            gridcolor='rgba(45, 53, 97, 0.3)'
        ),
        plot_bgcolor='rgba(10, 14, 39, 0.5)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(family='Segoe UI', color='#ECEFF4'),
        showlegend=False,
        height=400
    )
    
    return fig

# ============================================================================
# MAIN APP
# ============================================================================

# Header with gradient
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("""
    <div style='animation: fadeIn 0.8s ease-out;'>
    <h1 style='font-size: 3em; margin-bottom: 0.2em;'>
        📈 Pro SIP Intelligence
    </h1>
    <p style='color: #8892B0; font-size: 1.1em; margin: 0;'>
        Hourly Market Analysis • Airflow &  Local AI
    </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='text-align: right; padding-top: 20px;'>
    <div class='live-indicator' style='
        display: inline-block;
        padding: 10px 20px;
        background: rgba(0, 245, 160, 0.15);
        border: 1px solid rgba(0, 245, 160, 0.4);
        border-radius: 20px;
        color: #00F5A0;
        font-weight: 600;
        font-size: 0.95em;
    '>
        🟢 LIVE
    </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Sidebar Controls
with st.sidebar:
    st.markdown("""
    <h2 style='text-align: center; margin-bottom: 1.5em; font-size: 1.8em;'>
        ⚙️ Controls
    </h2>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with col2:
        st.write("")  # Spacing
    
    st.markdown("---")
    
    # Data refresh info
    st.markdown("""
    <div style='
        background: rgba(0, 217, 255, 0.1);
        border-left: 3px solid #00D9FF;
        padding: 12px;
        border-radius: 6px;
        font-size: 0.9em;
        color: #8892B0;
    '>
    <strong>ℹ️ Dashboard Info</strong><br>
    Updates: Hourly<br>
    Source: Airflow DAG<br>
    AI Model
    </div>
    """, unsafe_allow_html=True)

# Main Content
try:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM daily_briefings ORDER BY date ASC",
        conn
    )
    conn.close()

    if not df.empty:
        latest = df.iloc[-1]
        all_prices = json.loads(latest['nifty_price'])
        nifty_val = all_prices.get("NIFTYBEES.NS", 0)
        
        # Calculate price stats
        df['chart_price'] = df['nifty_price'].apply(get_nifty_value)
        current_price = df['chart_price'].iloc[-1]
        prev_price = df['chart_price'].iloc[-2] if len(df) > 1 else current_price
        price_change = current_price - prev_price
        price_change_pct = (price_change / prev_price * 100) if prev_price != 0 else 0

        # ====================================================================
        # SIDEBAR WATCHLIST
        # ====================================================================
        with st.sidebar:
            st.markdown("---")
            st.markdown("""
            <h3 style='margin-bottom: 1em; font-size: 1.3em;'>
                🚀 Watchlist
            </h3>
            """, unsafe_allow_html=True)
            
            watchlist_cols = st.columns(2)
            for idx, (stock, val) in enumerate(list(all_prices.items())[:4]):
                col = watchlist_cols[idx % 2]
                with col:
                    stock_name = stock.split('.')[0]
                    st.markdown(f"""
                    <div style='
                        background: rgba(0, 217, 255, 0.1);
                        border: 1px solid rgba(0, 217, 255, 0.2);
                        padding: 12px;
                        border-radius: 8px;
                        margin-bottom: 10px;
                    '>
                    <div style='color: #8892B0; font-size: 0.9em; margin-bottom: 5px;'>
                        {stock_name}
                    </div>
                    <div style='
                        color: #00D9FF;
                        font-size: 1.3em;
                        font-weight: 700;
                    '>
                        ₹{val:.2f}
                    </div>
                    </div>
                    """, unsafe_allow_html=True)

        # ====================================================================
        # KEY METRICS
        # ====================================================================
        st.markdown("""
        <h2 style='margin-top: 2em; margin-bottom: 1.5em; font-size: 1.5em;'>
            📊 Key Metrics
        </h2>
        """, unsafe_allow_html=True)
        
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            st.metric(
                label="💰 NIFTYBEES Price",
                value=f"₹{current_price:.2f}",
                delta=f"₹{price_change:.2f} ({price_change_pct:+.2f}%)"
            )
        
        with m2:
            st.metric(
                label="🕐 Last Update",
                value=latest['date'],
                delta="Now"
            )
        
        with m3:
            st.metric(
                label="📈 24h High",
                value=f"₹{df['chart_price'].tail(24).max():.2f}",
                delta=f"vs Now"
            )
        
        with m4:
            st.metric(
                label="📉 24h Low",
                value=f"₹{df['chart_price'].tail(24).min():.2f}",
                delta=f"vs Now"
            )

        # ====================================================================
        # TABBED CONTENT
        # ====================================================================
        tab1, tab2, tab3 = st.tabs(["📰 Current Briefing", "📊 Price Analysis", "💡 Insights"])

        with tab1:
            st.markdown("""
            <h3 style='margin-bottom: 1.5em; font-size: 1.3em;'>
                Latest Market Briefing
            </h3>
            """, unsafe_allow_html=True)
            
            # Sentiment
            analysis, sentiment = parse_sentiment(latest['ai_summary'])
            st.markdown(render_sentiment_badge(sentiment), unsafe_allow_html=True)
            
            st.markdown("---")
            
            # AI Analysis
            st.markdown("""
            <div style='
                background: linear-gradient(135deg, rgba(0, 217, 255, 0.1), rgba(255, 0, 110, 0.05));
                border: 1px solid rgba(0, 217, 255, 0.2);
                padding: 20px;
                border-radius: 12px;
                margin: 1.5em 0;
            '>
            <h4 style='margin-bottom: 1em; color: #00D9FF;'>🤖 AI Analysis</h4>
            """ + f"<p style='color: #ECEFF4; line-height: 1.6;'>{analysis}</p>" + """
            </div>
            """, unsafe_allow_html=True)
            
            # Headlines
            st.markdown("""
            <h4 style='margin-top: 2em; margin-bottom: 1.5em; font-size: 1.15em;'>
                📰 Latest Headlines
            </h4>
            """, unsafe_allow_html=True)
            
            headlines = latest['headlines'].split('\n')
            cols = st.columns(1)
            
            for headline in headlines:
                if headline.strip():
                    clean_headline = headline.strip('- ')
                    st.markdown(f"""
                    <div style='
                        background: rgba(255, 0, 110, 0.05);
                        border-left: 3px solid #FF006E;
                        padding: 12px 16px;
                        border-radius: 6px;
                        margin-bottom: 10px;
                        color: #ECEFF4;
                    '>
                    🔹 {clean_headline}
                    </div>
                    """, unsafe_allow_html=True)

        with tab2:
            st.markdown("""
            <h3 style='margin-bottom: 1.5em; font-size: 1.3em;'>
                Price Movement & Trends
            </h3>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Main price chart (last 24 records)
                chart_df = df.tail(24).copy()
                fig = create_enhanced_price_chart(chart_df)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("""
                <div style='
                    background: rgba(0, 217, 255, 0.1);
                    border: 1px solid rgba(0, 217, 255, 0.2);
                    padding: 16px;
                    border-radius: 10px;
                    height: 100%;
                '>
                <h4 style='margin-bottom: 1em; color: #00D9FF;'>Stats</h4>
                <div style='color: #8892B0; font-size: 0.95em; line-height: 2;'>
                <div><strong>Mean:</strong> ₹""" + f"{df['chart_price'].mean():.2f}" + """</div>
                <div><strong>Std Dev:</strong> ₹""" + f"{df['chart_price'].std():.2f}" + """</div>
                <div><strong>Volatility:</strong>""" + f"{((df['chart_price'].std() / df['chart_price'].mean()) * 100):.2f}%" + """</div>
                <div><strong>Records:</strong>""" + f"{len(df)}" + """</div>
                </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Price distribution
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                fig_dist = create_price_distribution_chart(df)
                st.plotly_chart(fig_dist, use_container_width=True)
            
            with col2:
                st.markdown("""
                <div style='
                    background: linear-gradient(135deg, rgba(255, 184, 0, 0.1), rgba(255, 0, 110, 0.05));
                    border: 1px solid rgba(255, 184, 0, 0.2);
                    padding: 20px;
                    border-radius: 12px;
                    height: 100%;
                '>
                <h4 style='margin-bottom: 1.5em; color: #FFB800;'>📌 Quick Insights</h4>
                <ul style='color: #ECEFF4; line-height: 2; list-style: none; padding: 0;'>
                <li>✓ Price Range: ₹""" + f"{df['chart_price'].min():.2f} - ₹{df['chart_price'].max():.2f}" + """</li>
                <li>✓ Avg Daily Vol: ₹""" + f"{df['chart_price'].diff().abs().mean():.2f}" + """</li>
                <li>✓ Data Points: """ + f"{len(df)}" + """</li>
                <li>✓ Coverage: """ + f"{df['date'].iloc[0]} to {df['date'].iloc[-1]}" + """</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)

        with tab3:
            st.markdown("""
            <h3 style='margin-bottom: 1.5em; font-size: 1.3em;'>
                Market Insights & Recommendations
            </h3>
            """, unsafe_allow_html=True)
            
            # Calculate some insights
            recent_trend = "📈 Uptrend" if price_change > 0 else "📉 Downtrend"
            volatility = ((df['chart_price'].std() / df['chart_price'].mean()) * 100)
            volatility_level = "🔴 High" if volatility > 2 else "🟡 Medium" if volatility > 1 else "🟢 Low"
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div style='
                    background: rgba(0, 245, 160, 0.1);
                    border: 1px solid rgba(0, 245, 160, 0.3);
                    padding: 16px;
                    border-radius: 10px;
                    text-align: center;
                '>
                <h4 style='color: #00F5A0; margin-bottom: 0.5em;'>{recent_trend}</h4>
                <p style='color: #8892B0; margin: 0;'>Recent Movement</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style='
                    background: rgba(255, 184, 0, 0.1);
                    border: 1px solid rgba(255, 184, 0, 0.3);
                    padding: 16px;
                    border-radius: 10px;
                    text-align: center;
                '>
                <h4 style='color: #FFB800; margin-bottom: 0.5em;'>{volatility_level}</h4>
                <p style='color: #8892B0; margin: 0;'>Volatility Level</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style='
                    background: rgba(0, 217, 255, 0.1);
                    border: 1px solid rgba(0, 217, 255, 0.3);
                    padding: 16px;
                    border-radius: 10px;
                    text-align: center;
                '>
                <h4 style='color: #00D9FF; margin-bottom: 0.5em;'>💡 Recommendation</h4>
                <p style='color: #8892B0; margin: 0;'>
                """ + ("Strong Buy" if price_change_pct > 2 else "Hold" if price_change_pct > -2 else "Review Position") + """
                </p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Detailed insights
            st.markdown("""
            <h4 style='margin-bottom: 1em; margin-top: 1.5em;'>Detailed Analysis</h4>
            <div style='
                background: rgba(0, 217, 255, 0.08);
                border: 1px solid rgba(0, 217, 255, 0.2);
                padding: 20px;
                border-radius: 10px;
                line-height: 1.8;
                color: #ECEFF4;
            '>
            <strong style='color: #00D9FF;'>📊 Technical Insights:</strong><br>
            """ + f"The market shows a {recent_trend.split()[0]} trend with current volatility at {volatility:.2f}%. " + \
            f"Price has moved ₹{abs(price_change):.2f} ({abs(price_change_pct):.2f}%) in the recent period. " + \
            "Consider your risk tolerance when making SIP contributions." + """
            </div>
            """, unsafe_allow_html=True)

    else:
        st.warning("""
        ⚠️ No data found in the database.
        
        Please ensure the Airflow DAG has been triggered and data has been populated in the database.
        """)

except Exception as e:
    st.error(f"""
    ❌ Error Loading Dashboard
    
    **Details:** {str(e)}
    
    Please check:
    - Database connection
    - Database file exists at: {DB_PATH}
    - Data has been populated
    """)