
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

DATA_FILE = Path(__file__).resolve().parent / "modified_healthcare_dataset.csv"

PRIMARY_TEAL = "#13A89E"
DEEP_NAVY = "#102B46"
WHITE = "#FFFFFF"
DARK_TEXT = "#243B53"
MUTED_TEXT = "#71849A"
BORDER_COLOR = "#E1EAF4"

ADMISSION_COLORS = {
    "Emergency": "#E76F51",
    "Elective": "#3A86FF",
    "Urgent": "#F4A261",
    "Routine": "#13A89E",
}


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_recommendation_data(file_path):
    """Load and clean the healthcare dataset."""
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()

    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype("string").str.strip()
        df[col] = df[col].replace("", pd.NA)

    return df


def get_column(df, possible_names):
    """Find a column using possible column names."""
    lookup = {str(col).strip().lower(): col for col in df.columns}

    for name in possible_names:
        if name.strip().lower() in lookup:
            return lookup[name.strip().lower()]

    return None


def clean_series(series):
    """Remove missing and empty values."""
    return (
        series.dropna()
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
    )


def get_admission_date_column(df):
    """Identify admission dates or derive dates from admission year."""
    date_col = get_column(
        df,
        [
            "Date of Admission",
            "Admission Date",
            "Admission_Date",
            "Date",
        ],
    )

    if date_col is not None:
        parsed_dates = pd.to_datetime(df[date_col], errors="coerce")

        if parsed_dates.notna().any():
            return date_col, parsed_dates

    year_col = get_column(df, ["Admission Year", "Year"])

    if year_col is not None:
        years = pd.to_numeric(df[year_col], errors="coerce")

        parsed_dates = pd.to_datetime(
            years.astype("Int64").astype("string") + "-01-01",
            errors="coerce",
        )

        return year_col, parsed_dates

    return None, pd.Series(pd.NaT, index=df.index)


# ============================================================
# PAGE STYLING
# ============================================================

