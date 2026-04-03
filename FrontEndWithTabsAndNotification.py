import tempfile
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from rasterio.features import rasterize
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table
from shapely.ops import transform

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="Mumbai Green Dashboard", page_icon="ÃƒÂ°Ã…Â¸Ã…â€™Ã‚Â¿", layout="wide")

# ===============================
# PREMIUM CSS (FULLY UPDATED)
# ===============================
st.markdown(
    """
<style>

/* ===== BACKGROUND ===== */
.stApp{
background-image: url("https://images.unsplash.com/photo-1542273917363-3b1817f69a2d?q=80&w=2074&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
background-size: cover;
background-position: center;
background-repeat: no-repeat;
background-attachment: fixed;
min-height: 100vh;
}

/* Soft overlay so text is readable over photo */
.stApp::before{
content: "";
position: fixed;
inset: 0;
background: rgba(255,255,255,0.0);
z-index: 0;
pointer-events: none;
}

/* Keep all app content above overlay */
.main,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"]{
position: relative;
z-index: 1;
}

/* Remove extra top white gap from Streamlit chrome */
header[data-testid="stHeader"]{
height: 0rem !important;
min-height: 0rem !important;
background: transparent !important;
}

[data-testid="stAppViewContainer"]{
padding-top: 0rem !important;
margin-top: 0rem !important;
}

/* Strong readability panel behind full main content */
[data-testid="stAppViewContainer"] .main .block-container,
[data-testid="stAppViewBlockContainer"],
.main .block-container{
background: rgba(255,255,255,0.98) !important;
border-radius: 16px;
padding: 0.5rem 1.25rem 1.5rem 1.25rem;
box-shadow: 0 8px 24px rgba(0,0,0,0.18);
}

/* Improve readability of default Streamlit widgets */
[data-testid="metric-container"],
[data-testid="stMetric"],
.stMetric,
[data-testid="stDataFrame"],
[data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlockBorderWrapper"],
.stProgress{
background: rgba(255,255,255,0.98) !important;
border-radius: 12px;
padding: 8px;
}

/* Keep bordered containers readable (used by chatbot section) */
[data-testid="stVerticalBlockBorderWrapper"]{
background: rgba(255,255,255,0.98) !important;
border: 1px solid #cfe8d8 !important;
border-radius: 14px !important;
}

/* Dark readable text for chatbot labels/caption */
[data-testid="stTextInput"] label,
[data-testid="stCaptionContainer"] p{
color: #0f172a !important;
font-weight: 600 !important;
}

[data-testid="stAppViewContainer"] .main .block-container p,
[data-testid="stAppViewContainer"] .main .block-container span,
[data-testid="stAppViewContainer"] .main .block-container label,
[data-testid="stAppViewContainer"] .main .block-container div{
color: #0f172a !important;
}

[data-testid="metric-container"] label,
[data-testid="metric-container"] [data-testid="stMetricValue"],
[data-testid="metric-container"] [data-testid="stMetricDelta"]{
color: #0f172a !important;
}

/* Opaque notification/success boxes */
[data-testid="stAlert"]{
background: rgba(255,255,255,0.98) !important;
color: #0f172a !important;
border: 1px solid #d1d5db !important;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"]{
background: linear-gradient(180deg,#06281c,#0f5132);
}

/* Sidebar labels and text remain white */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] h5,
[data-testid="stSidebar"] h6,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .st-emotion-cache-10trblm,
[data-testid="stSidebar"] .st-emotion-cache-16idsys {
color:#ffffff !important;
}

/* Sidebar button style for navigation clarity */
[data-testid="stSidebar"] .stButton > button{
background: rgba(255,255,255,0.12) !important;
border: 1px solid rgba(255,255,255,0.35) !important;
color: #ffffff !important;
border-radius: 10px !important;
font-weight: 600 !important;
}
[data-testid="stSidebar"] .stButton > button:hover{
background: rgba(255,255,255,0.22) !important;
}

/* Force active (primary) buttons to green */
.stButton > button[kind="primary"]{
background: #0b6f44 !important;
border: 1px solid #0b6f44 !important;
color: #ffffff !important;
}
.stButton > button[kind="primary"]:hover{
background: #0a5f3b !important;
border-color: #0a5f3b !important;
}

/* Dropdown selected value: black text on light box */
[data-testid="stSidebar"] div[data-baseweb="select"] > div{
background:#f4fff8 !important;
border:1px solid #cfe8d8 !important;
border-radius:10px !important;
}

[data-testid="stSidebar"] div[data-baseweb="select"] input,
[data-testid="stSidebar"] div[data-baseweb="select"] span,
[data-testid="stSidebar"] div[data-baseweb="select"] div{
color:#111111 !important;
}

/* ===== HEADER ===== */
.app-banner{
border-radius:16px;
padding:1rem 1.2rem;
margin-bottom:1rem;
background:linear-gradient(120deg,#0b6f44,#20a063);
color:white;
box-shadow:0 10px 26px rgba(13,67,43,0.23);
}

/* ===== GLASS CARD ===== */
.card{
background: rgba(255,255,255,0.88);
padding:18px;
border-radius:18px;
backdrop-filter: blur(6px);
box-shadow:0 10px 30px rgba(0,0,0,0.08);
margin-bottom:12px;
border-left:6px solid #0b6f44;
}

/* ===== ALERT CARD ===== */
.alert-card{
background: linear-gradient(120deg,#ffeded,#fff5f5);
border-left:8px solid #e63946;
padding:18px;
border-radius:18px;
box-shadow:0 10px 30px rgba(230,57,70,0.18);
margin-bottom:15px;
}

/* ===== CHAT CARD ===== */
.chat-card{
background: #f8fffb;
border: 1px solid #cfe8d8;
border-left: 6px solid #0b6f44;
border-radius: 14px;
padding: 14px 16px;
margin-top: 14px;
}

/* ===== TABS STYLE ===== */
button[data-baseweb="tab"]{
color:#1f2937 !important;
font-weight:600;
border-radius:8px 8px 0 0;
padding:8px 14px;
background:rgba(255,255,255,0.72);
border-bottom:2px solid transparent !important;
}

button[data-baseweb="tab"]:hover{
background:rgba(11,111,68,0.12);
color:#111827 !important;
}

button[data-baseweb="tab"][aria-selected="true"]{
color:#0b6f44 !important;
border-bottom:3px solid #0b6f44 !important;
background:#ffffff;
}

/* Fix top toolbar text visibility */
[data-testid="stToolbar"] *{
color:#111827 !important;
}

</style>
""",
    unsafe_allow_html=True,
)

