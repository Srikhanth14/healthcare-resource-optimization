import streamlit as st
import pandas as pd
import plotly.express as px
from patient_prediction import show_patient_prediction
from recommendation import show_recommendations
from sql_analytics import show_sql_analytics

# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Healthcare Insights",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. CUSTOM CSS — PREMIUM NAVY & TEAL THEME
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --navy: #102B46;
    --navy-dark: #091D32;
    --teal: #13A89E;
    --blue: #377DDF;
    --purple: #8264DE;
    --orange: #F5A64A;
    --text: #243B53;
    --muted: #71849A;
    --border: #E1EAF4;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #F3F7FB;
    color: var(--text);
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1600px;
    padding: 1.5rem 2rem 2rem 2rem;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #102B46 0%, #091D32 100%);
    border-right: 1px solid #203F5B;
}

section[data-testid="stSidebar"] * {
    color: #EDF6FF;
}

.brand {
    padding: 12px 4px 24px;
    border-bottom: 1px solid rgba(255,255,255,0.12);
    margin-bottom: 24px;
}

.brand-icon {
    font-size: 34px;
    margin-bottom: 6px;
}

.brand-title {
    font-size: 20px;
    font-weight: 800;
    letter-spacing: -0.6px;
}

.brand-subtitle {
    color: #A9C1D8;
    font-size: 10px;
    margin-top: 5px;
    letter-spacing: 0.6px;
}

.sidebar-caption {
    color: #8FAAC3 !important;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    margin: 18px 0 8px 4px;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: transparent;
    border-radius: 10px;
    padding: 9px 12px;
    margin-bottom: 5px;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,0.09);
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label p {
    font-size: 13px;
    font-weight: 500;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] > label {
    display: none;
}

/* HERO HEADER */
.hero {
    background: linear-gradient(115deg, #E5F4FA 0%, #F8FBFF 55%, #DDF6F2 100%);
    border: 1px solid #DDEAF4;
    border-radius: 18px;
    padding: 27px 30px;
    margin-bottom: 25px;
    box-shadow: 0 5px 20px rgba(16,43,70,0.025);
}

.hero-eyebrow {
    color: #168C91;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.7px;
    text-transform: uppercase;
    margin-bottom: 9px;
}

.hero-title {
    color: #102B46;
    font-size: clamp(25px, 3vw, 36px);
    line-height: 1.2;
    font-weight: 800;
    letter-spacing: -1.2px;
    margin-bottom: 10px;
}

.hero-description {
    color: #607994;
    font-size: 13px;
    line-height: 1.8;
}

.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.85);
    border: 1px solid #DCEAEF;
    color: #31556F;
    padding: 9px 13px;
    border-radius: 10px;
    font-size: 11px;
    margin-top: 13px;
}