def apply_recommendation_styles():
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        .rec-banner {
            background: linear-gradient(
                135deg, #EAF4FF 0%, #DCEEFF 100%
            );
            padding: 28px 30px;
            border-radius: 18px;
            margin-bottom: 22px;
            border: 1px solid #D2E5F8;
            box-shadow: 0 4px 14px rgba(16, 43, 70, 0.05);
        }

        .rec-banner h1 {
            color: #102B46;
            font-size: 29px;
            font-weight: 750;
            margin: 0 0 8px 0;
        }

        .rec-banner p {
            color: #526B84;
            font-size: 14px;
            margin: 0;
            line-height: 1.7;
        }

        .rec-kpi {
            background: #FFFFFF;
            border: 1px solid #E1EAF4;
            border-radius: 15px;
            padding: 17px 18px;
            min-height: 125px;
            box-shadow: 0 3px 12px rgba(16, 43, 70, 0.04);
        }

        .rec-kpi-top {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
        }

        .rec-kpi-icon {
            width: 38px;
            height: 38px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #E6F8F5;
            border-radius: 11px;
            font-size: 20px;
        }

        .rec-kpi-label {
            color: #71849A;
            font-size: 13px;
            font-weight: 600;
        }

        .rec-kpi-value {
            color: #102B46;
            font-size: 27px;
            font-weight: 750;
            line-height: 1.2;
        }

        .rec-chart-heading {
            background: #FFFFFF;
            border: 1px solid #E1EAF4;
            border-left: 5px solid #13A89E;
            border-radius: 12px;
            padding: 14px 17px;
            margin-top: 12px;
            margin-bottom: 8px;
            box-shadow: 0 2px 8px rgba(16, 43, 70, 0.035);
        }

        .rec-chart-heading h4 {
            color: #102B46;
            font-size: 17px;
            font-weight: 700;
            margin: 0 0 4px 0;
        }

        .rec-chart-heading p {
            color: #71849A;
            font-size: 12px;
            margin: 0;
        }

        .rec-insight {
            background: #E6F8F5;
            border: 1px solid #BFEAE3;
            border-radius: 12px;
            padding: 16px 18px;
            margin: 12px 0 18px 0;
            color: #243B53;
        }

        .rec-insight h4 {
            color: #102B46;
            margin: 0 0 8px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_banner():
    st.markdown(
        """
        <div class="rec-banner">
            <h1>Healthcare Recommendations</h1>
            <p>
                Explore historical admission patterns, identify common
                medical conditions, compare hospital admissions, and
                generate data-driven resource planning suggestions.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_kpi(label, value, icon):
    st.markdown(
        f"""
        <div class="rec-kpi">
            <div class="rec-kpi-top">
                <div class="rec-kpi-icon">{icon}</div>
                <div class="rec-kpi-label">{label}</div>
            </div>
            <div class="rec-kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_chart_heading(title, description):
    st.markdown(
        f"""
        <div class="rec-chart-heading">
            <h4>{title}</h4>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_chart(fig, height=390):
    fig.update_layout(
        height=height,
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(
            family="Arial, sans-serif",
            color=DARK_TEXT,
            size=12,
        ),
        margin=dict(l=20, r=35, t=30, b=25),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        hoverlabel=dict(
            bgcolor=WHITE,
            font_size=12,
            font_family="Arial",
        ),
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#EDF2F7",
        zeroline=False,
        showline=False,
    )

    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        showline=False,
    )

    return fig


# ============================================================
# RECOMMENDATION GENERATOR
# ============================================================

def build_recommendations(
    selected_types,
    filtered_df,
    condition_col,
    hospital_col,
):
    st.markdown("### Recommended Actions")

    if not selected_types:
        st.info("Select at least one admission type.")
        return

    st.markdown(
        f"""
        <div class="rec-insight">
            <h4>Analysis for: {", ".join(selected_types)}</h4>
            These suggestions are based on historical records matching
            your selected admission categories. They support resource
            planning and do not replace clinical decisions.
        </div>
        """,
        unsafe_allow_html=True,
    )

    recommendations = {
        "Emergency": (
            "Review historical emergency demand to support contingency "
            "planning and appropriate resource readiness."
        ),
        "Urgent": (
            "Review recurring urgent admission patterns to support "
            "operational planning during higher-demand periods."
        ),
        "Elective": (
            "Use historical elective admission volumes to support "
            "scheduling and planned resource allocation."
        ),
        "Routine": (
            "Review routine admission volumes to support standard "
            "workload and resource planning."
        ),
    }

    for admission_type in selected_types:
        if admission_type in recommendations:
            st.markdown(
                f"- **{admission_type}:** "
                f"{recommendations[admission_type]}"
            )

    if len(selected_types) == 4:
        st.markdown(
            "- **Overall planning:** Compare the admission mix and "
            "historical trends across all admission categories."
        )

    if condition_col and not filtered_df.empty:
        counts = clean_series(
            filtered_df[condition_col]
        ).value_counts()

        if not counts.empty:
            st.markdown(
                f"- **Most frequent condition:** {counts.index[0]} "
                f"({counts.iloc[0]:,} records in the current selection)."
            )

    if hospital_col and not filtered_df.empty:
        counts = clean_series(
            filtered_df[hospital_col]
        ).value_counts()

        if not counts.empty:
            st.markdown(
                f"- **Highest-volume hospital in this selection:** "
                f"{counts.index[0]} ({counts.iloc[0]:,} records)."
            )


# ============================================================
# CHART 1: ADMISSION TYPE DISTRIBUTION
# ============================================================

def show_admission_distribution(df, admission_col, selected_types):
    show_chart_heading(
        "Admission Type Distribution",
        "Overall admission mix, with selected categories highlighted.",
    )

    if admission_col is None:
        st.info("The Admission Type column was not found.")
        return

    counts = clean_series(df[admission_col]).value_counts()

    if counts.empty:
        st.info("No admission type data is available.")
        return

    chart_df = counts.rename_axis("Admission Type").reset_index(
        name="Admissions"
    )

    chart_df["Selection"] = chart_df["Admission Type"].apply(
        lambda value: (
            "Selected" if value in selected_types else "Other categories"
        )
    )

    fig = px.bar(
        chart_df.sort_values("Admissions", ascending=True),
        x="Admissions",
        y="Admission Type",
        orientation="h",
        color="Selection",
        color_discrete_map={
            "Selected": PRIMARY_TEAL,
            "Other categories": "#C7D7E8",
        },
        text="Admissions",
        custom_data=["Selection"],
    )

    fig.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Admissions: %{x:,}<br>"
            "%{customdata[0]}<extra></extra>"
        ),
    )

    fig.update_layout(
        xaxis_title="Number of Admissions",
        yaxis_title="",
        showlegend=False,
    )

    st.plotly_chart(
        style_chart(fig, height=350),
        width="stretch",
    )

    with st.expander("View admission type data"):
        st.dataframe(
            chart_df[["Admission Type", "Admissions"]].sort_values(
                "Admissions", ascending=False
            ),
            width="stretch",
            hide_index=True,
        )


# ============================================================
# CHART 2: COMMON MEDICAL CONDITIONS
# ============================================================

def show_condition_distribution(filtered_df, condition_col):
    show_chart_heading(
        "Common Medical Conditions",
        "Most frequently recorded conditions in the selected categories.",
    )

    if condition_col is None:
        st.info("The Medical Condition column was not found.")
        return

    counts = clean_series(
        filtered_df[condition_col]
    ).value_counts().head(10)

    if counts.empty:
        st.info("No medical condition data is available for this selection.")
        return

    chart_df = counts.rename_axis("Medical Condition").reset_index(
        name="Admissions"
    )

    fig = px.bar(
        chart_df.sort_values("Admissions", ascending=True),
        x="Admissions",
        y="Medical Condition",
        orientation="h",
        text="Admissions",
        color="Admissions",
        color_continuous_scale=["#BCEBE5", PRIMARY_TEAL, DEEP_NAVY],
    )

    fig.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Records: %{x:,}<extra></extra>"
        ),
    )

    fig.update_layout(
        xaxis_title="Number of Records",
        yaxis_title="",
        coloraxis_showscale=False,
    )

    st.plotly_chart(
        style_chart(fig, height=390),
        width="stretch",
    )

    with st.expander("View medical condition data"):
        st.dataframe(
            chart_df.sort_values("Admissions", ascending=False),
            width="stretch",
            hide_index=True,
        )


# ============================================================
# CHART 3: HOSPITAL ADMISSION ANALYSIS
# ============================================================

def show_hospital_analysis(filtered_df, hospital_col):
    show_chart_heading(
        "Hospital Admission Analysis",
        "Hospitals with the most records for the selected admission categories.",
    )

    if hospital_col is None:
        st.info("The Hospital column was not found.")
        return

    counts = clean_series(
        filtered_df[hospital_col]
    ).value_counts().head(10)

    if counts.empty:
        st.info("No hospital data is available for this selection.")
        return

    chart_df = counts.rename_axis("Hospital").reset_index(
        name="Admissions"
    )

    fig = px.bar(
        chart_df.sort_values("Admissions", ascending=True),
        x="Admissions",
        y="Hospital",
        orientation="h",
        text="Admissions",
        color="Admissions",
        color_continuous_scale=["#C9E9F8", "#3A86FF", DEEP_NAVY],
    )

    fig.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Records: %{x:,}<extra></extra>"
        ),
    )

    fig.update_layout(
        xaxis_title="Number of Records",
        yaxis_title="",
        coloraxis_showscale=False,
    )

    st.plotly_chart(
        style_chart(fig, height=420),
        width="stretch",
    )

    with st.expander("View hospital admission data"):
        st.dataframe(
            chart_df.sort_values("Admissions", ascending=False),
            width="stretch",
            hide_index=True,
        )


# ============================================================
# CHART 4: HISTORICAL ADMISSION TREND
# ============================================================

def show_historical_trend(filtered_df, date_col, date_series):
    show_chart_heading(
        "Historical Admission Trend",
        "Yearly admission counts for the selected categories.",
    )

    if date_col is None or date_series.notna().sum() == 0:
        st.info(
            "A valid admission date or admission year column is required "
            "to display the historical trend."
        )
        return

    trend_df = pd.DataFrame(
        {
            "Admission Date": date_series.reindex(filtered_df.index),
        },
        index=filtered_df.index,
    ).dropna(subset=["Admission Date"])

    if trend_df.empty:
        st.info("No valid historical dates are available for this selection.")
        return

    trend_df["Year"] = trend_df["Admission Date"].dt.year

    yearly_counts = (
        trend_df.groupby("Year")
        .size()
        .reset_index(name="Admissions")
        .sort_values("Year")
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=yearly_counts["Year"],
            y=yearly_counts["Admissions"],
            mode="lines+markers+text",
            name="Admissions",
            line=dict(color=PRIMARY_TEAL, width=3),
            marker=dict(
                size=9,
                color=PRIMARY_TEAL,
                line=dict(color=WHITE, width=2),
            ),
            text=yearly_counts["Admissions"],
            textposition="top center",
            texttemplate="%{text:,}",
            hovertemplate=(
                "<b>Year %{x}</b><br>"
                "Admissions: %{y:,}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        xaxis_title="Admission Year",
        yaxis_title="Number of Admissions",
        hovermode="x unified",
    )

    fig = style_chart(fig, height=370)
    fig.update_xaxes(tickmode="linear", dtick=1)

    st.plotly_chart(fig, width="stretch")

    with st.expander("View historical trend data"):
        st.dataframe(
            yearly_counts,
            width="stretch",
            hide_index=True,
        )


# ============================================================
# MAIN PAGE
# ============================================================

def show_recommendations():
    apply_recommendation_styles()

    if not DATA_FILE.exists():
        st.error(
            "Dataset not found. Ensure modified_healthcare_dataset.csv "
            "is in the same folder as recommendations.py."
        )
        return

    try:
        df = load_recommendation_data(str(DATA_FILE))
    except Exception as exc:
        st.error(f"Unable to load the healthcare dataset: {exc}")
        return

    if df.empty:
        st.warning("The healthcare dataset is empty.")
        return

    admission_col = get_column(
        df,
        ["Admission Type", "Admission_Type", "AdmissionType"],
    )

    condition_col = get_column(
        df,
        ["Medical Condition", "Medical_Condition", "Condition"],
    )

    hospital_col = get_column(
        df,
        ["Hospital", "Hospital Name", "Hospital_Name"],
    )

    # Banner
    show_banner()

    # --------------------------------------------------------
    # GLOBAL KPI CARDS
    # --------------------------------------------------------

    total_records = len(df)

    total_types = (
        clean_series(df[admission_col]).nunique()
        if admission_col else 0
    )

    total_hospitals = (
        clean_series(df[hospital_col]).nunique()
        if hospital_col else 0
    )

    total_conditions = (
        clean_series(df[condition_col]).nunique()
        if condition_col else 0
    )

    st.markdown("### Healthcare Overview")
    st.caption("Summary of the complete healthcare dataset.")

    kpi_columns = st.columns(4)

    kpi_values = [
        ("Total Records", f"{total_records:,}", "📊"),
        ("Admission Types", f"{total_types:,}", "🩺"),
        ("Hospitals", f"{total_hospitals:,}", "🏥"),
        ("Medical Conditions", f"{total_conditions:,}", "💊"),
    ]

    for column, (label, value, icon) in zip(kpi_columns, kpi_values):
        with column:
            show_kpi(label, value, icon)

    st.markdown("---")

    # --------------------------------------------------------
    # MULTIPLE ADMISSION TYPE SELECTION
    # --------------------------------------------------------

    st.markdown("### Recommendation Generator")
    st.caption(
        "Select one or more admission categories to update the analysis."
    )

    if admission_col is None:
        st.error("The Admission Type column was not found in the dataset.")
        return

    admission_values = sorted(
        clean_series(df[admission_col]).unique().tolist()
    )

    preferred_order = ["Emergency", "Elective", "Urgent", "Routine"]

    ordered_values = [
        value for value in preferred_order
        if value in admission_values
    ]

    ordered_values += [
        value for value in admission_values
        if value not in ordered_values
    ]

    selected_types = st.multiselect(
        "Select Admission Type(s)",
        options=ordered_values,
        default=ordered_values,
        placeholder="Choose one or more admission types",
        help="Select multiple categories to analyze them together.",
    )

    if not selected_types:
        st.info(
            "Select at least one admission type to view recommendations "
            "and charts."
        )
        return

    filtered_df = df[
        df[admission_col]
        .astype("string")
        .str.strip()
        .isin(selected_types)
    ].copy()

    st.caption(
        f"Showing {len(filtered_df):,} of {len(df):,} records "
        f"for: {', '.join(selected_types)}"
    )

    # Dynamic recommendations
    build_recommendations(
        selected_types,
        filtered_df,
        condition_col,
        hospital_col,
    )

    st.markdown("---")

    # --------------------------------------------------------
    # CHART 1 AND CHART 2
    # --------------------------------------------------------

    st.markdown("### Admission & Condition Analysis")
    st.caption(
        "Admission distribution compares the full dataset and highlights "
        "selected categories. Medical conditions reflect the current selection."
    )

    show_admission_distribution(
        df,
        admission_col,
        selected_types,
    )

    show_condition_distribution(
        filtered_df,
        condition_col,
    )

    st.markdown("---")

    # --------------------------------------------------------
    # CHART 3
    # --------------------------------------------------------

    st.markdown("### Hospital Admission Analysis")
    st.caption(
        "Hospital rankings update based on your selected admission categories."
    )

    show_hospital_analysis(
        filtered_df,
        hospital_col,
    )

    st.markdown("---")

    # --------------------------------------------------------
    # CHART 4
    # --------------------------------------------------------

    st.markdown("### Historical Admission Trend")
    st.caption(
        "Review how the selected admission categories have changed over time."
    )

    date_col, date_series = get_admission_date_column(df)

    show_historical_trend(
        filtered_df,
        date_col,
        date_series,
    )

    st.markdown("---")

    st.caption(
        "Project scope: This page analyzes historical healthcare records "
        "to support resource planning. It does not represent live hospital "
        "capacity, real-time staffing, or clinical decision-making."
    )