# ===============================
# TOP NAVIGATION STATE
# ===============================
if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"


def set_page(page_name: str):
    if st.session_state.active_page != page_name:
        st.session_state.active_page = page_name
        st.rerun()


nav_left, nav_right = st.columns([3.6, 2.4])
with nav_right:
    b1, b2, b3 = st.columns(3)
    if b1.button(
        "Dashboard",
        key="top_nav_dashboard",
        use_container_width=True,
        type="primary" if st.session_state.active_page == "Dashboard" else "secondary",
    ):
        set_page("Dashboard")
    if b2.button(
        "About Us",
        key="top_nav_about",
        use_container_width=True,
        type="primary" if st.session_state.active_page == "About Us" else "secondary",
    ):
        set_page("About Us")
    if b3.button(
        "Contact Us",
        key="top_nav_contact",
        use_container_width=True,
        type="primary" if st.session_state.active_page == "Contact Us" else "secondary",
    ):
        set_page("Contact Us")

# ===============================
# HEADER
# ===============================
st.markdown(
    """
<div class="app-banner">
<h1>Mumbai Ward-Wise Green Diffusion and AQI Dashboard</h1>
<p>Track greenery growth, compare ward performance, and prioritize interventions.</p>
</div>
""",
    unsafe_allow_html=True,
)

