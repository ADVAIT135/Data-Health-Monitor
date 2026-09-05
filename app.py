from __future__ import annotations

from io import BytesIO

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Data Health Monitor",
    page_icon="📊",
    layout="wide",
)


def profile_dataset(dataframe: pd.DataFrame) -> dict[str, object]:
    """Calculate the checks used by the dashboard and downloadable report."""
    total_cells = dataframe.shape[0] * dataframe.shape[1]
    missing_cells = int(dataframe.isna().sum().sum())
    duplicate_rows = int(dataframe.duplicated().sum())
    numeric_columns = dataframe.select_dtypes(include="number").columns

    outlier_cells = 0
    for column in numeric_columns:
        values = dataframe[column].dropna()
        if len(values) < 4:
            continue
        first_quartile = values.quantile(0.25)
        third_quartile = values.quantile(0.75)
        interquartile_range = third_quartile - first_quartile
        if interquartile_range == 0:
            continue
        lower_bound = first_quartile - (1.5 * interquartile_range)
        upper_bound = third_quartile + (1.5 * interquartile_range)
        outlier_cells += int(((values < lower_bound) | (values > upper_bound)).sum())

    missing_rate = missing_cells / total_cells if total_cells else 0
    duplicate_rate = duplicate_rows / len(dataframe) if len(dataframe) else 0
    outlier_rate = (
        outlier_cells / (len(dataframe) * len(numeric_columns))
        if len(dataframe) and len(numeric_columns)
        else 0
    )

    completeness_score = max(0.0, 1 - missing_rate)
    uniqueness_score = max(0.0, 1 - duplicate_rate)
    outlier_score = max(0.0, 1 - outlier_rate)
    health_score = round(
        100 * ((0.5 * completeness_score) + (0.3 * uniqueness_score) + (0.2 * outlier_score)),
        1,
    )

    return {
        "rows": len(dataframe),
        "columns": len(dataframe.columns),
        "missing_cells": missing_cells,
        "missing_rate": missing_rate,
        "duplicate_rows": duplicate_rows,
        "duplicate_rate": duplicate_rate,
        "outlier_cells": outlier_cells,
        "outlier_rate": outlier_rate,
        "numeric_columns": len(numeric_columns),
        "health_score": health_score,
    }


def build_report(dataframe: pd.DataFrame, profile: dict[str, object]) -> pd.DataFrame:
    """Return a compact, row-oriented report suitable for CSV export."""
    report = [
        ("Rows", profile["rows"]),
        ("Columns", profile["columns"]),
        ("Missing cells", profile["missing_cells"]),
        ("Missing rate", f"{profile['missing_rate']:.2%}"),
        ("Duplicate rows", profile["duplicate_rows"]),
        ("Duplicate rate", f"{profile['duplicate_rate']:.2%}"),
        ("Outlier cells", profile["outlier_cells"]),
        ("Outlier rate", f"{profile['outlier_rate']:.2%}"),
        ("Numeric columns", profile["numeric_columns"]),
        ("Health score", profile["health_score"]),
    ]
    return pd.DataFrame(report, columns=["Metric", "Value"])


st.title("📊 Data Health Monitor")
st.caption("Upload a dataset to identify quality issues before they affect your analysis.")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is None:
    st.info("Upload a CSV to begin profiling.")
    st.markdown(
        """
        **Current checks**
        - Completeness: missing cells and per-column missing rates
        - Uniqueness: duplicate rows
        - Numeric anomalies: IQR-based outlier detection
        """
    )
    st.stop()

try:
    dataframe = pd.read_csv(BytesIO(uploaded_file.getvalue()))
except (UnicodeDecodeError, pd.errors.ParserError, ValueError) as error:
    st.error(f"Could not read this CSV: {error}")
    st.stop()

if dataframe.empty or dataframe.shape[1] == 0:
    st.error("The uploaded CSV does not contain any data columns.")
    st.stop()

profile = profile_dataset(dataframe)

st.subheader(f"Health score: {profile['health_score']}/100")
st.progress(int(profile["health_score"]))

metric_columns = st.columns(4)
metric_columns[0].metric("Rows", f"{profile['rows']:,}")
metric_columns[1].metric("Columns", f"{profile['columns']:,}")
metric_columns[2].metric("Missing cells", f"{profile['missing_cells']:,}")
metric_columns[3].metric("Duplicate rows", f"{profile['duplicate_rows']:,}")

left, right = st.columns(2)
with left:
    st.subheader("Missing values by column")
    missing_by_column = (
        dataframe.isna().sum().rename("Missing values").sort_values(ascending=False)
    )
    st.bar_chart(missing_by_column)

with right:
    st.subheader("Column summary")
    summary = pd.DataFrame(
        {
            "Type": dataframe.dtypes.astype(str),
            "Missing": dataframe.isna().sum(),
            "Unique": dataframe.nunique(dropna=True),
        }
    )
    st.dataframe(summary, use_container_width=True)

st.subheader("Data preview")
st.dataframe(dataframe.head(100), use_container_width=True)

report = build_report(dataframe, profile)
st.download_button(
    "Download health report (CSV)",
    data=report.to_csv(index=False).encode("utf-8"),
    file_name="data-health-report.csv",
    mime="text/csv",
)
