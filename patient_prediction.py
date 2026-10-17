import calendar
import html
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st


# =========================================================
# CONFIGURATION
# =========================================================
BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "modified_healthcare_dataset.csv"

MODEL_FILES = [
    BASE_DIR / "healthcare_rf_l4.joblib",
    BASE_DIR / "healthcare_rf_l4 (1).joblib",
]

CATEGORICAL_FEATURES = [
    "Gender",
    "Blood Type",
    "Medical Condition",
    "Hospital",
    "Insurance Provider",
    "Admission Day",
]


# =========================================================
# PREMIUM UI STYLING
# =========================================================
def add_prediction_styles():
    st.markdown(
        """
        <style>
        .prediction-hero {
            background: linear-gradient(115deg, #E5F4FA 0%, #F8FBFF 55%, #DDF6F2 100%);
            border: 1px solid #DDEAF4;
            border-radius: 18px;
            padding: 26px 30px;
            margin-bottom: 24px;
            box-shadow: 0 5px 20px rgba(16,43,70,0.025);
        }

        .prediction-eyebrow {
            color: #168C91;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1.7px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }

        .prediction-title {
            color: #102B46;
            font-size: clamp(25px, 3vw, 34px);
            line-height: 1.2;
            font-weight: 800;
            letter-spacing: -1px;
            margin-bottom: 8px;
        }

        .prediction-description {
            color: #607994;
            font-size: 13px;
            line-height: 1.8;
            margin-bottom: 12px;
        }

        .model-badge {
            display: inline-block;
            background: #FFFFFF;
            border: 1px solid #DCEAEF;
            color: #31556F;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 700;
        }

        div[data-testid="stForm"] {
            background: #FFFFFF !important;
            border: 1px solid #DFE9F3 !important;
            border-radius: 18px !important;
            padding: 28px 32px !important;
            box-shadow: 0 6px 20px rgba(16, 43, 70, 0.04) !important;
        }

        .form-section-heading {
            color: #102B46;
            font-size: 17px;
            font-weight: 800;
            letter-spacing: -0.3px;
            margin-bottom: 4px;
        }

        .form-section-sub {
            color: #71849A;
            font-size: 12px;
            margin-bottom: 18px;
        }

        div[data-testid="stWidgetLabel"] label,
        div[data-testid="stWidgetLabel"] p {
            color: #102B46 !important;
            font-weight: 700 !important;
            font-size: 12px !important;
            margin-bottom: 5px !important;
        }

        div[data-baseweb="select"] > div {
            background-color: #FAFCFF !important;
            border: 1px solid #CFDCE8 !important;
            border-radius: 10px !important;
            color: #102B46 !important;
            min-height: 42px !important;
        }

        div[data-baseweb="select"] span {
            color: #102B46 !important;
            font-weight: 600 !important;
            font-size: 13px !important;
        }

        div[data-testid="stNumberInput"] div[data-baseweb="input"] {
            background-color: #FAFCFF !important;
            border: 1px solid #CFDCE8 !important;
            border-radius: 10px !important;
            min-height: 42px !important;
        }

        div[data-testid="stNumberInput"] input {
            color: #102B46 !important;
            font-weight: 600 !important;
            font-size: 13px !important;
        }

        div[data-baseweb="select"] > div:hover,
        div[data-testid="stNumberInput"] div[data-baseweb="input"]:hover {
            border-color: #13A89E !important;
            background-color: #FFFFFF !important;
        }

        div[data-testid="stFormSubmitButton"] button {
            background: linear-gradient(135deg, #102B46 0%, #1A436B 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 12px !important;
            min-height: 48px !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            letter-spacing: 0.5px !important;
            box-shadow: 0 4px 14px rgba(16, 43, 70, 0.18) !important;
            transition: all 0.2s ease !important;
        }

        div[data-testid="stFormSubmitButton"] button p {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }

        div[data-testid="stFormSubmitButton"] button:hover {
            background: linear-gradient(135deg, #13A89E 0%, #0F8B82 100%) !important;
            box-shadow: 0 6px 20px rgba(19, 168, 158, 0.3) !important;
            transform: translateY(-1px) !important;
        }

        .result-card-container {
            background: linear-gradient(145deg, #FFFFFF, #F8FCFF);
            border: 1px solid #DCEAEF;
            border-radius: 18px;
            padding: 24px 28px;
            box-shadow: 0 8px 25px rgba(16, 43, 70, 0.06);
            margin-top: 20px;
        }

        .result-eyebrow {
            color: #13A89E;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1.4px;
            text-transform: uppercase;
            margin-bottom: 6px;
        }

        .result-badge-value {
            display: inline-block;
            color: #102B46;
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin-bottom: 8px;
        }

        .result-description-text {
            color: #607994;
            font-size: 12px;
            line-height: 1.7;
        }

        .info-note-box {
            background: #EBF5FC;
            border: 1px solid #D4E8F5;
            border-radius: 12px;
            padding: 14px 18px;
            color: #59758D;
            font-size: 11px;
            line-height: 1.8;
            margin-top: 22px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# DATASET & MODEL FUNCTIONS
# =========================================================
@st.cache_data(show_spinner=False)
def load_dataset():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE.name}")

    df = pd.read_csv(DATA_FILE)

    required = [
        "Age",
        "Gender",
        "Blood Type",
        "Medical Condition",
        "Hospital",
        "Insurance Provider",
    ]

    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError("Missing dataset columns: " + ", ".join(missing))

    return df


@st.cache_resource(show_spinner=False)
def load_model_artifact():
    model_path = next((p for p in MODEL_FILES if p.exists()), None)

    if model_path is None:
        raise FileNotFoundError("Model file not found.")

    artifact = joblib.load(model_path)

    if isinstance(artifact, dict):
        model = None

        for key in (
            "model",
            "estimator",
            "classifier",
            "rf_model",
            "best_model",
        ):
            candidate = artifact.get(key)

            if candidate is not None and hasattr(candidate, "predict"):
                model = candidate
                break

        if model is None and hasattr(artifact, "predict"):
            model = artifact

        feature_names = None

        for key in ("feature_names", "features", "columns"):
            if artifact.get(key) is not None:
                feature_names = list(artifact[key])
                break

        categories = artifact.get("valid_categories", {})
        mapping = artifact.get("mapping", artifact.get("label_mapping", {}))

    else:
        model = artifact
        feature_names = getattr(model, "feature_names_in_", None)
        feature_names = list(feature_names) if feature_names is not None else None
        categories = {}
        mapping = {}

    if model is None or not hasattr(model, "predict"):
        raise ValueError("No usable prediction model found inside artifact.")

    if not feature_names:
        model_features = getattr(model, "feature_names_in_", None)

        if model_features is not None:
            feature_names = list(model_features)

    if not feature_names:
        raise ValueError("Training feature names are missing.")

    return {
        "model": model,
        "feature_names": feature_names,
        "valid_categories": categories or {},
        "mapping": mapping or {},
        "path": str(model_path),
    }


def get_category_options(column, df, valid_categories, fallback=None):
    values = []

    saved_values = valid_categories.get(column, [])

    if isinstance(saved_values, (list, tuple, set)):
        values.extend(list(saved_values))

    if column in df.columns:
        values.extend(df[column].dropna().unique().tolist())

    if fallback:
        values.extend(fallback)

    result = []

    for val in values:
        if pd.isna(val):
            continue

        val_str = str(val).strip()

        if val_str and val_str not in result:
            result.append(val_str)

    return result


def prepare_model_input(patient_input, feature_names):
    input_df = pd.DataFrame([patient_input])

    encoded_df = pd.get_dummies(
        input_df,
        columns=CATEGORICAL_FEATURES,
    )

    encoded_df = encoded_df.reindex(
        columns=feature_names,
        fill_value=0,
    )

    encoded_df = encoded_df.apply(
        pd.to_numeric,
        errors="coerce",
    ).fillna(0)

    return encoded_df


def decode_prediction(raw_pred, mapping, df=None):
    if mapping:
        if raw_pred in mapping:
            return str(mapping[raw_pred])

        if str(raw_pred) in mapping:
            return str(mapping[str(raw_pred)])

        try:
            if int(raw_pred) in mapping:
                return str(mapping[int(raw_pred)])
        except (ValueError, TypeError):
            pass

    if df is not None and "Admission Type" in df.columns:
        unique_types = sorted(
            df["Admission Type"].dropna().unique().tolist()
        )

        try:
            idx = int(raw_pred)

            if 0 <= idx < len(unique_types):
                return unique_types[idx]

        except (ValueError, TypeError):
            pass

    fallback_map = {
        0: "Elective",
        1: "Emergency",
        2: "Urgent",
        "0": "Elective",
        "1": "Emergency",
        "2": "Urgent",
    }

    if raw_pred in fallback_map:
        return fallback_map[raw_pred]

    if str(raw_pred) in fallback_map:
        return fallback_map[str(raw_pred)]

    return str(raw_pred)


def predict_admission_type(patient_input, df=None):
    artifact = load_model_artifact()

    model_input = prepare_model_input(
        patient_input,
        artifact["feature_names"],
    )

    prediction = artifact["model"].predict(model_input)

    if len(prediction) == 0:
        raise ValueError("Model returned an empty prediction.")

    return decode_prediction(
        prediction[0],
        artifact["mapping"],
        df=df,
    )


# =========================================================
# PATIENT PREDICTION PAGE RENDER
# =========================================================
def show_patient_prediction():
    add_prediction_styles()

    st.markdown(
        """
        <div class="prediction-hero">
            <div class="prediction-eyebrow">
                Machine Learning • Patient Analytics
            </div>
            <div class="prediction-title">
                Patient Admission Prediction
            </div>
            <div class="prediction-description">
                Enter demographic and clinical details to generate an admission-type
                prediction using the trained Random Forest classifier.
            </div>
            <span class="model-badge">
                🗂️ Model: healthcare_rf_l4.joblib
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        df = load_dataset()
        artifact = load_model_artifact()

    except Exception as error:
        st.error(f"Unable to load prediction resources: {error}")
        return

    categories = artifact["valid_categories"]

    options = {
        "Gender": get_category_options("Gender", df, categories),
        "Blood Type": get_category_options("Blood Type", df, categories),
        "Medical Condition": get_category_options(
            "Medical Condition", df, categories
        ),
        "Hospital": get_category_options("Hospital", df, categories),
        "Insurance Provider": get_category_options(
            "Insurance Provider", df, categories
        ),
        "Admission Day": get_category_options(
            "Admission Day",
            df,
            categories,
            fallback=list(calendar.day_name),
        ),
    }

    age_values = pd.to_numeric(
        df["Age"],
        errors="coerce",
    ).dropna()

    age_min = max(0, int(age_values.min()))
    age_max = int(age_values.max())
    default_age = min(max(45, age_min), age_max)

    if "Admission Year" in df.columns:
        year_values = pd.to_numeric(
            df["Admission Year"],
            errors="coerce",
        ).dropna()

        years = year_values.astype(int).unique().tolist()

    else:
        years = list(range(2019, 2026))

    years = sorted(set(int(y) for y in years))
    default_year = 2021 if 2021 in years else years[0]

    with st.form("modern_patient_prediction_form"):
        st.markdown(
            '<div class="form-section-heading">Patient Details</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="form-section-sub">'
            'Fill in the fields below to run the prediction model.'
            '</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2, gap="large")

        with col1:
            age = st.number_input(
                "Age",
                min_value=age_min,
                max_value=age_max,
                value=default_age,
                step=1,
            )

            gender = st.selectbox("Gender", options["Gender"])
            blood_type = st.selectbox("Blood Type", options["Blood Type"])

            medical_condition = st.selectbox(
                "Medical Condition",
                options["Medical Condition"],
            )

        with col2:
            hospital = st.selectbox("Hospital", options["Hospital"])

            insurance_provider = st.selectbox(
                "Insurance Provider",
                options["Insurance Provider"],
            )

            admission_year = st.selectbox(
                "Admission Year",
                years,
                index=years.index(default_year),
            )

            sub_col1, sub_col2 = st.columns(2, gap="small")

            with sub_col1:
                admission_month = st.selectbox(
                    "Admission Month",
                    list(range(1, 13)),
                    index=5,
                    format_func=lambda m: calendar.month_name[m],
                )

            with sub_col2:
                days = options["Admission Day"]

                default_day = (
                    days.index("Thursday")
                    if "Thursday" in days
                    else 0
                )

                admission_day = st.selectbox(
                    "Admission Day",
                    days,
                    index=default_day,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        submitted = st.form_submit_button(
            "✨ Predict Admission Type",
            type="primary",
            width="stretch",
        )

    if submitted:
        patient_input = {
            "Age": int(age),
            "Gender": gender,
            "Blood Type": blood_type,
            "Medical Condition": medical_condition,
            "Hospital": hospital,
            "Insurance Provider": insurance_provider,
            "Admission Year": int(admission_year),
            "Admission Month": int(admission_month),
            "Admission Day": admission_day,
        }

        try:
            with st.spinner(
                "Analyzing patient details with Random Forest model..."
            ):
                predicted_label = predict_admission_type(
                    patient_input,
                    df=df,
                )

            safe_result = html.escape(str(predicted_label))

            st.markdown(
                f"""
                <div class="result-card-container">
                    <div class="result-eyebrow">PREDICTION RESULT</div>
                    <div class="result-badge-value">
                        🏥 {safe_result}
                    </div>
                    <div class="result-description-text">
                        The machine-learning model classified this record as an
                        <strong>{safe_result}</strong> admission based on historical
                        demographic and clinical training patterns.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander("🔍 View submitted patient details"):
                summary_data = [
                    {
                        "Feature": str(key),
                        "Value": str(value),
                    }
                    for key, value in patient_input.items()
                ]

                summary_df = pd.DataFrame(summary_data)

                st.dataframe(
                    summary_df,
                    hide_index=True,
                    width="stretch",
                )

        except Exception as error:
            st.error(f"Prediction failed: {error}")

    st.markdown(
        """
        <div class="info-note-box">
            <strong>ⓘ Academic Demonstration Disclaimer:</strong>
            This dashboard uses a historical dataset. Predictions are generated
            by an experimental decision-support model and must not be used for
            live clinical decisions or hospital triage.
        </div>
        """,
        unsafe_allow_html=True,
    )