# ===============================
# LOAD DATA
# ===============================
@st.cache_data
def load_csv(path):
    return pd.read_csv(path).values


existing = load_csv("existing_map.csv")
final_map = load_csv("final_green_visibility.csv")
grid_size = existing.shape[0]

A_MAX = 220
BETA = 1.0

# ===============================
# SIDEBAR
# ===============================
st.sidebar.header("Green Controls")

threshold_value = st.sidebar.slider(
    "Minimum Green Intensity",
    float(existing.min()),
    float(existing.max()),
    float(np.mean(existing)),
)

wards = gpd.read_file("wards.geojson")
wards["NAME"] = wards["NAME"].str.strip()

selected_ward = st.sidebar.selectbox(
    "Select Ward",
    sorted(wards["NAME"].unique())
)

# ===============================
# NORMALIZE GEOMETRY
# ===============================
minx, miny, maxx, maxy = wards.total_bounds


def normalize_geometry(geom):
    def scale(x, y, z=None):
        x_norm = ((x - minx) / (maxx - minx)) * (grid_size - 1)
        y_norm = ((y - miny) / (maxy - miny)) * (grid_size - 1)
        return (x_norm, y_norm)

    return transform(scale, geom)


wards["geometry"] = wards["geometry"].apply(normalize_geometry)

ward_raster = rasterize(
    [(geom, idx + 1) for idx, geom in enumerate(wards.geometry)],
    out_shape=(grid_size, grid_size),
    fill=0,
    dtype=np.int32,
)

# ===============================
# CALCULATE RESULTS
# ===============================
existing_binary = (existing >= threshold_value).astype(int)
final_binary = (final_map >= threshold_value).astype(int)

ward_results = []

for idx, row in wards.iterrows():
    ward_id = idx + 1
    mask = ward_raster == ward_id
    total_cells = np.sum(mask)
    if total_cells == 0:
        continue

    existing_green = np.sum(existing_binary[mask])
    final_green = np.sum(final_binary[mask])

    before_percent = (existing_green / total_cells) * 100
    after_percent = (final_green / total_cells) * 100
    after_percent = max(after_percent, before_percent)
    increase = after_percent - before_percent

    baseline_aqi = np.clip(A_MAX - (BETA * before_percent), 80, 300)
    final_aqi = np.clip(A_MAX - (BETA * after_percent), 0, 500)
    aqi_improvement = baseline_aqi - final_aqi

    if final_aqi <= 50:
        cat = "Good"
    elif final_aqi <= 100:
        cat = "Satisfactory"
    elif final_aqi <= 200:
        cat = "Moderate"
    elif final_aqi <= 300:
        cat = "Poor"
    else:
        cat = "Very Poor"

    if increase < 2:
        policy = "High Priority Intervention Needed"
    elif increase < 5:
        policy = "Moderate Improvement - Strengthen Green Corridors"
    else:
        policy = "Satisfactory Growth - Maintain and Monitor"

    ward_results.append(
        {
            "Ward": row["NAME"],
            "Before %": round(before_percent, 2),
            "After %": round(after_percent, 2),
            "Increase %": round(increase, 2),
            "Baseline AQI": round(baseline_aqi, 2),
            "Final AQI": round(final_aqi, 2),
            "AQI Improvement": round(aqi_improvement, 2),
            "AQI Category": cat,
            "Policy Recommendation": policy,
        }
    )

results_df = pd.DataFrame(ward_results)
ward_data = results_df[results_df["Ward"] == selected_ward].iloc[0]

# ===============================
# SEVERE DEFICIT ALERT
# ===============================
SEVERE_THRESHOLD = 2
LOW_GREEN_THRESHOLD = 10

severe_wards = results_df[
    (results_df["Increase %"] < SEVERE_THRESHOLD)
    | (results_df["After %"] < LOW_GREEN_THRESHOLD)
]

