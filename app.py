import streamlit as st

st.set_page_config(
    page_title="PulseGrid",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: "Inter", sans-serif;
    }

    .stApp {
        background: #07111f;
        color: #f4f7fb;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.4rem 0 1.8rem 0;
        border-bottom: 1px solid #1c2a3c;
        margin-bottom: 2.2rem;
    }

    .brand {
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.45rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: #ffffff;
    }

    .brand-subtitle {
        color: #7f91a8;
        font-size: 0.78rem;
        margin-left: 0.7rem;
        letter-spacing: 0.03em;
    }

    .live-status {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        color: #9aabbe;
        font-size: 0.8rem;
    }

    .live-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #28d17c;
        display: inline-block;
    }

    .hero {
        padding: 1rem 0 2rem 0;
    }

    .hero-label {
        color: #ff5b5b;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.7rem;
    }

    .hero-title {
        font-family: "Space Grotesk", sans-serif;
        font-size: clamp(2.4rem, 5vw, 4.5rem);
        line-height: 0.98;
        font-weight: 700;
        letter-spacing: -0.045em;
        margin: 0;
        color: #ffffff;
    }

    .hero-text {
        max-width: 720px;
        color: #9eafc3;
        font-size: 1rem;
        line-height: 1.7;
        margin-top: 1.1rem;
    }

    .section-title {
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.35rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.3rem;
    }

    .section-text {
        color: #8293a8;
        font-size: 0.88rem;
        margin-bottom: 1.2rem;
    }

    .panel {
        background: #0d1929;
        border: 1px solid #1d2c40;
        border-radius: 16px;
        padding: 1.25rem;
        height: 100%;
    }

    .panel-title {
        font-family: "Space Grotesk", sans-serif;
        color: #ffffff;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }

    .status-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.65rem 0;
        border-bottom: 1px solid #1a293b;
        color: #9aabbe;
        font-size: 0.83rem;
    }

    .status-row:last-child {
        border-bottom: none;
    }

    .status-ready {
        color: #28d17c;
        font-weight: 600;
    }

    .status-pending {
        color: #f0b44d;
        font-weight: 600;
    }

    .metric-box {
        background: #0d1929;
        border: 1px solid #1d2c40;
        border-radius: 14px;
        padding: 1rem;
        min-height: 105px;
    }

    .metric-label {
        color: #8192a8;
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.45rem;
    }

    .metric-value {
        color: #ffffff;
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.65rem;
        font-weight: 600;
    }

    .metric-description {
        color: #71839a;
        font-size: 0.75rem;
        margin-top: 0.2rem;
    }

    .info-banner {
        background: #101f32;
        border: 1px solid #20344b;
        border-left: 3px solid #ff5b5b;
        border-radius: 10px;
        padding: 0.9rem 1rem;
        color: #a7b6c8;
        font-size: 0.84rem;
        line-height: 1.6;
        margin: 1rem 0;
    }

    .map-placeholder {
        min-height: 480px;
        background:
            linear-gradient(rgba(13, 25, 41, 0.82), rgba(13, 25, 41, 0.82)),
            repeating-linear-gradient(
                45deg,
                #101d2d,
                #101d2d 10px,
                #0f1b2b 10px,
                #0f1b2b 20px
            );
        border: 1px solid #1d2c40;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 2rem;
    }

    .map-placeholder-title {
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.3rem;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }

    .map-placeholder-text {
        max-width: 500px;
        color: #8192a8;
        font-size: 0.85rem;
        line-height: 1.6;
    }

    div.stButton > button {
        background: #e84c4c;
        color: #ffffff;
        border: none;
        border-radius: 9px;
        min-height: 2.8rem;
        font-weight: 600;
        transition: 0.2s ease;
    }

    div.stButton > button:hover {
        background: #ff5b5b;
        color: #ffffff;
        border: none;
    }

    div.stButton > button:focus {
        box-shadow: 0 0 0 2px #07111f, 0 0 0 4px #ff5b5b;
    }

    .stSelectbox label,
    .stNumberInput label,
    .stDateInput label,
    .stTimeInput label {
        color: #a9b8c9 !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
    }

    div[data-baseweb="select"] > div {
        background: #101d2d;
        border-color: #26384d;
        color: #ffffff;
        border-radius: 9px;
    }

    input {
        background: #101d2d !important;
        color: #ffffff !important;
        border-color: #26384d !important;
        border-radius: 9px !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
        border-bottom: 1px solid #1c2a3c;
    }

    .stTabs [data-baseweb="tab"] {
        color: #7f91a8;
        background: transparent;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        color: #ffffff;
    }

    .footer {
        border-top: 1px solid #1c2a3c;
        margin-top: 3rem;
        padding-top: 1.2rem;
        color: #63758b;
        font-size: 0.72rem;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def metric_box(label, value, description):
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def status_row(label, value, status_class):
    st.markdown(
        f"""
        <div class="status-row">
            <span>{label}</span>
            <span class="{status_class}">{value}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown(
    """
    <div class="topbar">
        <div>
            <span class="brand">PULSEGRID</span>
            <span class="brand-subtitle">EMERGENCY RESOURCE INTELLIGENCE</span>
        </div>
        <div class="live-status">
            <span class="live-dot"></span>
            SYSTEM READY
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="hero">
        <div class="hero-label">Emergency Medical Planning</div>
        <h1 class="hero-title">Smarter ambulance<br>positioning.</h1>
        <div class="hero-text">
            Analyze emergency demand, weather, traffic, road conditions,
            geography, and available resources to determine where ambulances
            should be positioned for improved predicted coverage and response.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">Configure analysis</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-text">Select the region and conditions you want PulseGrid to analyze.</div>',
    unsafe_allow_html=True
)

left, middle, right = st.columns([1.4, 1.4, 0.8], gap="medium")

with left:
    st.selectbox(
        "Location",
        [
            "Charlotte, NC",
            "Raleigh, NC",
            "Durham, NC",
            "Greensboro, NC",
            "Winston-Salem, NC"
        ],
        index=0
    )

with middle:
    st.selectbox(
        "Analysis conditions",
        [
            "Current conditions",
            "Historical conditions",
            "Custom scenario"
        ],
        index=0
    )

with right:
    st.number_input(
        "Available ambulances",
        min_value=1,
        max_value=100,
        value=12,
        step=1
    )

date_col, time_col, action_col = st.columns([1, 1, 0.8], gap="medium")

with date_col:
    st.date_input("Analysis date")

with time_col:
    st.time_input("Analysis time")

with action_col:
    st.markdown("<div style='height: 1.75rem'></div>", unsafe_allow_html=True)
    analyze = st.button("Run analysis", use_container_width=True)

st.markdown(
    """
    <div class="info-banner">
        PulseGrid will prioritize live authoritative data where available.
        Historical records and appropriate fallback data will only be used
        when the preferred source is unavailable.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">Data readiness</div>',
    unsafe_allow_html=True
)

status_1, status_2, status_3, status_4 = st.columns(4, gap="medium")

with status_1:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Weather</div>', unsafe_allow_html=True)
    status_row("Data source", "Pending", "status-pending")
    status_row("Live conditions", "Pending", "status-pending")
    st.markdown("</div>", unsafe_allow_html=True)

with status_2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Traffic</div>', unsafe_allow_html=True)
    status_row("Data source", "Pending", "status-pending")
    status_row("Current conditions", "Pending", "status-pending")
    st.markdown("</div>", unsafe_allow_html=True)

with status_3:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">EMS data</div>', unsafe_allow_html=True)
    status_row("Historical records", "Pending", "status-pending")
    status_row("Geographic data", "Pending", "status-pending")
    st.markdown("</div>", unsafe_allow_html=True)

with status_4:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Road network</div>', unsafe_allow_html=True)
    status_row("Network data", "Pending", "status-pending")
    status_row("Closures", "Pending", "status-pending")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)

map_col, metrics_col = st.columns([2.1, 1], gap="medium")

with map_col:
    st.markdown(
        '<div class="section-title">Emergency coverage map</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="map-placeholder">
            <div>
                <div class="map-placeholder-title">
                    Interactive map will appear here
                </div>
                <div class="map-placeholder-text">
                    The map will display emergency demand, EMS stations,
                    hospitals, traffic conditions, road closures, baseline
                    ambulance positions, and optimized deployment locations.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with metrics_col:
    st.markdown(
        '<div class="section-title">Analysis overview</div>',
        unsafe_allow_html=True
    )

    metric_box(
        "Predicted demand",
        "--",
        "emergency demand for selected period"
    )

    st.markdown("<div style='height: 0.7rem'></div>", unsafe_allow_html=True)

    metric_box(
        "Baseline response",
        "--",
        "predicted average response time"
    )

    st.markdown("<div style='height: 0.7rem'></div>", unsafe_allow_html=True)

    metric_box(
        "Optimized response",
        "--",
        "predicted average response time"
    )

    st.markdown("<div style='height: 0.7rem'></div>", unsafe_allow_html=True)

    metric_box(
        "Estimated improvement",
        "--",
        "baseline compared with optimized"
    )

st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Deployment",
        "Conditions",
        "Why this deployment",
        "Quantum engine"
    ]
)

with tab1:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Baseline vs. optimized deployment</div>
            <p style="color:#8192a8; line-height:1.7; font-size:0.85rem;">
                Once the analysis runs, this section will compare the existing
                or defined baseline deployment with the proposed ambulance
                positions and quantify the predicted difference.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with tab2:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Local conditions</div>
            <p style="color:#8192a8; line-height:1.7; font-size:0.85rem;">
                Current weather, traffic, road closures, historical traffic
                patterns, and other validated conditions will appear here.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with tab3:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Why did PulseGrid choose these locations?</div>
            <p style="color:#8192a8; line-height:1.7; font-size:0.85rem;">
                The application will generate a factual explanation based on
                the demand prediction, travel-time calculations, weather,
                traffic, road conditions, and optimization results.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with tab4:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Quantum optimization</div>
            <p style="color:#8192a8; line-height:1.7; font-size:0.85rem;">
                Qiskit optimization details, problem size, constraints,
                quantum configuration, and comparison with the classical
                solution will appear here after the optimization engine is
                connected.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

if analyze:
    st.session_state["analysis_started"] = True
    st.success(
        "Analysis configuration saved. The data and optimization engines will run once they are connected."
    )

st.markdown(
    """
    <div class="footer">
        PulseGrid is a decision-support research prototype. Recommendations
        are based on available data and do not replace emergency dispatch
        decisions.
    </div>
    """,
    unsafe_allow_html=True
)
