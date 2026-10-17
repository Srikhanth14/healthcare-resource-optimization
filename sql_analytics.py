from pathlib import Path
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "modified_healthcare_dataset.csv"
DB_FILE = BASE_DIR / "healthcare.db"
TABLE_NAME = "healthcare_records"

# Application theme
PRIMARY_TEAL = "#13A89E"
DEEP_NAVY = "#102B46"
BLUE = "#3977A8"
PURPLE = "#8274C8"
ORANGE = "#E9A23B"

TEXT_COLOR = "#334155"
MUTED_COLOR = "#64748B"
LIGHT_BACKGROUND = "#F8FAFC"
WHITE = "#FFFFFF"


# =========================================================
# SQL AND DATA HELPERS
# =========================================================

def quote_identifier(name):
    """Safely quote SQLite table or column identifiers."""
    return '"' + str(name).replace('"', '""') + '"'


@st.cache_data(show_spinner=False)
def load_source_data(csv_path, modified_time):
    """Load the source CSV."""
    return pd.read_csv(csv_path, low_memory=False)


@st.cache_resource(show_spinner="Preparing healthcare database...")
def prepare_sqlite_database(csv_path, modified_time):
    """Create or refresh the SQLite database from the CSV."""
    df = load_source_data(csv_path, modified_time)

    if df.empty:
        raise ValueError("The healthcare dataset is empty.")

    with sqlite3.connect(str(DB_FILE)) as conn:
        df.to_sql(
            TABLE_NAME,
            conn,
            if_exists="replace",
            index=False,
        )

        # Add an index to improve admission-type queries.
        admission_col = next(
            (
                col for col in df.columns
                if str(col).strip().lower() == "admission type"
            ),
            None,
        )

        if admission_col:
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_admission_type "
                f"ON {quote_identifier(TABLE_NAME)} "
                f"({quote_identifier(admission_col)})"
            )

    return str(DB_FILE)


def get_readonly_connection(db_path):
    """Open the SQLite database in read-only mode."""
    uri = Path(db_path).resolve().as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.execute("PRAGMA query_only = ON")
    return conn


def get_column(df, possible_names):
    """Find a column without depending on letter casing."""
    lookup = {
        str(col).strip().lower(): col
        for col in df.columns
    }

    for name in possible_names:
        found = lookup.get(name.strip().lower())
        if found is not None:
            return found

    return None


def sql_column(column_name):
    """Return a safely quoted SQL column reference."""
    return quote_identifier(column_name)


def run_sql_query(db_path, query, max_rows=5000):
    """
    Execute a read-only SQL query.
    Only SELECT and WITH queries are allowed.
    """
    cleaned_query = query.strip().rstrip(";").strip()

    if not cleaned_query:
        raise ValueError("Please enter a SQL query.")

    # Allow SELECT or WITH queries only.
    first_word = cleaned_query.split(None, 1)[0].upper()

    if first_word not in {"SELECT", "WITH"}:
        raise ValueError(
            "Only SELECT queries and read-only WITH queries are allowed."
        )

    # SQLite execute() accepts only one SQL statement.
    conn = get_readonly_connection(db_path)

    try:
        cursor = conn.execute(cleaned_query)
        rows = cursor.fetchmany(max_rows + 1)
        columns = [
            description[0]
            for description in cursor.description
        ]

        truncated = len(rows) > max_rows
        rows = rows[:max_rows]

        result = pd.DataFrame(rows, columns=columns)

        return result, truncated

    finally:
        conn.close()


# =========================================================
# PROFESSIONAL CHART THEME
# =========================================================

def style_sql_chart(fig):
    """Apply a clean, gridline-free Plotly theme."""

    fig.update_layout(
        template="plotly_white",

        colorway=[
            PRIMARY_TEAL,
            DEEP_NAVY,
            BLUE,
            PURPLE,
            ORANGE,
        ],

        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,

        font=dict(
            family="Arial, sans-serif",
            size=12,
            color=TEXT_COLOR,
        ),

        title=dict(
            x=0.02,
            xanchor="left",
            font=dict(
                size=18,
                color=DEEP_NAVY,
            ),
        ),

        margin=dict(
            l=20,
            r=20,
            t=65,
            b=35,
        ),

        hoverlabel=dict(
            bgcolor=DEEP_NAVY,
            font=dict(
                color=WHITE,
                size=12,
            ),
            bordercolor=DEEP_NAVY,
        ),

        legend=dict(
            font=dict(color=TEXT_COLOR),
            bgcolor="rgba(255,255,255,0)",
        ),

        hovermode="closest",
    )

    # Remove gridlines and axis lines.
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        showline=False,
        ticks="outside",
        tickcolor="#CBD5E1",
        tickfont=dict(color=MUTED_COLOR),
        title_font=dict(color=DEEP_NAVY),
    )

    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        showline=False,
        ticks="outside",
        tickcolor="#CBD5E1",
        tickfont=dict(color=MUTED_COLOR),
        title_font=dict(color=DEEP_NAVY),
    )

    return fig