# ===============================
# PDF FUNCTION
# ===============================
def generate_pdf(ward_info):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(temp_file.name)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("Mumbai Ward Green Diffusion and AQI Report", styles["Heading1"]))
    elements.append(Spacer(1, 0.5 * inch))
    data = [[k, str(v)] for k, v in ward_info.items()]
    elements.append(Table(data))
    doc.build(elements)
    return temp_file.name


def get_ward_chat_summary(ward_row):
    return (
        f"For {ward_row['Ward']}, green coverage increased from "
        f"{ward_row['Before %']}% to {ward_row['After %']}%, improving AQI "
        f"from {ward_row['Baseline AQI']} to {ward_row['Final AQI']}. "
        f"Recommendation: {ward_row['Policy Recommendation']}.\n\n"
        f"Ward Name: {ward_row['Ward']}\n"
        f"Green coverage before: {ward_row['Before %']}%\n"
        f"Green coverage after: {ward_row['After %']}%\n"
        f"Increase %: {ward_row['Increase %']}%\n"
        f"Baseline AQI: {ward_row['Baseline AQI']}\n"
        f"Final AQI: {ward_row['Final AQI']}\n"
        f"AQI category: {ward_row['AQI Category']}\n"
        f"Policy recommendation: {ward_row['Policy Recommendation']}"
    )