/* KPI CARDS */
.kpi-card {
    background: linear-gradient(145deg, #FFFFFF, #FBFDFF);
    border: 1px solid #E2EBF4;
    border-radius: 17px;
    padding: 20px 18px;
    min-height: 155px;
    box-shadow: 0 5px 18px rgba(16,43,70,0.035);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 28px rgba(16,43,70,0.08);
}

.kpi-top {
    display: flex;
    align-items: center;
    gap: 11px;
    margin-bottom: 15px;
}

.kpi-icon {
    width: 42px;
    height: 42px;
    border-radius: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 21px;
    flex-shrink: 0;
}

.kpi-label {
    font-size: 12px;
    line-height: 1.5;
    color: #60758D;
    font-weight: 600;
}

.kpi-value {
    color: #102B46;
    font-size: clamp(22px, 2vw, 29px);
    font-weight: 800;
    letter-spacing: -0.8px;
    overflow-wrap: anywhere;
}

.kpi-note {
    font-size: 10px;
    color: #71849A;
    margin-top: 9px;
}

/* SECTION HEADINGS */
.section-heading {
    color: #102B46;
    font-size: 21px;
    font-weight: 800;
    letter-spacing: -0.6px;
    margin: 28px 0 5px;
}

.section-subtitle {
    color: #71849A;
    font-size: 12px;
    line-height: 1.7;
    margin-bottom: 17px;
}

/* CHART CARDS */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(145deg, #FFFFFF, #FBFDFF);
    border: 1px solid #DFE9F3;
    border-radius: 18px;
    padding: 18px 20px 12px 20px;
    box-shadow: 0 6px 20px rgba(16, 43, 70, 0.055);
}

.chart-heading {
    color: #102B46;
    font-size: 16px;
    font-weight: 800;
    letter-spacing: -0.3px;
    margin-bottom: 3px;
}

.chart-subtitle {
    color: #71849A;
    font-size: 11px;
    line-height: 1.7;
    margin-bottom: 10px;
}

/* INSIGHTS */
.insight-box {
    background: linear-gradient(110deg, #E6F8F5, #F4FBFF);
    border: 1px solid #CDEDE7;
    border-radius: 15px;
    padding: 17px 20px;
    margin: 12px 0 18px;
}

.insight-title {
    color: #146C69;
    font-weight: 800;
    font-size: 14px;
    margin-bottom: 7px;
}

.insight-text {
    color: #456B7D;
    font-size: 12px;
    line-height: 1.8;
}

/* DISCLAIMER */
.disclaimer {
    background: #EBF5FC;
    border: 1px solid #D4E8F5;
    border-radius: 13px;
    padding: 16px 18px;
    color: #59758D;
    font-size: 11px;
    line-height: 1.9;
    margin-top: 22px;
}

.disclaimer strong {
    color: #1B5578;
}

.footer {
    text-align: center;
    color: #8A9BAD;
    font-size: 10px;
    letter-spacing: 0.6px;
    padding: 20px 0 5px;
}

/* STREAMLIT METRICS */
[data-testid="stMetricValue"] {
    color: #102B46;
    font-size: 20px !important;
    line-height: 1.35 !important;
    overflow-wrap: anywhere;
    word-break: break-word;
}

[data-testid="stMetricLabel"] {
    color: #60758D;
    font-size: 12px !important;
    line-height: 1.5 !important;
}

[data-testid="stMetricDelta"] {
    font-size: 11px !important;
}

[data-testid="stMetricValue"] div {
    font-size: 20px !important;
    white-space: normal !important;
    overflow-wrap: anywhere;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# 3. LOAD DATASET
# =========================================================
@st.cache_data
def load_data():
    data = pd.read_csv("modified_healthcare_dataset.csv")
    data.columns = data.columns.str.strip()

    if "Date of Admission" in data.columns:
        data["Date of Admission"] = pd.to_datetime(
            data["Date of Admission"],
            errors="coerce"
        )

        if "Admission Month" not in data.columns:
            data["Admission Month"] = (
                data["Date of Admission"].dt.month
            )

        if "Admission Year" not in data.columns:
            data["Admission Year"] = (
                data["Date of Admission"].dt.year
            )

    return data


try:
    df = load_data()
except Exception as e:
    st.error(
        "Unable to load the dataset. Make sure "
        "'modified_healthcare_dataset.csv' is in the same "
        "folder as app.py."
    )
    st.exception(e)
    st.stop()


required_columns = [
    "Hospital",
    "Admission Type",
    "Medical Condition"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        f"Required dataset columns are missing: {missing_columns}"
    )
    st.stop()

if df.empty:
    st.error("The healthcare dataset contains no records.")
    st.stop()


# 4. SIDEBAR NAVIGATION
# =========================================================
with st.sidebar:
    st.markdown("""
    <div class="brand">
        <div class="brand-icon">💠</div>
        <div class="brand-title">Healthcare Insights</div>
        <div class="brand-subtitle">
            BETTER DATA. BETTER DECISIONS.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="sidebar-caption">WORKSPACE</div>',
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigation",
        [
            "🏠  Dashboard",
            "🧑‍⚕️  Patient Prediction",
            "💡  Recommendations",
            "▤  SQL Analytics"
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.markdown(
        '<div class="sidebar-caption">DATASET STATUS</div>',
        unsafe_allow_html=True
    )

    st.markdown("🟢 Dataset loaded")
    st.caption(f"{len(df):,} patient records")
    st.caption("Academic demonstration")

    st.markdown("---")

    st.markdown("""
    <div style="color:#A9C1D8;font-size:11px;line-height:1.9;">
        Data today,<br>
        healthier decisions tomorrow.
    </div>
    """, unsafe_allow_html=True)


if page == "🧑‍⚕️  Patient Prediction":
    show_patient_prediction()
    st.stop()

elif page == "💡  Recommendations":
    show_recommendations()
    st.stop()

elif page == "▤  SQL Analytics":
    show_sql_analytics()
    st.stop()

# =========================================================
# 5. PREPARE KPI VALUES
# =========================================================
total_records = len(df)
total_hospitals = df["Hospital"].nunique()
total_categories = df["Admission Type"].nunique()

if "Admission Year" in df.columns:
    years = pd.to_numeric(
        df["Admission Year"],
        errors="coerce"
    ).dropna()

    year_range = (
        f"{int(years.min())} – {int(years.max())}"
        if not years.empty else "N/A"
    )
else:
    year_range = "N/A"


# =========================================================
# 6. HERO HEADER
# =========================================================
st.markdown(f"""
<div class="hero">
    <div class="hero-eyebrow">Healthcare Analytics Platform</div>
    <div class="hero-title">
        Intelligent Healthcare<br>
        Resource Optimization
    </div>
    <div class="hero-description">
        Explore historical admission patterns, hospital workload,
        medical conditions, and healthcare trends.
    </div>
    <div class="hero-badge">
        📅 Data period: {year_range}
        &nbsp;&nbsp; • &nbsp;&nbsp;
        🗂️ {total_records:,} records analysed
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# 7. KPI CARDS
# =========================================================
st.markdown(
    '<div class="section-heading">'
    'Your Healthcare at a Glance'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'A high-level overview of the dataset'
    '</div>',
    unsafe_allow_html=True
)


def render_kpi(icon, label, value, note, icon_bg):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-top">
            <div class="kpi-icon" style="background:{icon_bg};">
                {icon}
            </div>
            <div class="kpi-label">{label}</div>
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-note">{note}</div>
    </div>
    """, unsafe_allow_html=True)


k1, k2, k3, k4 = st.columns(4, gap="medium")

with k1:
    render_kpi("👥", "Total Patient Records", f"{total_records:,}", "Historical dataset records", "#DDF8F2")

with k2:
    render_kpi("🏥", "Number of Hospitals", f"{total_hospitals:,}", "Hospitals represented in data", "#E4EEFF")

with k3:
    render_kpi("📋", "Admission Categories", f"{total_categories:,}", "Distinct admission types", "#F0E9FF")

with k4:
    render_kpi("📅", "Data Year Range", year_range, "Historical data coverage", "#DFF5FC")


# =========================================================
# 8. COMMON PLOTLY STYLING
# =========================================================
CHART_CONFIG = {
    "displayModeBar": False,
    "responsive": True
}


def style_chart(fig, height=330):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=18, r=38, t=20, b=35),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, Arial, sans-serif",
            color="#243B53",
            size=12
        ),
        legend=dict(
            font=dict(
                family="Inter, Arial, sans-serif",
                color="#243B53",
                size=11
            ),
            bgcolor="rgba(255,255,255,0)",
            borderwidth=0
        ),
        hoverlabel=dict(
            bgcolor="#102B46",
            bordercolor="#102B46",
            font=dict(
                family="Inter, Arial, sans-serif",
                color="#FFFFFF",
                size=12
            ),
            namelength=-1
        ),
        hovermode="closest"
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#DCE5EF",
        tickfont=dict(color="#52677F", size=11),
        title_font=dict(color="#243B53", size=12),
        automargin=True
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#EAF0F6",
        gridwidth=1,
        zeroline=False,
        linecolor="#DCE5EF",
        tickfont=dict(color="#52677F", size=11),
        title_font=dict(color="#243B53", size=12),
        automargin=True
    )

    return fig


def chart_header(title, subtitle):
    st.markdown(f"""
    <div class="chart-heading">{title}</div>
    <div class="chart-subtitle">{subtitle}</div>
    """, unsafe_allow_html=True)


# =========================================================
# 9. ADMISSION PATTERNS & HOSPITAL WORKLOAD (ROW 1)
# =========================================================
st.markdown(
    '<div class="section-heading">'
    'Admission Patterns & Hospital Workload'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Understand how patient records are distributed'
    '</div>',
    unsafe_allow_html=True
)

# ROW 1 COLUMNS (Independent alignment)
row1_left, row1_right = st.columns(2, gap="medium")


# ---------------------------------------------------------
# 9A. DONUT CHART (Row 1 Left)
# ---------------------------------------------------------
admission_counts = (
    df["Admission Type"]
    .fillna("Unknown")
    .value_counts()
    .rename_axis("Admission Type")
    .reset_index(name="Patient Records")
)

admission_colors = {
    "Emergency": "#2E5BFF",
    "Elective": "#008080",
    "Urgent": "#7B1FA2",
    "Routine": "#E65100",
    "Unknown": "#71849A"
}

with row1_left:
    with st.container(border=True):

        chart_header(
            "Admission Type Distribution",
            "Share of patient records by admission category"
        )

        fig_admission = px.pie(
            admission_counts,
            names="Admission Type",
            values="Patient Records",
            hole=0.66,
            color="Admission Type",
            color_discrete_map=admission_colors
        )

        fig_admission.update_traces(
            textposition="inside",
            textinfo="percent",
            textfont=dict(
                color="#FFFFFF",
                size=12,
                family="Inter, Arial, sans-serif"
            ),
            sort=False,
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Patient Records: %{value:,}<br>"
                "Share: %{percent}<extra></extra>"
            ),
            marker=dict(
                line=dict(color="#FFFFFF", width=3)
            )
        )

        fig_admission.add_annotation(
            text=(
                f"<b>{total_records:,}</b>"
                "<br><span style='font-size:11px'>Records</span>"
            ),
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(
                size=21,
                color="#102B46",
                family="Inter, Arial, sans-serif"
            )
        )

        fig_admission = style_chart(fig_admission, 340)

        fig_admission.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.09,
                xanchor="center",
                x=0.5,
                font=dict(
                    color="#243B53",
                    size=11
                )
            )
        )

        st.plotly_chart(
            fig_admission,
            width="stretch",
            config=CHART_CONFIG
        )



# ---------------------------------------------------------
# 9B. HOSPITAL WORKLOAD BAR CHART (Row 1 Right)
# ---------------------------------------------------------
hospital_counts = (
    df.groupby("Hospital")
    .size()
    .reset_index(name="Patient Records")
    .sort_values("Patient Records", ascending=True)
)

with row1_right:
    with st.container(border=True):

        chart_header(
            "Hospital Workload",
            "Historical patient-record volume by hospital"
        )

        fig_hospital = px.bar(
            hospital_counts,
            x="Patient Records",
            y="Hospital",
            orientation="h",
            text="Patient Records",
            color="Patient Records",
            color_continuous_scale=[
                "#4DB6AC",  # Soft readable teal
                "#00897B",  # Medium teal
                "#004D40"   # Deep teal
            ]
        )

        fig_hospital.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
            marker=dict(cornerradius=6),
            textfont=dict(
                color="#243B53",
                size=11,
                family="Inter, Arial, sans-serif"
            ),
            cliponaxis=False,
            marker_line_width=0,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Patient records: %{x:,.0f}"
                "<extra></extra>"
            )
        )

        fig_hospital.update_layout(
            coloraxis_showscale=False,
            showlegend=False,
            xaxis_title=None,
            yaxis_title=None,
            bargap=0.42,
            margin=dict(l=140, r=40, t=20, b=35)
        )

        fig_hospital = style_chart(
            fig_hospital,
            max(330, len(hospital_counts) * 48)
        )

        fig_hospital.update_xaxes(
            showgrid=True,
            gridcolor="#EAF0F6",
            tickformat=",",
            title=None
        )

        st.plotly_chart(
            fig_hospital,
            width="stretch",
            config=CHART_CONFIG
        )


# =========================================================
# 10. TRENDS & CONDITIONS (ROW 2)
# =========================================================
# ROW 2 COLUMNS (Independent alignment for bottom row)
row2_left, row2_right = st.columns(2, gap="medium")


# ---------------------------------------------------------
# 10A. MONTHLY ADMISSION TREND (Row 2 Left)
# ---------------------------------------------------------
with row2_left:
    with st.container(border=True):

        chart_header(
            "Monthly Admission Trends",
            "Historical records grouped by calendar month across all years"
        )

        if "Admission Month" in df.columns:
            monthly_data = df.copy()

            monthly_data["Admission Month"] = pd.to_numeric(
                monthly_data["Admission Month"],
                errors="coerce"
            )

            monthly_data = monthly_data.dropna(
                subset=["Admission Month"]
            )

            monthly_data = monthly_data[
                monthly_data["Admission Month"].between(1, 12)
            ]

            monthly_counts = (
                monthly_data.groupby("Admission Month")
                .size()
                .reindex(range(1, 13), fill_value=0)
                .rename("Patient Records")
                .reset_index()
            )

            month_names = {
                1: "Jan", 2: "Feb", 3: "Mar",
                4: "Apr", 5: "May", 6: "Jun",
                7: "Jul", 8: "Aug", 9: "Sep",
                10: "Oct", 11: "Nov", 12: "Dec"
            }

            monthly_counts["Month"] = (
                monthly_counts["Admission Month"].map(month_names)
            )

            fig_monthly = px.line(
                monthly_counts,
                x="Month",
                y="Patient Records",
                markers=True,
                category_orders={
                    "Month": list(month_names.values())
                }
            )

            fig_monthly.update_traces(
                line=dict(
                    color="#008080",
                    width=3,
                    shape="spline"
                ),
                marker=dict(
                    size=7,
                    color="#008080",
                    line=dict(color="#FFFFFF", width=2)
                ),
                fill="tozeroy",
                fillcolor="rgba(0,128,128,0.08)",
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Patient records: %{y:,.0f}"
                    "<extra></extra>"
                )
            )

            fig_monthly = style_chart(fig_monthly, 330)

            fig_monthly.update_xaxes(
                showgrid=False,
                categoryorder="array",
                categoryarray=list(month_names.values())
            )

            fig_monthly.update_yaxes(
                showgrid=True,
                gridcolor="#EAF0F6",
                tickformat=",",
                rangemode="tozero"
            )

            st.plotly_chart(
                fig_monthly,
                width="stretch",
                config=CHART_CONFIG
            )
        else:
            st.info("Admission month data is unavailable.")


# ---------------------------------------------------------
# 10B. MEDICAL CONDITION DISTRIBUTION (Row 2 Right)
# ---------------------------------------------------------
condition_counts = (
    df["Medical Condition"]
    .fillna("Unknown")
    .value_counts()
    .sort_values(ascending=True)
    .rename_axis("Medical Condition")
    .reset_index(name="Patient Records")
)

top_condition_name = (
    condition_counts
    .sort_values("Patient Records", ascending=False)
    .iloc[0]["Medical Condition"]
)

condition_bar_colors = [
    "#102B46" if condition == top_condition_name
    else "#90A4AE"
    for condition in condition_counts["Medical Condition"]
]

with row2_right:
    with st.container(border=True):

        chart_header(
            "Medical Condition Distribution",
            "Ranked comparison of conditions in the dataset"
        )

        fig_condition = px.bar(
            condition_counts,
            x="Patient Records",
            y="Medical Condition",
            orientation="h",
            text="Patient Records"
        )

        fig_condition.update_traces(
            marker_color=condition_bar_colors,
            marker=dict(cornerradius=5),
            texttemplate="%{text:,.0f}",
            textposition="outside",
            textfont=dict(
                color="#243B53",
                size=10,
                family="Inter, Arial, sans-serif"
            ),
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Patient records: %{x:,.0f}"
                "<extra></extra>"
            )
        )

        fig_condition.update_layout(
            showlegend=False,
            xaxis_title=None,
            yaxis_title=None,
            bargap=0.34,
            margin=dict(l=90, r=40, t=20, b=35)
        )

        fig_condition = style_chart(
            fig_condition,
            max(330, len(condition_counts) * 35)
        )

        fig_condition.update_xaxes(
            showgrid=True,
            gridcolor="#EAF0F6",
            tickformat=",",
            title=None
        )

        st.plotly_chart(
            fig_condition,
            width="stretch",
            config=CHART_CONFIG
        )


# =========================================================
# 11. AUTOMATIC KEY INSIGHTS
# =========================================================
top_admission = admission_counts.sort_values(
    "Patient Records",
    ascending=False
).iloc[0]

top_hospital = hospital_counts.sort_values(
    "Patient Records",
    ascending=False
).iloc[0]

top_condition = condition_counts.sort_values(
    "Patient Records",
    ascending=False
).iloc[0]

st.markdown("""
<div class="insight-box">
    <div class="insight-title">✦ Key Dataset Insights</div>
    <div class="insight-text">
        These highlights are calculated from the currently loaded dataset.
        They describe historical record patterns, not live hospital conditions.
    </div>
</div>
""", unsafe_allow_html=True)

i1, i2, i3 = st.columns(3, gap="medium")

with i1:
    st.metric(
        "Most Frequent Admission Type",
        str(top_admission["Admission Type"]),
        f'{int(top_admission["Patient Records"]):,} records'
    )

with i2:
    st.metric(
        "Highest Historical Record Count",
        str(top_hospital["Hospital"]),
        f'{int(top_hospital["Patient Records"]):,} records'
    )

with i3:
    st.metric(
        "Most Common Medical Condition",
        str(top_condition["Medical Condition"]),
        f'{int(top_condition["Patient Records"]):,} records'
    )


# =========================================================
# 12. DISCLAIMER & FOOTER
# =========================================================
st.markdown("""
<div class="disclaimer">
    <strong>ⓘ Data Disclaimer</strong><br>
    This dashboard uses historical synthetic healthcare data for academic
    analysis. Patient-record counts do not represent live occupancy, available
    beds, staffing levels, ambulance locations, or real-time hospital capacity.
    Predictions and recommendations are experimental decision-support outputs
    and must not be used for clinical decisions.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="footer">
    INTELLIGENT HEALTHCARE RESOURCE OPTIMIZATION
    &nbsp;•&nbsp; MCA DATA ANALYTICS PROJECT
</div>
""", unsafe_allow_html=True)