# =========================================================
# PAGE STYLING
# =========================================================

def apply_sql_styles():
    """Style SQL Analytics page elements."""

    st.markdown(
        f"""
        <style>
          .sql-banner {{
            background: #D9EAEF;
            padding: 23px 25px;
            border-radius: 14px;
            margin-bottom: 22px;
            color: white;
        }}

        .sql-banner h2 {{
            color: white;
            margin: 0 0 8px 0;
            font-size: 25px;
        }}

        .sql-banner p {{
            color: #DCE8F1;
            margin: 0;
            font-size: 14px;
        }}

        .sql-kpi {{
            background: white;
            border: 1px solid #E2E8F0;
            border-left: 4px solid {PRIMARY_TEAL};
            border-radius: 10px;
            padding: 17px 18px;
            min-height: 100px;
        }}

        .sql-kpi-label {{
            font-size: 12px;
            color: {MUTED_COLOR};
            margin-bottom: 8px;
        }}

        .sql-kpi-value {{
            font-size: 25px;
            font-weight: 700;
            color: {DEEP_NAVY};
            overflow-wrap: anywhere;
        }}

        div[data-testid="stDataFrame"] {{
            border: 1px solid #E2E8F0;
            border-radius: 10px;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


def render_kpi(label, value):
    """Render one KPI card."""
    st.markdown(
        f"""
        <div class="sql-kpi">
            <div class="sql-kpi-label">{label}</div>
            <div class="sql-kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# PREDEFINED SQL QUERY LIBRARY
# =========================================================

def build_query_library(df):
    """Build queries based on columns available in the dataset."""

    columns = list(df.columns)
    queries = {}

    admission = get_column(df, ["Admission Type"])
    condition = get_column(df, ["Medical Condition"])
    hospital = get_column(df, ["Hospital"])
    billing = get_column(df, ["Billing Amount"])
    stay = get_column(df, ["Length of Stay"])
    insurance = get_column(df, ["Insurance Provider"])
    admission_date = get_column(
        df,
        ["Date of Admission", "Admission Date"],
    )
    admission_year = get_column(df, ["Admission Year", "Year"])

    queries["Total Records"] = f"""
        SELECT COUNT(*) AS total_records
        FROM {quote_identifier(TABLE_NAME)}
    """

    if admission:
        queries["Admission Type Distribution"] = f"""
            SELECT
                {sql_column(admission)} AS admission_type,
                COUNT(*) AS patient_count
            FROM {quote_identifier(TABLE_NAME)}
            GROUP BY {sql_column(admission)}
            ORDER BY patient_count DESC
        """

    if condition:
        queries["Top Medical Conditions"] = f"""
            SELECT
                {sql_column(condition)} AS medical_condition,
                COUNT(*) AS patient_count
            FROM {quote_identifier(TABLE_NAME)}
            GROUP BY {sql_column(condition)}
            ORDER BY patient_count DESC
            LIMIT 10
        """

    if hospital:
        queries["Top Hospitals by Records"] = f"""
            SELECT
                {sql_column(hospital)} AS hospital,
                COUNT(*) AS patient_count
            FROM {quote_identifier(TABLE_NAME)}
            GROUP BY {sql_column(hospital)}
            ORDER BY patient_count DESC
            LIMIT 10
        """

    if billing:
        queries["Billing Summary"] = f"""
            SELECT
                COUNT({sql_column(billing)}) AS billing_records,
                ROUND(AVG({sql_column(billing)}), 2) AS average_billing,
                ROUND(MIN({sql_column(billing)}), 2) AS minimum_billing,
                ROUND(MAX({sql_column(billing)}), 2) AS maximum_billing
            FROM {quote_identifier(TABLE_NAME)}
        """.replace(
            f"AVG({sql_column(billing)}, 2)",
            f"AVG({sql_column(billing)})",
        )

    if stay:
        queries["Length of Stay Summary"] = f"""
            SELECT
                COUNT({sql_column(stay)}) AS stay_records,
                ROUND(AVG({sql_column(stay)}), 2) AS average_stay,
                MIN({sql_column(stay)}) AS minimum_stay,
                MAX({sql_column(stay)}) AS maximum_stay
            FROM {quote_identifier(TABLE_NAME)}
        """

    if condition and admission:
        queries["Conditions by Admission Type"] = f"""
            SELECT
                {sql_column(condition)} AS medical_condition,
                {sql_column(admission)} AS admission_type,
                COUNT(*) AS patient_count
            FROM {quote_identifier(TABLE_NAME)}
            GROUP BY
                {sql_column(condition)},
                {sql_column(admission)}
            ORDER BY patient_count DESC
            LIMIT 100
        """

    if billing and admission:
        queries["Average Billing by Admission Type"] = f"""
            SELECT
                {sql_column(admission)} AS admission_type,
                ROUND(AVG({sql_column(billing)}), 2)
                    AS average_billing
            FROM {quote_identifier(TABLE_NAME)}
            GROUP BY {sql_column(admission)}
            ORDER BY average_billing DESC
        """

    if insurance:
        queries["Insurance Provider Distribution"] = f"""
            SELECT
                {sql_column(insurance)} AS insurance_provider,
                COUNT(*) AS patient_count
            FROM {quote_identifier(TABLE_NAME)}
            GROUP BY {sql_column(insurance)}
            ORDER BY patient_count DESC
        """

    if admission_year:
        queries["Admissions by Year"] = f"""
            SELECT
                {sql_column(admission_year)} AS admission_year,
                COUNT(*) AS patient_count
            FROM {quote_identifier(TABLE_NAME)}
            GROUP BY {sql_column(admission_year)}
            ORDER BY admission_year
        """

    elif admission_date:
        # ISO date strings sort chronologically when grouped by year.
        queries["Admissions by Year"] = f"""
            SELECT
                SUBSTR({sql_column(admission_date)}, 1, 4)
                    AS admission_year,
                COUNT(*) AS patient_count
            FROM {quote_identifier(TABLE_NAME)}
            WHERE {sql_column(admission_date)} IS NOT NULL
            GROUP BY SUBSTR({sql_column(admission_date)}, 1, 4)
            ORDER BY admission_year
        """

    return queries


# =========================================================
# CHART CREATION
# =========================================================

def create_result_chart(result):
    """
    Automatically create a chart for suitable SQL result sets.
    Uses the first text column and first numeric column.
    """

    if result.empty or len(result.columns) < 2:
        return None

    numeric_columns = result.select_dtypes(
        include="number"
    ).columns.tolist()

    text_columns = [
        col for col in result.columns
        if col not in numeric_columns
    ]

    if not numeric_columns:
        return None

    # Prefer a descriptive category for the X-axis.
    if text_columns:
        x_col = text_columns[0]
        y_col = numeric_columns[0]

        chart_df = result.copy()

        # Avoid overcrowding the chart.
        if len(chart_df) > 25:
            chart_df = chart_df.head(25)

        # Horizontal bars are clearer for long category names.
        fig = px.bar(
            chart_df,
            x=y_col,
            y=x_col,
            orientation="h",
            title=f"{y_col.replace('_', ' ').title()} by "
                  f"{x_col.replace('_', ' ').title()}",
            color_discrete_sequence=[PRIMARY_TEAL],
            text=y_col,
        )

        fig.update_traces(
            texttemplate="%{text:,.2f}",
            textposition="outside",
            cliponaxis=False,
            marker_line_width=0,
        )

        fig.update_yaxes(
            categoryorder="total ascending",
        )

        fig.update_layout(
            xaxis_title=y_col.replace("_", " ").title(),
            yaxis_title="",
        )

        return style_sql_chart(fig)

    # If only numeric columns exist, use a simple bar chart.
    numeric_df = result[numeric_columns].head(25)

    fig = px.bar(
        numeric_df,
        title="SQL Query Numeric Results",
        color_discrete_sequence=[PRIMARY_TEAL],
    )

    fig.update_traces(
        marker_line_width=0,
    )

    return style_sql_chart(fig)


# =========================================================
# QUERY RESULTS
# =========================================================

def show_query_results(db_path, query, chart=True, key_prefix="sql"):
    """Execute a query and display results, chart, and download."""

    try:
        result, truncated = run_sql_query(db_path, query)

        if result.empty:
            st.info("The query executed successfully but returned no rows.")
            return

        if truncated:
            st.warning(
                "Showing the first 5,000 rows for performance. "
                "Refine your SQL query if you need fewer or different rows."
            )

        st.markdown("#### Query Results")

        st.dataframe(
            result,
            width="stretch",
            hide_index=True,
        )

        st.download_button(
            label="Download Results as CSV",
            data=result.to_csv(index=False).encode("utf-8"),
            file_name="sql_analytics_results.csv",
            mime="text/csv",
            width="stretch",
            key=f"{key_prefix}_download",
        )

        if chart:
            fig = create_result_chart(result)

            if fig is not None:
                st.markdown("#### Data Visualization")
                st.plotly_chart(
                    fig,
                    width="stretch",
                    config={"displayModeBar": False},
                )

    except Exception as exc:
        st.error(f"Unable to execute the SQL query: {exc}")


# =========================================================
# MAIN SQL ANALYTICS PAGE
# =========================================================

def show_sql_analytics():
    """Render the SQL Analytics page."""

    apply_sql_styles()

    st.markdown(
        f"""
        <div class="sql-banner">
            <h2>SQL Analytics & Data Exploration</h2>
            <p>
                Explore healthcare records using SQL, analyze key metrics,
                visualize query results, and export your findings.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # Load source data and prepare database
    # -----------------------------------------------------

    if not CSV_FILE.exists():
        st.error(
            f"Dataset not found: {CSV_FILE}\n\n"
            "Place modified_healthcare_dataset.csv in the same "
            "folder as app.py and sql_analytics.py."
        )
        return

    try:
        modified_time = CSV_FILE.stat().st_mtime

        df = load_source_data(
            str(CSV_FILE),
            modified_time,
        )

        db_path = prepare_sqlite_database(
            str(CSV_FILE),
            modified_time,
        )

    except Exception as exc:
        st.error(f"Unable to load the healthcare database: {exc}")
        return

    # -----------------------------------------------------
    # Database overview
    # -----------------------------------------------------

    st.markdown("### Database Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        render_kpi("Total Records", f"{len(df):,}")

    with col2:
        render_kpi("Total Columns", f"{len(df.columns):,}")

    with col3:
        render_kpi("Database Engine", "SQLite")

    st.caption(
        f"Database: {Path(db_path).name}  |  "
        f"Table: {TABLE_NAME}  |  "
        "Source: modified_healthcare_dataset.csv"
    )

    st.divider()

    # -----------------------------------------------------
    # Predefined SQL analysis
    # -----------------------------------------------------

    st.markdown("### Predefined SQL Analysis")

    st.write(
        "Choose an analysis to execute a prepared SQL query "
        "against the healthcare dataset."
    )

    query_library = build_query_library(df)

    if query_library:
        selected_query = st.selectbox(
            "Select an analysis",
            options=list(query_library.keys()),
            key="sql_analysis_selector",
        )

        selected_sql = query_library[selected_query]

        with st.expander("View SQL Query"):
            st.code(selected_sql.strip(), language="sql")

        if st.button(
            "Run SQL Analysis",
            type="primary",
            width="stretch",
            key="run_predefined_sql",
        ):
            show_query_results(
                db_path,
                selected_sql,
                chart=True,
                key_prefix="predefined",
            )

    else:
        st.warning(
            "No predefined queries could be created from the "
            "available dataset columns."
        )

    st.divider()

    # -----------------------------------------------------
    # Custom SQL editor
    # -----------------------------------------------------

    st.markdown("### Custom SQL Query")

    st.write(
        "Write your own SELECT query to explore the dataset. "
        "Only read-only SELECT and WITH queries are permitted."
    )

    with st.expander("View Table Columns"):
        schema_df = pd.DataFrame({
            "Column Name": df.columns,
            "Data Type": [
                str(dtype) for dtype in df.dtypes
            ],
        })

        st.dataframe(
            schema_df,
            width="stretch",
            hide_index=True,
        )

    default_query = (
        'SELECT "Admission Type", COUNT(*) AS patient_count\n'
        f'FROM {quote_identifier(TABLE_NAME)}\n'
        'GROUP BY "Admission Type"\n'
        'ORDER BY patient_count DESC'
        if get_column(df, ["Admission Type"])
        else f"SELECT * FROM {quote_identifier(TABLE_NAME)} LIMIT 10"
    )

    custom_query = st.text_area(
        "Enter SQL query",
        value=default_query,
        height=170,
        key="custom_sql_query",
        help="Use the healthcare_records table name in your query.",
    )

    if st.button(
        "Execute Custom Query",
        type="primary",
        width="stretch",
        key="execute_custom_sql",
    ):
        show_query_results(
            db_path,
            custom_query,
            chart=True,
            key_prefix="custom",
        )

    # -----------------------------------------------------
    # Scope note
    # -----------------------------------------------------

    st.divider()

    st.caption(
        "Project scope: This page analyzes the historical healthcare "
        "dataset stored locally in SQLite. It does not represent "
        "live hospital capacity, real-time staffing, or live patient "
        "admission monitoring."
    )