# ===============================
# PAGE ROUTING
# ===============================
if st.session_state.active_page == "Dashboard":
    if len(severe_wards) > 0:
        severe_list = ", ".join(severe_wards["Ward"].head(5))
        st.markdown(
            f"""
            <div class="alert-card">
             🚨 <b>URGENT GREEN DEFICIT ALERT</b><br><br>
            Immediate intervention required in:<br>{severe_list}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ===============================
    # CREATE TABS
    # ===============================
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Ward Overview", "Visualization", "Rankings", "Export Report", "Chatbot"]
    )

    # TAB 1
    with tab1:
        if selected_ward in severe_wards["Ward"].values:
            st.markdown(
                f"""
                <div class="alert-card">
                &#9888; <b>{selected_ward} is SEVERELY GREEN DEFICIT</b><br>
                Requires urgent plantation drives & green corridor recovery.
                </div>
                """,
                unsafe_allow_html=True,
            )

        c1, c2, c3 = st.columns(3)
        c1.metric("Previous Green Coverage", f"{ward_data['Before %']}%")
        c2.metric(
            "New Green Coverage",
            f"{ward_data['After %']}%",
            delta=f"+{ward_data['Increase %']}%",
        )
        c3.metric("Net Improvement", f"{ward_data['Increase %']}%")

        st.success(f"Policy Recommendation: {ward_data['Policy Recommendation']}")

        a1, a2, a3 = st.columns(3)
        a1.metric("Baseline AQI", ward_data["Baseline AQI"])
        a2.metric("Final AQI", ward_data["Final AQI"], delta=f"-{ward_data['AQI Improvement']}")
        a3.metric("AQI Category", ward_data["AQI Category"])

        st.progress(ward_data["Before %"] / 100)
        st.progress(ward_data["After %"] / 100)

    # TAB 2
    with tab2:
        ward_index = wards[wards["NAME"] == selected_ward].index[0]
        ward_id = ward_index + 1
        mask = ward_raster == ward_id
        difference_map = final_binary - existing_binary

        col1, col2, col3 = st.columns(3)

        def show_map(data, title, col, cmap):
            fig, ax = plt.subplots(figsize=(4, 4))
            img = ax.imshow(data * mask, cmap=cmap)
            ax.set_title(title)
            ax.set_xticks([])
            ax.set_yticks([])
            fig.colorbar(img, ax=ax)
            col.pyplot(fig)

        show_map(existing_binary, "Before", col1, "Greens")
        show_map(final_binary, "After", col2, "Greens")
        show_map(difference_map, "Change", col3, "RdYlGn")

    # TAB 3
    with tab3:
        ranking_df = results_df.sort_values("Increase %", ascending=False)
        st.dataframe(ranking_df, use_container_width=True)

        colors = []
        for w in ranking_df["Ward"]:
            if w == selected_ward:
                colors.append("#0b6f44")
            elif w in severe_wards["Ward"].values:
                colors.append("#e63946")
            else:
                colors.append("#a9dfbf")

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(ranking_df["Ward"], ranking_df["Increase %"], color=colors)
        plt.xticks(rotation=75, ha="right")
        st.pyplot(fig)

        aqi_ranking = results_df.sort_values("AQI Improvement", ascending=False)
        st.dataframe(aqi_ranking, use_container_width=True)

    # TAB 4
    with tab4:
        if st.button("Generate PDF Report"):
            pdf_path = generate_pdf(ward_data)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="Download PDF",
                    data=f,
                    file_name=f"{selected_ward}_Green_AQI_Report.pdf",
                    mime="application/pdf",
                )

    # TAB 5
    with tab5:
        st.markdown(
            """
            <div class="card" style="margin-top:0.2rem;margin-bottom:0.6rem;">
                <h3 style="margin:0;">Ward Chatbot</h3>
                <p style="margin:0.35rem 0 0 0;">Which ward info do you want to inspect?</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            ward_list = sorted(results_df["Ward"].unique())
            chat_ward = st.selectbox(
                "Select ward",
                ward_list,
                index=ward_list.index(selected_ward),
                key="chatbot_ward_select",
            )
            chat_row = results_df[results_df["Ward"] == chat_ward].iloc[0]

            if st.button("Inspect ward"):
                st.session_state["ward_chat_response"] = get_ward_chat_summary(chat_row)
                st.session_state["ward_chat_last_ward"] = chat_ward

            if st.session_state.get("ward_chat_last_ward") != chat_ward:
                st.session_state["ward_chat_response"] = get_ward_chat_summary(chat_row)
                st.session_state["ward_chat_last_ward"] = chat_ward

            st.markdown(
                f"""
                <div class="chat-card">
                    <b>Assistant:</b><br><br>
                    {st.session_state["ward_chat_response"].replace(chr(10), "<br>")}
                </div>
                """,
                unsafe_allow_html=True,
            )

elif st.session_state.active_page == "About Us":
    st.markdown(
        """
        <div class="card" style="max-width:860px;margin:1rem auto;padding:1.5rem 1.8rem;">
            <h2 style="margin-top:0;margin-bottom:0.8rem;">About Us</h2>
            <p style="font-size:1.02rem;line-height:1.7;margin-bottom:0.8rem;">
                This dashboard supports <b>Mumbai ward-wise green planning</b> and provides
                clear decision support for urban environmental initiatives.
            </p>
            <p style="font-size:1.02rem;line-height:1.7;margin-bottom:0.8rem;">
                It uses GIS + AI-based green diffusion modelling to help authorities track
                green coverage improvement, AQI impact, and ward-level policy recommendations.
            </p>
            <p style="font-size:1.02rem;line-height:1.7;margin-bottom:0;">
                Designed for research, planning, and environmental monitoring.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

elif st.session_state.active_page == "Contact Us":
    st.markdown(
        """
        <div class="card" style="max-width:760px;margin:1rem auto;padding:1.5rem 1.8rem;">
            <h2 style="margin-top:0;margin-bottom:0.8rem;">Contact Us</h2>
            <p style="margin:0.3rem 0;"><b>Department:</b> Artificial Intelligence & Machine Learning</p>
            <p style="margin:0.3rem 0;"><b>Project:</b> Mumbai-Ward based Green City Dashboard</p>
            <p style="margin:0.3rem 0;"><b>Email:</b> daniatasheen@gmail.com</p>
            <p style="margin:0.3rem 0;"><b>Phone:</b> +91-9152483646</p>
            <p style="margin-top:0.8rem;margin-bottom:0;">
                For collaboration, research access, or technical queries, please contact us.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
